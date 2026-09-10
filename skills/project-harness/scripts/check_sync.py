#!/usr/bin/env python3
"""check_sync.py — 对目标项目的 AGENTS.md + aiDoc/ 做机械漂移检查。

用法:
    python3 check_sync.py <repo-path>

检查项:
    1. 索引完整性: aiDoc/README.md 中引用的相对 .md 路径必须存在。
    2. 路径真实性: AGENTS.md 与 aiDoc/**/*.md 中行内代码里形如 src/... 的
       代码路径，必须在仓库根下存在（宁缺毋滥，只查白名单顶层目录）。
    3. last-updated 头部: aiDoc/ 下每个 .md（TEMPLATE 豁免；.harness-backups/
       等点目录跳过）前 5 行内应有 <!-- last-updated: YYYY-MM-DD -->。
    4. 区域一致性（提示级别，不影响退出码）: AGENTS.md 提到的 aiDoc 区域名
       与实际子目录互相对照。

输出为纯文本（无颜色依赖），每项 ✅/❌ + 明细，末尾总计。
退出码: 0 全部通过；1 存在 ❌；2 目标缺 AGENTS.md 或 aiDoc/。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 检查 2：只认这些常见源码顶层目录开头的行内代码（白名单，宁缺毋滥）
CODE_TOP_DIRS = (
    "src", "app", "pkg", "cmd", "internal", "lib", "server", "client",
)

# 检查 4：aiDoc 标准区域名
AIDOC_SECTIONS = (
    "relations", "modules", "frontend-backend", "examples",
    "memory", "notes", "plans",
)

MD_REF_RE = re.compile(r"[A-Za-z0-9_\-./]+\.md(?:#[A-Za-z0-9_\-]*)?")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
LAST_UPDATED_RE = re.compile(
    r"<!--\s*last-updated:\s*\d{4}-\d{2}-\d{2}\s*-->")


def iter_aidoc_md(aidoc: Path):
    """aiDoc 下的 .md 文件，跳过 .harness-backups/ 等点目录。"""
    for f in sorted(aidoc.rglob("*.md")):
        rel = f.relative_to(aidoc)
        if any(part.startswith(".") for part in rel.parts):
            continue
        yield f


class Report:
    def __init__(self) -> None:
        self.checks: list[tuple[str, bool, list[str], bool]] = []
        # (标题, 是否通过, 明细行, 是否仅提示级别)

    def add(self, title: str, ok: bool, details: list[str], *,
            hint_only: bool = False) -> None:
        self.checks.append((title, ok, details, hint_only))

    def print(self) -> int:
        passed = failed = hints = 0
        for i, (title, ok, details, hint_only) in enumerate(self.checks, 1):
            if ok:
                mark = "✅"
                passed += 1
            elif hint_only:
                mark = "⚠️ (提示)"
                hints += 1
            else:
                mark = "❌"
                failed += 1
            print(f"[{i}/{len(self.checks)}] {title} ... {mark}")
            for line in details:
                print(f"    {line}")
            print()
        print(f"===== 总计: {passed} 通过, {failed} 失败, {hints} 提示 =====")
        return 1 if failed else 0


# ---------------------------------------------------------------- 检查 1

def check_index(repo: Path, aidoc: Path) -> tuple[bool, list[str]]:
    readme = aidoc / "README.md"
    if not readme.is_file():
        return False, ["aiDoc/README.md 不存在，无法检查索引"]
    text = readme.read_text(encoding="utf-8", errors="replace")
    missing: list[str] = []
    seen: set[str] = set()
    for m in MD_REF_RE.finditer(text):
        ref = m.group(0)
        if "://" in ref:
            continue
        # 占位符断裂的匹配（如 <workflow>/SKILL.md 只匹配到 /SKILL.md）：跳过
        if m.start() > 0 and text[m.start() - 1] in "<>":
            continue
        ref = ref.split("#", 1)[0]
        if ref.startswith("./"):
            ref = ref[2:]
        for prefix in ("aiDoc/", "aidoc/"):
            if ref.startswith(prefix):
                ref = ref[len(prefix):]
                break
        # 形如 xxx/yyy.md 才视为路径引用；裸文件名（如 AGENTS.md）不算
        if not ref or "/" not in ref or ref in seen:
            continue
        seen.add(ref)
        if ref.startswith("/"):
            # 仓库根绝对引用（如 /AGENTS.md）
            if not (repo / ref[1:]).exists():
                missing.append(f"缺失: {ref}  (aiDoc/README.md 中引用)")
        elif ref.startswith("."):
            # 仓库根相对引用（如 .agents/skills/...）
            if not (repo / ref).exists():
                missing.append(f"缺失: {ref}  (aiDoc/README.md 中引用)")
        elif not (aidoc / ref).exists():
            missing.append(f"缺失: {ref}  (aiDoc/README.md 中引用)")
    return (not missing), missing


# ---------------------------------------------------------------- 检查 2

def _code_path_candidates(text: str) -> list[str]:
    out: list[str] = []
    for span in INLINE_CODE_RE.findall(text):
        token = span.strip()
        if "/" not in token or "://" in token:
            continue
        if any(ch in token for ch in (" ", "?", "#", "*", "{", "}", "(", ")", ":")):
            continue
        token = token[2:] if token.startswith("./") else token
        top = token.split("/", 1)[0]
        if top in CODE_TOP_DIRS:
            out.append(token.rstrip("/"))
    return out


def check_paths(repo: Path, aidoc: Path, agents: Path) -> tuple[bool, list[str]]:
    files = [agents] + list(iter_aidoc_md(aidoc))
    missing: list[str] = []
    seen: set[str] = set()
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        rel_f = f.relative_to(repo)
        for lineno, line in enumerate(lines, 1):
            for cand in _code_path_candidates(line):
                key = f"{cand}"
                if key in seen:
                    continue
                seen.add(key)
                if not (repo / cand).exists():
                    missing.append(
                        f"不存在: {cand}  (引用于 {rel_f}:{lineno})")
    return (not missing), missing


# ---------------------------------------------------------------- 检查 3

def check_last_updated(aidoc: Path) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for f in iter_aidoc_md(aidoc):
        if "TEMPLATE" in f.name.upper():
            continue
        try:
            head = f.read_text(
                encoding="utf-8", errors="replace").splitlines()[:5]
        except OSError:
            continue
        if not any(LAST_UPDATED_RE.search(line) for line in head):
            missing.append(f"缺少 last-updated 头部: {f.relative_to(aidoc)}")
    return (not missing), missing


# ---------------------------------------------------------------- 检查 4

def check_sections(aidoc: Path, agents: Path) -> tuple[bool, list[str]]:
    text = agents.read_text(encoding="utf-8", errors="replace")
    details: list[str] = []
    ok = True
    for section in AIDOC_SECTIONS:
        mentioned = re.search(
            r"(?<![\w-])" + re.escape(section) + r"(?![\w-])", text) is not None
        exists = (aidoc / section).is_dir()
        if mentioned and not exists:
            ok = False
            details.append(f"AGENTS.md 提到但目录不存在: aiDoc/{section}/")
        elif exists and not mentioned:
            ok = False
            details.append(f"目录存在但 AGENTS.md 完全未提及: aiDoc/{section}/")
    return ok, details


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv and argv[0] in ("-h", "--help") else 2

    repo = Path(argv[0]).expanduser().resolve()
    agents = repo / "AGENTS.md"
    aidoc = repo / "aiDoc"
    if not agents.is_file() or not aidoc.is_dir():
        print("错误: 目标缺少 AGENTS.md 或 aiDoc/，无法检查。"
              "请先运行 init_project.py。", file=sys.stderr)
        print(f"  AGENTS.md: {'存在' if agents.is_file() else '缺失'}  {agents}",
              file=sys.stderr)
        print(f"  aiDoc/:    {'存在' if aidoc.is_dir() else '缺失'}  {aidoc}",
              file=sys.stderr)
        return 2

    print(f"check_sync: {repo}\n")
    report = Report()

    ok, details = check_index(repo, aidoc)
    report.add("索引完整性 (aiDoc/README.md 引用的 .md 均存在)", ok, details)

    ok, details = check_paths(repo, aidoc, agents)
    report.add("路径真实性 (行内代码路径在仓库中存在)", ok, details)

    ok, details = check_last_updated(aidoc)
    report.add("last-updated 头部 (aiDoc 下 .md 前 5 行)", ok, details)

    ok, details = check_sections(aidoc, agents)
    report.add("区域一致性 (AGENTS.md 提到的区域 vs 实际目录)", ok, details,
               hint_only=True)

    return report.print()


if __name__ == "__main__":
    sys.exit(main())
