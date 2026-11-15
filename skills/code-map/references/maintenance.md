# 维护：status、update 与四查

## status：只读探测器

读各模块 Coverage 的 `verified` 行，`git diff --name-only <sha> HEAD -- <模块scope>` 计数（`git status --porcelain` 捕未提交改动）→ 输出一行：「N/M 模块 stale、落后 X commits」。零写入。

## update：对账刷新

按新鲜度头分模块：

- **touched**（模块 scope 内 diff 非空）：深查四查（默认整图跑一遍 check-map.py——秒级，发现按模块认领）+ 轻量重复实现扫描 + 重算 Coverage + 推进 verified。
- **untouched**：diff 为空 = 四查恒真，verified 直接推新 HEAD。

保证：跑完 update 后全图对新 HEAD 为真。

**重复实现扫描**（只对 touched 模块的新增/变更条目）：symbols / 文件名 grep 全图（INDEX + 各模块条目）找同功能候选 → 只报告。四查管「图 vs 码」，dup 扫描管「码 vs 码」——硬门槛被跳过的最典型后果（功能被重写）只有后者能发现。保持指令式、不进 check-map.py：它产候选不产事实。

**待定归属复审**：深查 touched 模块时顺手重跑三锚裁决（代码长了几个月，倾向可能已明显）→ 明显的当场归位、清待定标记；仍不明 → 留待定、进报告。人看到报告随时拍板（= 移动条目，普通维护操作）。

update 不做语义审读——指令式 agent 跑语义审读是低置信的装忙；职责散文失实靠干活 agent 机会性同笔修。例外：touched 模块深查时允许顺手修明显失实的职责行，Coverage 不因此升档。

update 产生的纯地图变更（机械修 + 刷头）单独成 PR，review 只确认它没越界动职责归属。

## 四查清单

1. **路径存在性**：全量对 `git ls-files`（机械）。
2. **symbols 真实性**：grep `export` 行核对导出名（不上 tree-sitter）。
3. **计数漂移**：glob 重数目录 → 差额进缺口报告（缺口，不是谎报）。
4. **链接完整性**：INDEX ↔ 模块文件互链、条目 `uses` 指向的模块存在。

### 机械化：check-map.py（默认）

四查默认跑本 skill 自带的核查器（单脚本、纯 stdlib Python）：

```
python <本 skill 安装目录>/scripts/check-map.py <目标仓路径>
```

- 一次跑四查，输出 `MISS`（路径）/ `BAD`（symbols）/ `DRIFT`（计数）/ `BROKEN-LINK`（链接）发现清单 + 各查汇总，**零修改**、有发现退出码非零；`NOTE` 行是不可机械裁决的说明（如速记锚点歧义），不算发现。脚本只报——裁决与修图按「谎报与缺口：处置表」归 agent。
- 四查之外顺守 INDEX ≤1k tokens 预算（`OVER`），超标即发现。守门项不是谎报——瘦行（压缩一句话职责 / 路由前缀写法）即修；瘦不动说明模块过多，并模块是归属判断，进报告交人。
- 取值范围：条目 `files` 字段 + 全文反引号路径串。`files` 速记（逗号后省略目录前缀、裸组件名、家族目录）按解析阶梯核对存在性：全路径精确/后缀 → 组件名 → basename/stem → 目录组件——只断言「库中有相符实现物」，目录歧义交 agent。
- 「什么算导出」挂栈检测表：v1 只装 Nuxt/Vue/TS（`export const/let/var/function/class/enum`、re-export 清单、`defineStore` id、components 文件名与目录名）。未识别栈 → 仅 symbols 查跳过并在输出说明，其余三查照跑。
- 跑不了（无 Python / 非 git 仓）或栈不支持 → 落回上方指令式清单，全量降抽样（如 symbols 每模块抽 2 对 export，治「导出名 ≠ 文件名」）；INDEX 预算此时手算（字节近似：拉丁 ≈4 B/token、CJK ≈1.8 B/token，加权估算）。清单是四查的真值定义，不随脚本搬家。

## 谎报与缺口：处置表

脚本输出标签对照：MISS = 路径谎报 · BAD = symbols 谎报 · DRIFT = 计数漂移（重算即修；多出的差额同时进缺口报告） · BROKEN-LINK = 链接断裂（补链或修目标名） · OVER = INDEX token 预算超标（守门项非谎报：瘦行即修，瘦不动进报告）。

- **谎报** = 条目事实性字段与代码不符（路径不存在、symbols 非实际导出、计数失实）。机械可定，发现即修，代码为准：
  - 干活 / 读图撞见 → 同笔只修事实字段；条目存废与归属进报告。
  - 批量四查发现 → 机械修：路径试目录式（`X.vue` 不存在则试 `X/index.vue`）、symbols 从 `export` 行重取、计数重算。
- **覆盖缺口** = 代码已存在而地图未收录。只报告，交 update 或人，不代判、不顺手补（agent 新建功能走的是硬门槛「同笔补条目」，不算缺口处置）。
- 无条目级 stale 标记（散标无人擦拭会永久悬挂）；无拒绝服务（与「代码为准」直接矛盾）。地图烂透的处置是重跑 init，不是锁门。

## Coverage 升档规则

双通道：① 同笔修图时顺手记——路径修 = 已核对、读过代码修 = 已抽读，不虚抬；② update 全量四查时整体重算。

机械化衔接：check-map.py 产出直接喂 Coverage 机械部分——paths/counts 全绿即「清单核对 N/N」定格；update 推进 verified 以脚本全绿为前提。抽读档位仍归 agent：脚本不读语义，不虚抬。

## review 三看（图码同 PR 时）

建议性——skill 管不着目标项目的 PR 制度：

1. 新/改条目的路径与 symbols 在同一 diff 里可机械验证。
2. 职责一句话与 diff 语义一致（唯一需要人脑的一项）。
3. 新条目与 INDEX 既有行无重复（硬门槛的人肉版）。
