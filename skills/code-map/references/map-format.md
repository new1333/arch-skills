# 地图文件格式

地图 = 目标项目 `docs/code-map/` 下的纯 Markdown 文件层级。两层地图文件 + 代码当第三层，目录结构本身即三层下钻；不用任何结构化数据文件。

## INDEX.md（模块层，唯一入口）

- 每模块一行，仅三样：模块名（链接）+ 一句话职责 + 路由前缀（嵌入式模块写「（嵌入式）」，redirect 前缀用 `→` 跟在主前缀后）。
- 头部记全图 `verified: <short-sha>`（格式见下方 Coverage）。
- **≤1k tokens 守门**（字节近似实测）——INDEX 是每 session 的常驻成本。

行样例：

```markdown
- [sources](sources.md) — 期刊/数据源检索、详情、引用指标 I3 · /sources, /journals→
- [analytics](analytics.md) — 详情页图表与分析（跨实体，嵌入各详情页）· （嵌入式）
```

## `<module>.md`（功能层）

文件名 = 模块名 kebab-case。骨架：

````markdown
# <module> — 一句话职责
alias: <落选异名 / legacy 名>（存在才写）

> coverage: 清单核对 N/N · 抽读确认 x/y · verified: <short-sha>
> 未读代表作: <条目名单> · 未覆盖区: <连条目都没有的角落> · 待定归属: <条目 → 倾向>

### <功能名> (route: /xxx)
一句话职责（用术语，不定义术语）。
files:
- <域自有文件或目录 /** +计数>
symbols: <实际导出名>
uses: [<module>](<module>.md)（依赖说明）
````

## 功能条目字段

必填：

- **功能名**：英文短语，与代码词汇同源、可 grep。
- **一句话职责**：中文；只许来自读过的代码。
- **files**：只列**域自有**文件——共享物不列，走 `uses`。粒度：目录级 `/**` + 计数优先；平铺层（stores / utils）列单文件。同一行逗号并列可省略重复目录前缀（速记，含裸组件名/家族目录）；核查器按解析阶梯核对存在性（见 maintenance.md「机械化」）。
- **uses**：依赖的模块 / 条目。

条件必填：

- **symbols**：shared 条目必填；域内有可复用导出时填。**写实际导出名，不写文件名**（`stores/api-solr.ts` → `useSolrApi`）——这是防重复实现的钥匙。
- **alias**：存在异名（legacy 名、redirect、口语名）必填，服务定位。

禁止：行号、签名全文、实现散文、import 图、代码片段。地图只指路，实现细节以代码为准。

## 模块

模块 = 功能域，横切 pages / components / composables / stores / server 技术分层；只是地图分组，代码目录不动。单层域（只含一个 page 的域）也算模块；横切基建进 `shared-*` 模块。

## 命名

模块文件名 = 规范域名 kebab-case，取**代码主流拼写**（`top-cited-scholars` 而非 `top-scholars`）；落选异名进模块 `alias`。功能名英文、职责中文。

## Coverage 块与新鲜度头

模块文件头部的置信度统计（见上方骨架模板），地图诚实度的载体：

- **清单核对 N/N**：`files` 列表对 `git ls-files` 已核对的条目数。
- **抽读确认 x/y**：职责来自读过代码的条目数。
- **未读代表作 / 未覆盖区 / 待定归属**：低置信名单，待 update 或人消化。
- **verified: `<short-sha>`**：上次四查时的 HEAD。过期机械可判：模块 scope 内 `git diff <sha>..HEAD` 非空，或 `git status --porcelain` 有未提交改动。用 commit 不用日期——日期会谎报「查过」，commit 是证据。
