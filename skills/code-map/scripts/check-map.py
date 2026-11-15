"""code-map 四查核查器：只产发现清单，零修改——裁决与修图归 agent（处置表见 references/maintenance.md）。

用法: python check-map.py <目标仓路径>
输出: MISS / BAD / DRIFT / BROKEN-LINK 发现清单 + 各查汇总（+ NOTE 说明行）；有发现退出码 1。
栈检测表（「什么算导出」）v1 仅 Nuxt/Vue/TS；未识别栈时仅 symbols 查跳过，其余三查照跑。
"""
import re
import subprocess
import sys
from pathlib import Path

PATH_TOKEN = re.compile(r"[A-Za-z0-9_.\[\]-]+(?:/[A-Za-z0-9_.\[\]-]+)*(?:/\*\*)?")
COUNT_NOTATION = re.compile(r"[（(]\s*(~?\d+)\s*[)）]")
MD_LINK = re.compile(r"\]\(([^)#\s]+?\.md)\)")
BACKTICK = re.compile(r"`([^`\s]+)`")
PAREN = re.compile(r"[（(][^）)]*[）)]")
CJK = re.compile(r"[\u4e00-\u9fff]")
EXPORT_DECL = re.compile(r"\bexport\s+(?:const|let|var|async\s+function|function|class|enum)\s+([A-Za-z0-9_]+)")
EXPORT_LIST = re.compile(r"\bexport\s*\{([^}]*)\}")
DEFINE_STORE = re.compile(r"defineStore\(\s*[\"']([A-Za-z0-9_-]+)[\"']")
IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
CODE_EXT = (".ts", ".tsx", ".js", ".mjs", ".vue")


def read(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def parse_files_fields(text):
    """files 字段 → (路径引用, 计数引用)。token 原样保留：速记锚点是人定的，解析归 resolve_ref。

    括注外仍含 CJK 的 chunk（如「X 系列」）是家族散文，不是路径引用，跳过。
    """
    refs, counts = [], []
    in_files = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("files:"):
            in_files = True
            s = s[len("files:"):].strip()
        elif in_files and s.startswith("- "):
            s = s[2:].strip()
        else:
            in_files = False
            continue
        if not s:
            continue
        for chunk in re.split(r"[,，]", s):
            m = PATH_TOKEN.match(chunk.strip())
            if not m:
                continue
            tok, rest = m.group(0), chunk[m.end():]
            if CJK.search(PAREN.sub("", chunk)):
                continue
            refs.append(tok)
            if tok.endswith("/**"):
                cm = COUNT_NOTATION.search(rest)
                if cm and not cm.group(1).startswith("~"):
                    counts.append((tok[:-3], int(cm.group(1))))
    return refs, counts


class Codebase:
    """git 清单 + 派生索引，供各查共享。"""

    def __init__(self, repo, lsfiles):
        self.repo = repo
        self.lsfiles = lsfiles
        self.fileset = set(lsfiles)
        self.basenames = {x.rsplit("/", 1)[-1] for x in lsfiles}
        self.stems = {x.rsplit("/", 1)[-1].rsplit(".", 1)[0] for x in lsfiles}
        self.stem_list = list(self.stems)
        self.comps = self._component_names()

    def _component_names(self):
        """components/ 下按文件名/目录名推组件名（index.vue、index.client.vue → 目录名）。"""
        names = set()
        for rel in self.lsfiles:
            if not rel.startswith("components/"):
                continue
            parts = rel.split("/")
            stem = parts[-1].rsplit(".", 1)[0]
            if stem == "index" or stem.startswith("index."):
                if len(parts) >= 3:
                    names.add(parts[-2])
            elif stem:
                names.add(stem)
        return names

    def path_ok(self, tok):
        """files 字段引用存在性。全路径精确/后缀；裸名走组件名与 basename 阶梯（速记天生有歧义，
        只断言「库中有与之相符的实现物」，目录歧义交 agent）。"""
        if tok.endswith("/**"):
            base = tok[:-3]
            return (any(x.startswith(base + "/") for x in self.lsfiles)
                    or any(("/" + base + "/") in x for x in self.lsfiles))
        if "/" in tok:
            return tok in self.fileset or any(x.endswith("/" + tok) for x in self.lsfiles)
        stem = tok.rsplit(".", 1)[0] if "." in tok else tok
        return (tok in self.comps or stem in self.comps
                or tok in self.basenames or stem in self.stems
                or any(s.endswith(stem) for s in self.stem_list)
                or any(("/" + tok + "/") in x for x in self.lsfiles)
                or any(("/" + stem + "/") in x for x in self.lsfiles))

    def glob_roots(self, base):
        """`base/**` 的锚定目录集合：全路径前缀优先，否则按组件段后缀锚定。"""
        direct = [x for x in self.lsfiles if x.startswith(base + "/")]
        if direct:
            return {base}
        roots = set()
        marker = "/" + base + "/"
        for x in self.lsfiles:
            i = x.find(marker)
            if i != -1:
                roots.add(x[: i + len(marker) - 1])
        return roots


def check_paths(md_files, code):
    refs = set()
    for f in md_files:
        text = read(f)
        field_refs, _ = parse_files_fields(text)
        refs |= {(f.name, p) for p in field_refs}
        for m in BACKTICK.finditer(text):
            v = m.group(1)
            # 反引号串只查「形如文件」者（带扩展名或 /** 通配），目录名/散文不误报
            if "/" in v and PATH_TOKEN.fullmatch(v) and (v.endswith("/**") or "." in v.rsplit("/", 1)[-1]):
                refs.add((f.name, v))
    misses = [(n, p) for n, p in sorted(refs) if not code.path_ok(p)]
    print(f"paths: checked={len(refs)} misses={len(misses)}")
    for name, p in misses:
        print(f"MISS {name}: {p}")
    return len(misses)


def check_counts(md_files, code):
    seen = set()
    for f in md_files:
        _, counts = parse_files_fields(read(f))
        seen |= {(f.name, base, claimed) for base, claimed in counts}
    drift, notes = [], []
    checked = 0
    for name, base, claimed in sorted(seen):
        roots = code.glob_roots(base)
        if not roots:
            drift.append((name, base, claimed, 0))
            continue
        if len(roots) > 1:
            notes.append(f"NOTE {name}: {base}/** count skipped — anchor ambiguous ({len(roots)} roots)")
            continue
        checked += 1
        root = next(iter(roots))
        actual = sum(1 for x in code.lsfiles if x.startswith(root + "/"))
        if actual != claimed:
            drift.append((name, base, claimed, actual))
    print(f"counts: checked={checked + len(drift)} drift={len(drift)}")
    for name, base, c, a in drift:
        print(f"DRIFT {name}: {base}/** claimed={c} actual={a}")
    for line in notes:
        print(line)
    return len(drift)


def detect_stack(code):
    if "nuxt.config.ts" in code.fileset:
        return "nuxt/vue/ts"
    pkg = read(code.repo / "package.json")
    if '"nuxt"' in pkg or '"vue"' in pkg:
        return "nuxt/vue/ts"
    if any(x.endswith(".vue") for x in code.lsfiles):
        return "nuxt/vue/ts"
    return None


def build_export_table(code):
    exports = set()
    for rel in code.lsfiles:
        if not rel.endswith(CODE_EXT):
            continue
        text = read(code.repo / rel)
        exports.update(m.group(1) for m in EXPORT_DECL.finditer(text))
        for m in EXPORT_LIST.finditer(text):
            for item in m.group(1).split(","):
                names = IDENT.findall(item)
                if names and names[-1] != "as":
                    exports.add(names[-1])
        exports.update(m.group(1) for m in DEFINE_STORE.finditer(text))
    return exports


def check_symbols(md_files, code):
    stack = detect_stack(code)
    if not stack:
        print("symbols: skipped — stack not recognized (detection table ships nuxt/vue/ts only)")
        return 0
    exports = build_export_table(code)
    checked = bad = 0
    misses = []
    for f in md_files:
        if f.name == "INDEX.md":
            continue
        for line in read(f).splitlines():
            if not line.startswith("symbols:"):
                continue
            body = re.split(r"[（(]", line[len("symbols:"):], 1)[0]
            for sym in IDENT.findall(body):
                checked += 1
                if sym not in exports and sym not in code.comps:
                    bad += 1
                    misses.append((f.name, sym))
    print(f"symbols: stack={stack} exports={len(exports)} comps={len(code.comps)} checked={checked} bad={bad}")
    for name, s in misses:
        print(f"BAD {name}: {s}")
    return bad


def check_links(md_files):
    names = {f.name for f in md_files}
    module_names = names - {"INDEX.md"}
    broken = []
    checked = 0
    index = next((f for f in md_files if f.name == "INDEX.md"), None)
    if index:
        targets = set()
        for m in MD_LINK.finditer(read(index)):
            t = m.group(1).split("#")[0]
            if not t.startswith(("http://", "https://")):
                targets.add(t)
        checked += len(targets) + len(module_names)
        for t in sorted(targets):
            if t not in names:
                broken.append((index.name, t))
        for name in sorted(module_names - targets):
            broken.append((index.name, f"no link to module file {name}"))
    for f in md_files:
        if f.name == "INDEX.md":
            continue
        for m in MD_LINK.finditer(read(f)):
            t = m.group(1).split("#")[0]
            if t.startswith(("http://", "https://")):
                continue
            checked += 1
            if t not in names:
                broken.append((f.name, t))
    print(f"links: checked={checked} broken={len(broken)}")
    for name, t in broken:
        print(f"BROKEN-LINK {name}: {t}")
    return len(broken)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python check-map.py <target-repo-path>")
    repo = Path(sys.argv[1]).resolve()
    md_dir = repo / "docs" / "code-map"
    if not md_dir.is_dir():
        sys.exit(f"not a code-mapped repo (no docs/code-map/): {repo}")
    r = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                       cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"git ls-files failed in {repo}: {r.stderr.strip()}")
    code = Codebase(repo, r.stdout.splitlines())
    md_files = [f for f in sorted(md_dir.glob("*.md")) if not f.name.startswith(".init")]

    total = 0
    total += check_paths(md_files, code)
    total += check_counts(md_files, code)
    total += check_symbols(md_files, code)
    total += check_links(md_files)
    print("result:", "OK — no findings" if total == 0 else f"{total} finding(s)")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
