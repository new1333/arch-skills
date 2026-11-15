# arch-skills

面向 AI agent 的工程 skills 孵化仓。当前 skill：**code-map**。

## code-map 是什么

给 AI agent 的代码库结构导航地图。在目标项目 `docs/code-map/` 下生成纯 Markdown 文件层级，索引「功能在哪」：`INDEX.md`（模块层）→ `<module>.md`（功能条目）→ 代码本身，三层渐进下钻。地图只指路、不描述实现——单一数据源是代码。

- **init** — 收编无图存量代码，四阶段指令式成图
- **update / status** — 按新鲜度头对账刷新 / 一行新鲜度报告
- **开发纪律** — 动功能前必查地图、码先图后同笔提交；写进目标项目 AGENTS.md 的硬门槛段自足生效，不装 skill 的 agent 也能走图

## 安装

走 [npx skills](https://www.npmjs.com/package/skills) 安装器：

```sh
npx skills add new1333/arch-skills
```

装进 `~/.agents/skills/code-map/`。日后检查与更新：`npx skills check` / `npx skills update`。
