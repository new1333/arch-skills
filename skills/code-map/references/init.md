# init：收编无图存量代码

前提：项目有存量代码、无 `docs/code-map/`（绿地空仓库不预跑 init，见 SKILL.md 开发纪律）。

默认全自动、一口气跑完。唯一例外：用户明确要求询问（如「init 时问我」）→ 在阶段 1 候选模块清单成形后停一次，其余阶段不停。例外是用户口头给的，流程不内置停顿。

## 阶段 0：结构侦察（零读码）

- `git ls-files` + 各技术分层（pages / components / composables / stores / server）目录与文件名 → 候选模块清单，含跨层文件簇（同前缀的 page + composable + store + api 目录）。
- 清单落盘 `docs/code-map/.init-workspace.md`（断点续跑的工作台，init 完成时删除）。
- 既有 CLAUDE.md / README 只作聚类先验与业务词汇来源；条目内容一字不搬——未经理码核实的描述是从别处抄来的谎。

## 阶段 1：定模块

三锚交集归纳功能域：

- **主锚**：pages 路由前缀 × components 顶层目录 × server/api 子目录。
- **归入**：composables / stores 文件名前缀。
- **特例**：单层域也算模块；user 相关合一（auth + profile + library + alert-center，共享 user-\* stores / api）。

锚冲突三级裁决：

1. 锚一致 → 直接归。
2. 倾向明显（前缀 / 复用方向 / 文件数一边倒）→ 归倾向侧 + Coverage 记「待定归属」。
3. 无法判断 → 归 shared + 记待定。

原则：宁可归错加标注，不可停下来等。待定项全进最终报告，事后改图走维护流程。

## 阶段 2：逐模块成图

- `files` 直接用阶段 0 清单，不再扫盘。
- 职责一句话靠**分层读取预算**（比例感按千文件级 Nuxt 项目标定，更小项目按比例收缩）：
  - pages / stores / utils：全读。
  - server/api：目录名 + 每目录代表 1 文件。
  - composables：文件名全扫 + 每域 ≤3 抽读。
  - components：目录名 + 每域 1–2 抽读。
- 铁律：职责只允许来自读过的代码；读不到 → 低置信，进 Coverage 块。
- 逐模块处理、完成即写盘；单模块抽读代表作 ≤5 文件，控制 token 峰值（session 大小不一，不写死绝对数字）。
- 条目与 Coverage 格式：[map-format.md](map-format.md)。

## 阶段 3：自校验 + 硬门槛 + 报告

四查与 INDEX ≤1k tokens 守门默认跑本 skill 自带核查器 check-map.py；用法、输出标签与跑不了时的指令式回退见 [maintenance.md](maintenance.md)（谎报/缺口处置表同在此），发现按处置表机械修。

两项保持指令式（不进脚本）：

- 跨模块重复实现扫描 → 只报告不裁决（init 是制图员，不是法官）。
- 随机 3 个「X 在哪」下钻链路走通（INDEX → 模块 → 条目 → 代码）。

然后：

- 写入硬门槛段：按 [hard-gate-section.md](hard-gate-section.md) 的规则与模板，纯追加，收尾展示写入内容。
- 总结报告（最终交付）：
  - 模块清单
  - 待定归属
  - 重复实现候选
  - 未覆盖区
  - 合并指引：既有 AGENTS.md / CLAUDE.md 里的导航形重叠（Key stores 类列表）建议瘦身为指向地图的指针——只报告，不改写
  - 分流线索：术语候选 + 决策候选，各带代码出处——交人跑 `/domain-modeling` 落地，不代写 GLOSSARY / ADR，不落持久文件
- 删除 `.init-workspace.md`。

## 断点续跑

已存在的 `<module>.md` 即进度标记：重跑 → 跳过已有模块（Coverage 自校验不过的除外）→ 从 workspace 清单继续补缺。

## 完成判据

四查全绿 + INDEX ≤1k tokens + 硬门槛段已写入 + 总结报告交付。没有硬门槛段的 init 是没上锁的门。
