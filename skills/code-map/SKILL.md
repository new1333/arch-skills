---
name: code-map
description: Use when the target project has (or needs) a code map in docs/code-map/ — consult it before any feature work and keep its entries fresh in the same change as the code — or when the user invokes init (chart an existing unmapped codebase), update (reconcile the map against git history), or status (one-line freshness report).
---

# code-map

目标项目 `docs/code-map/` 下的纯 Markdown 文件层级，索引「功能在哪」。地图只指路，不描述实现——单一数据源是代码。

本 skill 是制图与维护工具：init 收编存量、update 对账、日常同笔保鲜。查询零仪式——写进目标项目 AGENTS.md 的硬门槛段自足生效（模板：[references/hard-gate-section.md](references/hard-gate-section.md)）。

## Scope

地图管「在哪」；术语含义归 GLOSSARY.md、决策原因归 docs/adr、项目规矩归 AGENTS.md。维护地图时，术语定义与决策原因一律不进地图：名字承载值得定义的含义、或条目揭示一处取舍时，在输出中提示分流 `/domain-modeling`，由人落地。

## 查询：三层下钻

1. `INDEX.md` — 每模块一行（名 + 一句话 + 路由前缀），选模块。
2. `<module>.md` — 找功能条目；`files` / `symbols` 直指实现。
3. 需要实现细节才打开代码文件。

读图零仪式。开文件 404、grep symbols 不中 = 撞见**谎报**：代码为准，同笔只修事实字段，条目存废与归属进报告。代码有、图无 = **覆盖缺口**：只报告，不代判。处置细节：[references/maintenance.md](references/maintenance.md) 处置表。

## 开发纪律：动功能时的地图规矩

1. 新增或修改功能前，必走上面的三步查询。命中 → 原地复用、扩展。
2. 未命中 → 先按文件名 / 导出符号全局搜索，确认不存在才当新功能做，同笔补条目。
3. 地图与代码冲突 → 代码为准，同笔修图。

登记时序：**码先图后、同笔提交**。新模块先定名（定名 ≠ 建条目，随时可做）→ 写码 → 验证可用 → 同一提交建模块文件 + INDEX 行。先图后码必撒谎：条目指向尚不存在的文件即谎报。

条目 / 模块文件 / Coverage 的格式：[references/map-format.md](references/map-format.md)。自己动过的代码，其条目同笔新鲜，Coverage 顺手记档位、不虚抬。

## init：收编无图存量代码

项目有存量代码而无 `docs/code-map/` 时跑；绿地空仓库不预跑——靠开发纪律自然长图，硬门槛段在首次 agent 接触时写入。全自动零停顿，四阶段与全部细节：[references/init.md](references/init.md)。

## update 与 status

**status**：只读探测器，一行「N/M 模块 stale、落后 X commits」，零写入。

**update**：显式对账刷新。触发：全图 verified 落后明显（>50 commits / >2 周）、大重构合并后、人喊。跑完全图对新 HEAD 为真。四查默认机械化（`scripts/check-map.py`）。update 细节与四查用法：[references/maintenance.md](references/maintenance.md)。
