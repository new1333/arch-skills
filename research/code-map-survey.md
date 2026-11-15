# 业界方案与惯例调研：agent 代码地图（code map）

Ticket: [#6](https://github.com/new1333/arch-skills/issues/6) · 2026-11-13
目的：为「代码地图 skill」的**文件布局**与 **init 流程**设计票提供事实输入。

范围声明：本机 `writing-for-agents` skill（`C:\Users\deare\.agents\skills\writing-for-agents\`）已覆盖写作原理（context pointer、两种负载、信息层级、progressive disclosure 作为写作概念、co-location、completion criterion、leading words、pruning、model/user-invocation 的取舍）。本文**只补它没覆盖的**：官方格式规格与硬性数字、渐进式披露在客户端的实际加载机制、社区 code-map 实践、索引工具对比、token 经济学实证。除注明外所有结论均溯源自一手来源（官方文档/规格/工程博客、工具官方文档与仓库、论文原文）。

---

## 1. Anthropic Agent Skills 官方惯例（writing-for-agents 未覆盖的部分）

### 1.1 格式规格（agentskills.io 开放标准，源头为 Anthropic）

Skill = 一个目录，至少含 `SKILL.md`。标准目录约定：

```
skill-name/
├── SKILL.md          # 必需：metadata + 指令
├── scripts/          # 可选：可执行代码
├── references/       # 可选：按需加载的文档
└── assets/           # 可选：模板、静态资源
```

Frontmatter 字段的硬性约束（规格原文）：

| 字段 | 必需 | 约束 |
|---|---|---|
| `name` | 是 | 最长 **64 字符**；仅小写字母/数字/连字符；不得首尾连字符、不得连续 `--`；**必须与父目录名一致** |
| `description` | 是 | 最长 **1024 字符**；须写「做什么 + 何时用」 |
| `license` | 否 | 许可证名或指向打包的 license 文件 |
| `compatibility` | 否 | 最长 **500 字符**；环境要求（目标产品、系统依赖、网络） |
| `metadata` | 否 | 任意 string→string 键值对，供自家工具用 |
| `allowed-tools` | 否 | 空格分隔的预批准工具列表（实验性） |

正文（body）无格式限制；推荐内容：分步指令、输入输出示例、边界情况。规格明确建议：**文件引用保持一层深**（从 SKILL.md 直达，避免嵌套引用链）。
来源：[Agent Skills Specification](https://agentskills.io/specification)

### 1.2 渐进式披露的官方三级模型与数字

标准定义三级加载（[agentskills.io](https://agentskills.io)）：

1. **Discovery**：启动时只把每个 skill 的 `name` + `description` 载入 system prompt —— 官方给的量级是 **metadata ≈ 100 tokens/skill**；
2. **Activation**：任务命中 description 时才读入整个 SKILL.md 正文 —— 官方建议 **正文 < 5000 tokens、SKILL.md < 500 行**；
3. **Execution**：`scripts/`、`references/`、`assets/` 里的文件**按需**加载或执行，不进默认上下文。

Anthropic 工程博客把这称为「核心设计原则」：类比一本有目录、章节、附录的手册，信息按需载入；因此「skill 可打包的上下文实际上无上限」。同一篇还给出两条对我们有用的结构建议：**把互斥的内容拆成独立路径**（只在部分任务用到的材料不要常驻），以及**明确区分「给机器执行的代码」与「给模型读的参考」**。来源：[Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 1.3 Claude Code 客户端的加载机制（比标准更具体的数字）

来自官方 Claude Code skills 文档（[code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)）：

- 空闲态只有各 skill 的 description 在上下文里（`disable-model-invocation: true` 可彻底移出）；
- 被调用后**整个渲染后的正文作为一条消息进入对话并跨轮常驻**，Claude Code 之后不会重读该文件——所以正文长就是永久负担；
- **压缩（compaction）时每个 skill 最多保留最近一次调用的前 5,000 tokens，所有 skill 共享 25,000 tokens 的合并预算**，按最新优先填充；
- 支持文件被引用才加载；脚本是执行而非载入（「长参考材料在需要前几乎零成本」）；
- 列表中 description + `when_to_use` 合计在 **1,536 字符**处截断——description 的触发词必须前置；
- Claude Code 专属 frontmatter（标准之外的扩展）：`when_to_use`、`argument-hint`、`disable-model-invocation`、`user-invocable`、`allowed-tools`、`context: fork`（子代理中运行）、`paths`（glob 限定自动激活范围）、`metadata` 等；
- 官方评估方法：开/关 skill 各跑一轮新会话对比；`/skill-doctor` 报告每个 skill 的上下文成本。

### 1.4 对本项目的含义

- 地图 skill 的 `description` 是唯一常驻成本（≈100 tokens 量级），必须把触发场景（进入陌生仓库、找东西、导航）写进这一句；
- 地图本体应放 `references/`（按需读取）而非 SKILL.md 正文（调用即常驻）；
- 若生成地图的脚本较重（tree-sitter 依赖），官方惯例是放 `scripts/` 里执行、绝不载入上下文。

---

## 2. 已有的「代码地图」实践

### 2.1 Aider repo map（先例，非 skill）

- 机制：tree-sitter 解析出定义/引用 → 文件为节点、依赖为边构图 → **图排序（PageRank 类）**选出最重要符号 → 二分搜索把尽可能多的条目装进 token 预算。地图含类/函数签名等「关键定义行」。
- **预算：`--map-tokens` 默认 1k tokens**；无文件加入对话时地图会显著扩大；地图随每个请求重发（因此大小即成本）。大仓库的全量地图本身可能超出上下文窗口，所以才需要排序+预算。
- 演进史对我们最有价值：aider 2023-10 之前用 **ctags**，之后换 tree-sitter，官方理由：① 地图更丰富（含完整函数签名）；② 语言支持可 pip 安装、免去用户手装 universal-ctags；③ 为后续能力铺路。
- 来源：[aider repomap 文档](https://aider.chat/docs/repomap.html)、[Building a better repository map with tree-sitter](https://aider.chat/2023/10/22/repomap.html)

### 2.2 社区 code-map / repo-map skills（claude-code 生态）

实取样例（均为 GitHub 上的 SKILL.md 原文，一手）：

**(a) pm-claude-skills/repo-map —— 确定性轻量地图 + 导航纪律**
- 零依赖 stdlib Python 脚本：目录树 + 每文件行数 + 正则提取的顶层符号（刻意「谦逊」：只要名字，不做语义）；
- 卖点是纪律而非工具：*read the map first, open only the files whose names and symbols match the task*；
- 自带经济学输出：**典型地图成本 ≈ 读全部文件的 3%**；
- 设计细节值得抄：输出确定性排序（字节稳定，**不破坏 provider prefix cache**）、大仓库按子目录分幅（`--max-files` 防地图自我膨胀）、明确诚实边界（正则符号做不了调用图，grep 收尾）。
- 来源：[skills/repo-map/SKILL.md](https://github.com/mohitagw15856/pm-claude-skills/blob/main/skills/repo-map/SKILL.md)

**(b) Tomatio13/repo-map-skill —— tree-sitter+PageRank + 持久化状态生命周期**
- 脚本复刻 aider 路线（tree-sitter + PageRank 排序），但把地图持久化为仓库内状态：`.repomap/state.json` + `.repomap/latest_map.txt`；
- **命令面就是一整套生命周期：`init`（首次生成）/ `update`（刷新）/ `status`（查缺失或过期）/ `view --top-files N`（只看头部）**——过期判断基于 git 状态变化；
- frontmatter 用了标准字段：`license: MIT`、`compatibility: python 3.10+, ~20MB pip deps`、`allowed-tools: bash`；
- 明确写了 Do-Not-Use（已知下一文件、直接文本搜索就能回答、仓库小到列目录更便宜时不用）。
- 来源：[Tomatio13/repo-map-skill/SKILL.md](https://github.com/Tomatio13/repo-map-skill/blob/main/SKILL.md)

**(c) savia/agent-code-map（.acm 格式）—— 分层地图 + 索引入口 + 新鲜度哈希**
- agent 手写的分层 Markdown 地图（`.acm`）：每个实体/模块一条（类型、文件:行号、一句话目的、关键依赖、公开 API），支持 `@include domain/entities.acm` **按需下钻**；
- **`INDEX.acm` 作为唯一入口**：会话开始只读索引，按层加载需要的部分；
- 头部带 `> hash: sha256:... | generated: 日期 | lines: N` 的新鲜度标记；`refresh-agent-maps.sh` 只原子重写头部日期，不动正文；hash 与生成是 agent 的手动程序。
- 这是最接近「布局 + init」问题的完整设计：入口索引 / 分层 include / 头部哈希防陈旧 / 廉价刷新。
- 来源：[savia .claude/skills/agent-code-map/SKILL.md](https://github.com/gonzalezpazmonica/savia/blob/main/.claude/skills/agent-code-map/SKILL.md)

**(d) 其他样例（编目，未逐个实取）**：majiayu000/claude-skill-registry 的 repo-map（带 `--depth` / `--focus=<module>` 参数，见 [skillsdirectory 条目](https://www.skillsdirectory.com/skills/majiayu000-repo-map)）；oaustegard 的 mapping-codebases（触发词 "map this codebase"）；nodays-off 的 code-map（**并行子代理分别测绘 API 路由 / 数据库 schema / 前端路由 / 组件**，见 [LobeHub 条目](https://lobehub.com/ru/skills/nodays-off-skills-code-map)）；Graphify（tree-sitter 全图版本，pm repo-map 自述以其为「完整版」）。

### 2.3 索引工具对比：ctags / repomix / Sourcegraph

| 方案 | 长处 | 短板 |
|---|---|---|
| **universal-ctags** | 成熟、快、语言广、纯本地符号索引 | 只有符号名无签名/结构；需系统级安装（aider 弃用的主因之一）；输出面向编辑器而非 LLM token 预算 |
| **repomix**（[repo](https://github.com/yamadashy/repomix)，29.3k stars） | 打包整仓为单文件、逐文件 token 计数、`--split-output` 分卷、`--token-budget` CI 守门、MCP 模式支持部分行读取；tree-sitter 压缩号称 **~70% token 缩减**（官方标注实验性） | 全量注入路线：上下文成本随仓库线性涨，必然撞 context rot；适合一次性喂给 LLM 分析/评审，不适合做常驻导航层 |
| **Sourcegraph / Cody**（[lessons 博客](https://sourcegraph.com/blog/lessons-from-building-ai-coding-assistants-context-retrieval-and-evaluation)、[how-cody-understands](https://sourcegraph.com/blog/how-cody-understands-your-codebase)） | 多检索器并行（Zoekt 关键词/BM25 + 语义 + 依赖图 + 编辑器局部上下文）→ encoder 重排序，**在 token 预算内解背包问题**；工程教训：曾以 embeddings 为主，因「代码须送第三方、运维复杂、>10 万仓库规模难扩展」而**降级为辅助，主力换回关键词/BM25 + 局部上下文** | 重基建（自有检索栈/服务），个人 skill 无法照搬；但其「多检索器 + 预算内重排序」与「局部上下文优先」结论可缩样借鉴 |
| **aider repo map**（2.1） | 图排序自动适配预算，1k token 常驻 | 每请求重发；语义薄（签名级）；非 skill 形态 |

---

## 3. Token 经济学：分层索引 vs 全量注入

### 3.1 全量注入会衰减：context rot 的实证

- **Chroma《Context Rot》**（18 个模型、8 种长度、11 个针位、**194,480 次 LLM 调用**）：输入变长时即使平凡任务性能也下降；**单个干扰项即降低性能，四个干扰项复合衰减**；GPT 系幻觉率最高，Claude 系最低（倾向弃答）。最有分量的对照：LongMemEval 上，**聚焦版提示（~300 tokens）得分全面显著高于全量版（~113k tokens）——瓶颈是「在无关上下文里做检索」，不是推理能力**。结论：宁可检索出相关的小上下文，也不要整段历史塞进提示。来源：[research.trychroma.com/context-rot](https://www.trychroma.com/research/context-rot)
- **Lost in the Middle**（Liu et al. 2023，[arXiv:2307.03172](https://arxiv.org/abs/2307.03172)）：相关信息位于长上下文**中部**时性能显著低于首/尾（U 型曲线），模型专为长上下文设计也如此——地图应放在会话顶部而非中部，且长文档中部内容最易被忽略。
- **Anthropic 官方**（[Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)，2025-09）：自注意力 n² 关系导致「注意力预算」摊薄，性能是「梯度下降而非悬崖」；指导原则为 **"find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome"**；趋势从「预取全量」转向 **just-in-time 检索：上下文里只留轻量标识符（文件路径、存储查询、链接），运行时按需取**；Claude Code 自身即混合策略（CLAUDE.md 常驻 + glob/grep 按需）；子代理可烧数万 token 探索但**只回传 1,000–2,000 token 的蒸馏摘要**，在复杂研究任务上显著优于单代理。

### 3.2 分层索引的实测/经验数字汇总

| 数字 | 含义 | 来源 |
|---|---|---|
| ~100 tokens/skill | 常驻成本（metadata 级） | agentskills.io 规格 |
| < 5,000 tokens / < 500 行 | SKILL.md 正文建议上限 | agentskills.io 规格 + Claude Code 文档 |
| 5k tokens/skill、25k 合计 | Claude Code 压缩时对 skill 内容的保留预算 | Claude Code 官方文档 |
| 1,536 字符 | description+when_to_use 截断点 | Claude Code 官方文档 |
| 1k tokens（默认，可调） | aider 地图预算，图排序自动装填 | aider 官方文档 |
| ≈ 3% | 「读地图 vs 读全部」典型成本比（正则符号地图自测） | pm-claude-skills/repo-map |
| ~70% | repomix tree-sitter 压缩的 token 缩减（实验性） | repomix README |
| ~300 vs ~113k tokens | LongMemEval 聚焦版 vs 全量版输入规模，聚焦版全面更高 | Chroma context rot |
| 1,000–2,000 tokens | 子代理回传摘要规模 | Anthropic 工程博客 |
| 50 万 bytes | repomix 默认单文件大小上限（超大文件跳过） | repomix README |

**合成结论**：分层索引（常驻 ≈100 token 索引层 + 按需下钻）在所有证据方向上都优于全量注入：全量注入既撞 context rot 的检索衰减（Chroma、Lost in the Middle），又线性增加每轮成本（aider「地图随每请求重发」的教训）；而索引层的边际成本几乎为零（技能规格、Claude Code 压缩预算都在鼓励这个结构）。唯一例外是 repomix 式**一次性**全量打包——用于「整体评审/一次性理解」场景合理，用于常驻导航不合理。

---

## 4. 对 arch-skills 布局 / init 设计票最有用的发现

1. **布局**：官方三级披露天然支持「地图分层」——SKILL.md 只放流程（<500 行、<5k tokens），地图本体放 `references/`（按需读），生成脚本放 `scripts/`（执行不载入）；文件引用保持一层深。savia 的 `INDEX.acm` 入口 + `@include` 下钻是这个结构的一个可直接抄的实例。
2. **init 流程**：Tomatio13 的 `init / update / status / view` 生命周期 + git 状态判过期，几乎就是 init 票要设计的接口面；savia 的「头部 hash/date + 只重写头部的廉价刷新」解决了地图陈旧问题而不用全量重生成。
3. **经济性**：地图生成成本应向 aider 的 1k-token 预算和 pm repo-map 的 ~3% 比看齐，并且输出确定性排序以保住 prefix cache；导航靠「地图出候选清单 → grep/Read 收尾」的两段式，不要试图在地图里做调用图。
4. **描述即触发**：description（≤1024 字符，Claude Code 列表在 1,536 截断）是唯一常驻成本，触发词必须前置——这与本机 writing-for-agents 的 pointer 规则一致，官方数字补足了预算。

## 5. 来源清单（一手优先）

- [Agent Skills Specification](https://agentskills.io/specification) · [Agent Skills Overview](https://agentskills.io)（开放标准，Anthropic 源头）
- [Claude Code Skills 官方文档](https://code.claude.com/docs/en/skills)
- [Equipping agents for the real world with Agent Skills（Anthropic Engineering, 2025-10）](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Effective context engineering for AI agents（Anthropic, 2025-09）](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)
- [aider: Repository map 文档](https://aider.chat/docs/repomap.html) · [Building a better repository map with tree-sitter（2023-10）](https://aider.chat/2023/10/22/repomap.html)
- [repomix README](https://github.com/yamadashy/repomix)
- [Sourcegraph: Lessons from building AI coding assistants](https://sourcegraph.com/blog/lessons-from-building-ai-coding-assistants-context-retrieval-and-evaluation) · [How Cody understands your codebase](https://sourcegraph.com/blog/how-cody-understands-your-codebase)
- [Chroma: Context Rot](https://www.trychroma.com/research/context-rot)
- [Lost in the Middle（arXiv:2307.03172）](https://arxiv.org/abs/2307.03172)
- 社区 skill 原文：[pm-claude-skills/repo-map](https://github.com/mohitagw15856/pm-claude-skills/blob/main/skills/repo-map/SKILL.md) · [Tomatio13/repo-map-skill](https://github.com/Tomatio13/repo-map-skill/blob/main/SKILL.md) · [savia/agent-code-map](https://github.com/gonzalezpazmonica/savia/blob/main/.claude/skills/agent-code-map/SKILL.md)
