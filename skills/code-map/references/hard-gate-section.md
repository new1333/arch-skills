# 硬门槛段（hard-gate section）

写给任何读到目标项目 AGENTS.md / CLAUDE.md 的 agent：自足、纯导航，不提本 skill、不假设安装。门槛是仓库纪律，skill 只是维护工具。

## 写入规则（init 收尾执行；绿地项目首次 agent 接触时执行）

- **目标文件**：有 AGENTS.md 追加至 AGENTS.md（两者都有只写它）；只有 CLAUDE.md 追加至 CLAUDE.md；皆无 → 新建 AGENTS.md（本模板 + 一行文件用途说明；语言取仓库 README 主导语言，无则英文）。
- **位置**：紧跟标题 / Overview 的第一个正文章节（顶部注意力最高，此段每 session 加载）。
- **语言**：匹配目标文件既有语言（下方英文模板按需转写，语义不变）。
- **纯追加**：一字不动既有内容。检测到的导航形重叠（如 Key stores / Key composables 列表）只进 init 报告的合并指引清单，由人决定是否瘦身为指向地图的指针。
- **预算**：~10 行 / ~120 tokens 量级。
- **措辞**：正向（Reuse / extend），统一 leading word "code map"。

## 模板

以下 fenced block 的内容即要追加的原文：

```markdown
# Code map

`docs/code-map/` indexes what lives where. Before adding or changing
any feature, walk it:

1. `docs/code-map/INDEX.md` — pick the module.
2. `<module>.md` — find the feature entry; its `files`/`symbols`
   point at the implementation.
3. Open those files only when you need implementation detail.

- Reuse mapped features: extend them where they live.
- Nothing in the map? Search file names and exported symbols before
  building it new; add its entry to the module file in the same change.
- Map disagrees with code? Code wins; fix the entry in the same change.
```
