# arch-skills

本仓库孵化面向 agent 的工程 skills。当前 effort：`code-map` skill——给 AI agent 的代码库结构导航地图。

## Language

### code-map 域

**代码地图（code map）**:
目标项目 `docs/code-map/` 下的纯 Markdown 文件层级，索引「功能在哪」，供 agent 渐进式下钻导航。
_Avoid_: repo map、架构文档、目录树打印。

**模块（module / 功能域）**:
地图里横切技术分层（pages/components/composables/stores/server）的功能域分组；只是地图分组，代码目录不动。
_Avoid_: 把技术分层（components 层、stores 层）当作模块。

**shared 模块**:
收纳不属于任何功能域的横切基础设施（基础 UI、搜索基建、应用基建）的模块。

**功能条目（feature entry）**:
模块文件里的一条：一个可独立指认的能力，其字段指向实现它的代码文件，不描述实现。

**INDEX.md**:
地图唯一入口（模块层），每模块一行；会话常驻成本所在，须守住 token 预算。

**Coverage 块（coverage block）**:
模块文件头部的置信度统计：文件清单核对数、抽读确认条目数、未读条目与未覆盖区名单、待定归属记录。地图诚实度的载体。
_Avoid_: 条目级 ⚠️ 散标（无人擦拭会永久悬挂）；视作可省略的实现细节——它是地图结构的一部分。

**谎报（lie）**:
功能条目里与代码不符的事实性字段：指向的文件路径不存在、symbols 非该文件实际导出、目录计数失实。机械可定、发现即修（以代码为准）；干活时只修事实性字段，条目存废与归属进报告。
_Avoid_: 与覆盖缺口混用；挂条目级 stale 标记代替修正（散标无人擦拭）。

**覆盖缺口（coverage gap）**:
代码库已存在而地图未收录的实现：未映射的新文件、目录计数漂移多出的部分。补齐需功能归属判断，只报告交 update 流程或人，不代判、不顺手补。
_Avoid_: 当作谎报机械修；把 agent 新建功能走的硬门槛「顺手补条目」算进缺口处置。

**核查器（checker）**:
skill 自带的 scripts/ 四查脚本：对账地图事实字段 vs 代码，只产发现清单（MISS/BAD/DRIFT），零修改零生成；裁决与修图归 agent 按处置表。凡四查处皆可用（update 深查、init 自校验）；paths/counts/links 格式驱动栈无关，symbols 挂栈检测表（v1 只装 Nuxt/TS，未识别栈仅该查降级跳过）。脚本为默认路径，指令式清单是 fallback 与四查的定义文本。
_Avoid_: 与扫描器混用；让核查器写地图（它是证据生成器，不是修图者）；栈不支持时整脚本拒绝服务（只降级 symbols 一查）。

**扫描器（scanner）**:
代判断成图的可执行生成器（python/ts 扫描器）：聚类定模块、生成条目内容——init 的判断价值所在，已划出 scope，init 保持指令式。
_Avoid_: 与核查器混用——边界在「替 agent 生成地图内容」，不在「skill 里有没有脚本」。

**硬门槛段（hard-gate section）**:
init 写进目标项目 AGENTS.md/CLAUDE.md 的自足段：动功能前必走代码地图、复用已映射实现、未命中先全局搜索再新建并补条目、地图与代码冲突以代码为准并顺手修图。
_Avoid_: 视作 code-map skill 的一部分（它自足生效，无需安装 skill）；与地图本体（`docs/code-map/`）混淆。

**分诊规则（triage rules）**:
code-map SKILL.md 里的短段（Scope）：地图管「在哪」；术语含义归 GLOSSARY.md、决策原因归 docs/adr、项目规矩归 AGENTS.md。维护地图时术语定义与决策原因一律不进地图，在输出中提示分流。
_Avoid_: 把术语定义写进功能条目；init 代写 GLOSSARY/ADR（线索只进 init 报告，由人跑 /domain-modeling 落地）。

**同笔（same-commit）**:
地图变更与引发它的代码变更落在同一提交里；agent 动过的代码，其条目同笔补齐或修正。条目是功能的出生证明，不是孕检报告——图必须后于码，先图必撒谎（条目指向不存在的文件即谎报）。
_Avoid_: 先建条目再写码；地图变更攒批延后提交。

**新鲜度头（verified 行）**:
模块文件 Coverage 块内的 `verified: <short-sha>` 行（INDEX.md 另记全图值）：上次对账四查时的 HEAD。过期机械可判：模块 scope 内 `git diff <sha>..HEAD` 非空即 stale。用 commit 不用日期——日期会谎报「查过」，commit 是证据。
_Avoid_: 日期戳；条目级时间标记。

**update（对账刷新）**:
显式维护指令：按新鲜度头把模块分成 touched/untouched——touched 深查四查、轻量重复实现扫描（只报告）、重算 Coverage 块、推进 verified；untouched 的 diff 为空即免检推头。跑完全图对新 HEAD 为真。
_Avoid_: 每次全量重扫（贵到没人跑，恰与防腐烂相反）；对职责散文做语义审读（那归干活的 agent 机会性同笔修）。

**status（新鲜度报告）**:
只读探测器：读各模块新鲜度头 + git diff 计数，输出一行「N/M 模块 stale、落后 X commits」，零写入。
_Avoid_: 当作 update 的别名——status 只看，update 才修。
