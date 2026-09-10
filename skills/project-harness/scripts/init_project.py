#!/usr/bin/env python3
"""init_project.py — 把 project-harness 模板骨架安装到任意目标仓库。

用法:
    python3 init_project.py <repo-path> [--project-name NAME] [--lang zh|en]
                            [--dry-run] [--overwrite] [--no-scan]

行为概述:
    1. 校验 <repo-path> 的 git 根（嵌套仓库拒绝，非 git 仓库警告后继续）。
    2. 基于 scan_repo.py 的组件探测判定项目类型（fullstack / backend /
       frontend / library / cli / general / mixed）与技术栈线索。
    3. 从 skills/project-harness/templates/<lang>/ 拷贝 aiDoc 骨架、AGENTS.md、
       CLAUDE.md、.agents/skills，并创建 notes/plans 生命周期目录；
       未探测到前端时跳过的 frontend/ 文件会同步裁剪索引
       （aiDoc/README.md、AGENTS.md）中引用它们的行。
    4. 静态扫描填充（--no-scan 关闭）：把清单/结构等机械事实填入本次新生成的
       relations 文档（锚 `## ` 小节标题，zh/en 双语），并总是重新生成
       aiDoc/relations/code-index.md（机器产物，覆盖规则例外）。
    5. 默认绝不覆盖已存在文件；--overwrite 会先备份到 aiDoc/.harness-backups/。
    6. 幂等：第二次运行文档全部 SKIP，code-index.md 重新生成且内容一致。

退出码: 0 成功；2 参数错误 / 嵌套 git 拒绝。
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_ROOT = SCRIPT_DIR.parent / "templates"

try:
    import scan_repo
except ImportError:  # 被其他脚本 import 时兜底
    sys.path.insert(0, str(SCRIPT_DIR))
    import scan_repo

# 与模板布局对应的条件性跳过清单（相对 aidoc/ 根）。
# 仅 frontend/ 区域是条件性的：未探测到前端时跳过；其余区域全类型保留，
# 内容由 generate 工作流按范式适配。若模板文件名调整，这里需要同步修改。
FRONTEND_SKIP = (
    "frontend/frontend-rules.md",
    "frontend/frontend-utils.md",
)

GITIGNORE_LINE = "aiDoc/.harness-backups/"

LIFECYCLE_DIRS = (
    "aiDoc/notes/proposed",
    "aiDoc/notes/implemented",
    "aiDoc/notes/rejected",
    "aiDoc/plans/active",
    "aiDoc/plans/completed",
)


# ---------------------------------------------------------------- git 根校验

def find_git_root(path: Path) -> Path | None:
    """向上查找包含 .git 的目录（.git 可以是目录或 worktree 文件）。"""
    for cand in (path, *path.parents):
        if (cand / ".git").exists():
            return cand
    return None


# ---------------------------------------------------------------- 项目探测

def detect_project(repo: Path, scan: dict | None = None) -> tuple[str, list[str], bool]:
    """返回 (项目类型, 线索说明列表, 是否探测到前端)。

    基于 scan_repo 的组件探测实现。类型 ∈ fullstack/backend/frontend/
    library/cli/general/mixed：前端+Web 框架（同路径）→ fullstack；
    仅前端 → frontend；仅 Web/Java 框架 → backend；CLI 入口 → cli；
    库打包标志 → library；qt/go-module/cpp 组件单独存在 → general
    （clues 注明组件）；多路径多类型 → mixed；无任何标志 → general。
    """
    if scan is None:
        scan = scan_repo.scan_repo(repo)
    return scan["label"], list(scan["clues"]), scan["has_frontend"]


# ---------------------------------------------------------------- 拷贝计划

class Plan:
    def __init__(self) -> None:
        self.created: list[str] = []       # CREATE / APPEND
        self.skipped: list[str] = []       # 已存在，SKIP
        self.overwritten: list[str] = []   # BACKUP+OVERWRITE
        self.deferred: list[str] = []      # 未探测到前端，跳过 frontend/
        self.backups: list[str] = []       # 备份目标路径
        self.auto_filled: list[str] = []   # 扫描填充（relations 文档小节 + code-index）


def _render(text: str, project_name: str, today: str) -> str:
    return text.replace("{{PROJECT_NAME}}", project_name).replace("{{DATE}}", today)


def _copy_file(src: Path, dst: Path, repo: Path, plan: Plan, *,
               overwrite: bool, dry_run: bool, render: tuple[str, str] | None,
               backup_root: Path, label_prefix: str = "") -> None:
    rel = dst.relative_to(repo)
    tag = f"{label_prefix}{rel}"
    if dst.exists():
        if not overwrite:
            plan.skipped.append(str(rel))
            return
        backup = backup_root / rel
        plan.overwritten.append(f"{rel}  (备份 -> {backup.relative_to(repo)})")
        plan.backups.append(str(backup.relative_to(repo)))
        if dry_run:
            return
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, backup)
    else:
        plan.created.append(tag)
        if dry_run:
            return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if render is not None:
        try:
            text = src.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            shutil.copy2(src, dst)
        else:
            dst.write_text(_render(text, render[0], render[1]), encoding="utf-8")
    else:
        shutil.copy2(src, dst)


# ---------------------------------------------------------------- 引用裁剪

def _freshly_written(plan: Plan, rel: str) -> bool:
    """该文件是否本次刚由模板写入（created 或 overwrite）——已存在的用户文件不碰。"""
    if rel in plan.created:
        return True
    return any(it.startswith(rel + "  ") for it in plan.overwritten)


def _prune_deferred_refs(repo: Path, skip_set: set[str], plan: Plan, *,
                         dry_run: bool) -> None:
    """从本次新生成的 aiDoc/README.md 与 AGENTS.md 中删除引用被跳过文件的行。

    表格行均为单行，按行过滤安全；AGENTS.md 中的散文条目（非 | 开头）保留，
    交由 generate 工作流重写。
    """
    if not skip_set:
        return
    path_needles = tuple(skip_set)
    # 整个区域被跳过时，还需删除索引中指向该区域目录的表格行
    area_tokens: tuple[str, ...] = ()
    if set(FRONTEND_SKIP) <= skip_set:
        area_tokens = ("`frontend/`", "`aiDoc/frontend/`")

    for rel in ("aiDoc/README.md", "AGENTS.md"):
        if not _freshly_written(plan, rel):
            continue
        f = repo / rel
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        kept: list[str] = []
        dropped = 0
        for ln in lines:
            if any(n in ln for n in path_needles):
                dropped += 1
                continue
            if area_tokens and ln.lstrip().startswith("|") \
                    and any(t in ln for t in area_tokens):
                dropped += 1
                continue
            kept.append(ln)
        if dropped:
            plan.created.append(f"{rel}  (裁剪 {dropped} 行失效引用)")
            if not dry_run:
                f.write_text("\n".join(kept) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- 扫描填充

AUTO_SCAN_MARK = "<!-- auto-scan: init 扫描生成，generate 工作流校订后移除此标记 -->"
CODE_INDEX_REL = "aiDoc/relations/code-index.md"

# 双语小节锚点表（取 templates/zh 与 templates/en 的实际 `## ` 标题；
# 匹配时只锚标题文本，不锚整行，容忍模板其它行变化）
SECTION_ANCHORS = {
    "positioning": ("项目定位", "Project Positioning"),
    "stack": ("核心技术栈", "Core Tech Stack"),
    "pkgmgmt": ("包管理", "Package Management"),
    "features": ("核心特性", "Core Features"),
    "env": ("环境与依赖", "Environment & Dependencies",
            "Environment and Dependencies"),
    "rootdirs": ("根目录职责", "Root Directory Responsibilities"),
    "config": ("配置文件", "Configuration Files"),
}

# 配置文件用途（zh, en）
_CONFIG_PURPOSE = {
    "package.json": ("Node 清单（name/scripts/依赖）",
                     "Node manifest (name/scripts/deps)"),
    "pyproject.toml": ("Python 工程配置", "Python project configuration"),
    "requirements.txt": ("Python 依赖清单", "Python dependency list"),
    "setup.py": ("Python 打包配置", "Python packaging"),
    "go.mod": ("Go 模块定义", "Go module definition"),
    "pom.xml": ("Maven 工程配置", "Maven project configuration"),
    "build.gradle": ("Gradle 构建配置", "Gradle build configuration"),
    "build.gradle.kts": ("Gradle 构建配置（Kotlin DSL）",
                         "Gradle build configuration (Kotlin DSL)"),
    "CMakeLists.txt": ("CMake 构建配置", "CMake build configuration"),
    "Makefile": ("make 目标定义", "make targets"),
    "Cargo.toml": ("Rust crate 配置", "Rust crate configuration"),
    "nvmrc": ("Node 版本固定", "Node version pin"),
    "python-version": ("Python 版本固定", "Python version pin"),
    "dockerfile": ("容器镜像构建", "container image build"),
    "docker-compose": ("容器编排", "container orchestration"),
    "tox": ("tox 多环境测试", "tox multi-env testing"),
    "gh-workflows": ("GitHub Actions 工作流", "GitHub Actions workflows"),
    "sln": ("Visual Studio 解决方案", "Visual Studio solution"),
    "vcxproj": ("Visual Studio C++ 工程", "Visual Studio C++ project"),
}


def _find_section(lines: list[str], candidates: tuple[str, ...]):
    """按 `## ` 标题文本定位小节，返回 (标题行号, 下一标题/文末行号, 标题)。"""
    cands = tuple(c.lower() for c in candidates)
    for i, ln in enumerate(lines):
        m = re.match(r"^##\s+(.+?)\s*$", ln)
        if not m:
            continue
        title = m.group(1).strip().lower()
        if any(title == c or c in title for c in cands):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## "):
                j += 1
            return i, j, m.group(1).strip()
    return None


def _fill_sections(text: str, sections: list) -> tuple[str, list[str], list[str]]:
    """sections: [(key, candidates, body_lines)]。整段替换小节正文。"""
    lines = text.splitlines()
    matches = []
    missing: list[str] = []
    for key, candidates, body in sections:
        found = _find_section(lines, candidates)
        if found:
            matches.append((found[0], found[1], found[2], body))
        else:
            missing.append(key)
    done = [m[2] for m in matches]
    for i, j, _title, body in sorted(matches, key=lambda m: m[0], reverse=True):
        lines[i + 1:j] = ["", AUTO_SCAN_MARK, ""] + body + [""]
    return "\n".join(lines) + "\n", done, missing


def _primary_identity(scan: dict, project_name: str) -> tuple[str, str | None]:
    """从清单推断项目名与一句话描述（优先根目录清单）。"""
    man = scan["manifests"]
    order = sorted(man.items(), key=lambda kv: ("/" in kv[0], kv[0]))
    name = desc = None
    for rel, m in order:
        if name is None:
            name = m.get("name") or m.get("artifact") or m.get("module") \
                or m.get("project") or m.get("target")
        if desc is None:
            desc = m.get("description")
    return name or project_name, desc


def _root_disp(lang: str) -> str:
    return "（根）" if lang == "zh" else "(root)"


def _comp_path_disp(path: str, lang: str) -> str:
    return _root_disp(lang) if path == "." else f"`{path}`"


def _pos_lines(scan: dict, lang: str, project_name: str) -> list[str]:
    name, desc = _primary_identity(scan, project_name)
    ptype = scan["label"]
    n = len([c for c in scan["components"] if c["kind"] != "generic"])
    if lang == "zh":
        if desc:
            return [f"**{name}** — {desc}（项目类型：{ptype}，组件 {n} 个）"]
        return [f"**{name}**（项目类型：{ptype}，组件 {n} 个；"
                "清单文件未提供描述，待 generate 工作流补充）"]
    if desc:
        return [f"**{name}** — {desc} (project type: {ptype}, {n} components)"]
    return [f"**{name}** (project type: {ptype}, {n} components; no "
            "description found in manifests — generate workflow to refine)"]


def _stack_table(scan: dict, lang: str) -> list[str]:
    zh = lang == "zh"
    rows = ["| 组件 | 路径 | 技术栈 |" if zh else "| Component | Path | Stack |",
            "|---|---|---|"]
    comps = [c for c in scan["components"] if c["kind"] != "generic"]
    if not comps:
        langs = ", ".join(f"{ext} ×{n}"
                          for ext, n in list(scan["languages"].items())[:4])
        note = ("主要语言: " + langs) if langs else \
            ("未识别技术栈" if zh else "no stack signals")
        rows.append(f"| generic | {_root_disp(lang)} | {note} |")
    for c in comps:
        rows.append(f"| {c['kind']} | {_comp_path_disp(c['path'], lang)} "
                    f"| {c['stack']} |")
    return rows


def _pkgmgmt_lines(scan: dict, lang: str) -> list[str]:
    zh = lang == "zh"
    pms = scan["package_managers"]
    if not pms:
        return ["未检测到包管理配置。" if zh else
                "No package manager configuration detected."]
    out = []
    for p in pms:
        evi = ", ".join(f"`{e}`" for e in p["evidence"])
        out.append(f"- {p['tool']}（依据: {evi}）" if zh else
                   f"- {p['tool']} (evidence: {evi})")
    return out


def _features_table(scan: dict, lang: str) -> list[str]:
    zh = lang == "zh"
    rows = ["| 入口 | 类型 | 位置 |" if zh else "| Entry | Type | Location |",
            "|---|---|---|"]
    eps = scan["entry_points"][:15]
    if not eps:
        rows.append("| - | " + ("未发现明确入口点" if zh else
                                 "no entry points found") + " | - |")
    for e in eps:
        rows.append(f"| {e['name']} | {e['type']} | `{e['location']}` |")
    if len(scan["entry_points"]) > 15:
        rows.append(f"| … | 共 {len(scan['entry_points'])} 个，详见 code-index.md | - |"
                    if zh else
                    f"| … | {len(scan['entry_points'])} total, see code-index.md | - |")
    return rows


def _env_table(scan: dict, lang: str) -> list[str]:
    zh = lang == "zh"
    rows = ["| 操作 | 命令 |" if zh else "| Task | Command |", "|---|---|"]
    cmds = scan["commands"][:15]
    if not cmds:
        rows.append("| - | " + ("未发现命令定义" if zh else
                                 "no commands found") + " |")
    for c in cmds:
        src_dir = c["source"].rsplit("/", 1)[0] if "/" in c["source"] else "."
        where = _root_disp(lang) if src_dir == "." else src_dir
        rows.append(f"| {c['name']}（{where}） | `{c['command']}` |" if zh else
                    f"| {c['name']} ({where}) | `{c['command']}` |")
    return rows


def _rootdirs_table(scan: dict, lang: str) -> list[str]:
    zh = lang == "zh"
    rows = ["| 目录 | 职责 |" if zh else "| Directory | Responsibility |",
            "|---|---|"]
    comp_by_path: dict = {}
    for c in scan["components"]:
        if c["kind"] != "generic":
            comp_by_path.setdefault(c["path"], []).append(c["kind"])
    if not scan["top_dirs"]:
        rows.append("| - | " + ("无子目录" if zh else "no subdirectories") + " |")
    for d in scan["top_dirs"]:
        parts = []
        if d["convention"]:
            parts.append(scan_repo.DIR_CONVENTIONS[d["convention"]]
                         [0 if zh else 1])
        exts = ", ".join(d["exts"])
        seg = f"{d['files']} 个文件（{exts}）" if zh and exts else \
            (f"{d['files']} 个文件" if zh else
             (f"{d['files']} files ({exts})" if exts else f"{d['files']} files"))
        parts.append(seg)
        kinds = comp_by_path.get(d["name"])
        if kinds:
            parts.append(("组件: " if zh else "components: ") + "/".join(kinds))
        rows.append(f"| `{d['name']}` | {'；'.join(parts) if zh else '; '.join(parts)} |")
    return rows


def _config_table(scan: dict, lang: str) -> list[str]:
    zh = lang == "zh"
    idx = 0 if zh else 1
    rows = ["| 文件 | 用途 |" if zh else "| File | Purpose |", "|---|---|"]
    items = []
    for rel in sorted(scan["manifests"]):
        base = rel.rsplit("/", 1)[-1]
        if base.endswith(".pro"):
            purpose = ("qmake 工程文件", "qmake project file")[idx]
        else:
            purpose = _CONFIG_PURPOSE.get(base, ("工程清单", "project manifest"))[idx]
        items.append((rel, purpose))
    for c in scan["configs"]:
        purpose = _CONFIG_PURPOSE.get(c["kind"], (c["kind"], c["kind"]))[idx]
        if c["value"] is not None:
            purpose += f"（{c['value']}）" if zh else f" ({c['value']})"
        items.append((c["path"], purpose))
    if not items:
        rows.append("| - | " + ("未发现配置文件" if zh else
                                 "no config files found") + " |")
    for rel, purpose in items[:20]:
        rows.append(f"| `{rel}` | {purpose} |")
    return rows


def _fill_specs(scan: dict, lang: str, project_name: str) -> list:
    A = SECTION_ANCHORS
    return [
        ("aiDoc/relations/repo-profile.md", [
            ("positioning", A["positioning"], _pos_lines(scan, lang, project_name)),
            ("stack", A["stack"], _stack_table(scan, lang)),
            ("pkgmgmt", A["pkgmgmt"], _pkgmgmt_lines(scan, lang)),
            ("features", A["features"], _features_table(scan, lang)),
        ]),
        ("aiDoc/relations/development-workflow.md", [
            ("env", A["env"], _env_table(scan, lang)),
        ]),
        ("aiDoc/relations/system-map.md", [
            ("rootdirs", A["rootdirs"], _rootdirs_table(scan, lang)),
            ("config", A["config"], _config_table(scan, lang)),
        ]),
    ]


def apply_scan_fill(repo: Path, templates: Path, scan: dict, plan: Plan, *,
                    lang: str, project_name: str, dry_run: bool) -> None:
    """把扫描事实填入本次新生成的 relations 文档，并重新生成 code-index.md。

    只填 _freshly_written 命中的文件；code-index.md 是机器产物，总是重新
    生成（覆盖规则例外）。dry-run 下只记录计划，不写文件。
    """
    today = date.today().isoformat()
    for rel, sections in _fill_specs(scan, lang, project_name):
        if not _freshly_written(plan, rel):
            continue
        if dry_run:
            src = templates / "aidoc" / rel[len("aiDoc/"):]
            if not src.is_file():
                plan.auto_filled.append(f"{rel}  (模板缺失，跳过扫描填充)")
                continue
            try:
                text = _render(src.read_text(encoding="utf-8"),
                               project_name, today)
            except OSError:
                continue
        else:
            try:
                text = (repo / rel).read_text(encoding="utf-8")
            except OSError:
                continue
        new_text, done, missing = _fill_sections(text, sections)
        tag = "dry-run 计划填充" if dry_run else "扫描填充"
        if done:
            plan.auto_filled.append(f"{rel}  ({tag}: {'、'.join(done)})")
        for key in missing:
            plan.auto_filled.append(f"{rel}  (锚点未找到，跳过小节: {key})")
        if done and not dry_run:
            (repo / rel).write_text(new_text, encoding="utf-8")

    # code-index.md：机器产物，总是重新生成
    content = scan_repo.render_code_index(scan, lang=lang, today=today)
    if dry_run:
        plan.auto_filled.append(f"{CODE_INDEX_REL}  (机器产物，dry-run 计划重新生成)")
    else:
        dst = repo / CODE_INDEX_REL
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
        plan.auto_filled.append(f"{CODE_INDEX_REL}  (机器产物，已重新生成)")


def build_and_run(repo: Path, templates: Path, project_name: str,
                  has_frontend: bool, *, overwrite: bool, dry_run: bool) -> Plan:
    plan = Plan()
    today = date.today().isoformat()
    render_ctx = (project_name, today)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = repo / "aiDoc" / ".harness-backups" / timestamp

    # 仅 frontend/ 区域是条件性的；contracts/boundary.md、modules/* 等其余
    # 区域对全部类型保留，内容由 generate 工作流按范式适配。
    skip_set = set() if has_frontend else set(FRONTEND_SKIP)

    # 1) aidoc/ -> aiDoc/（整树，含按类型跳过）
    aidoc_src = templates / "aidoc"
    if aidoc_src.is_dir():
        for root, dirs, files in os.walk(aidoc_src):
            dirs.sort()
            root_p = Path(root)
            rel_dir = root_p.relative_to(aidoc_src)
            for name in sorted(files):
                src = root_p / name
                rel = rel_dir / name
                rel_str = str(rel)
                if rel_str in skip_set:
                    plan.deferred.append(f"aiDoc/{rel_str}  (未探测到前端)")
                    continue
                dst = repo / "aiDoc" / rel
                if name.endswith(".tmpl"):
                    dst = dst.with_name(name[: -len(".tmpl")])
                _copy_file(src, dst, repo, plan, overwrite=overwrite,
                           dry_run=dry_run, render=render_ctx,
                           backup_root=backup_root)
            # 空目录也创建（模板中可能存在暂无文件的目录）
            if not files and not dirs:
                dst_dir = repo / "aiDoc" / rel_dir
                if str(rel_dir) != "." and not dst_dir.exists():
                    plan.created.append(f"aiDoc/{rel_dir}/  (空目录)")
                    if not dry_run:
                        dst_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"警告: 模板目录不存在: {aidoc_src}", file=sys.stderr)

    # 2) AGENTS.md.tmpl -> AGENTS.md
    agents_tmpl = templates / "AGENTS.md.tmpl"
    if agents_tmpl.is_file():
        _copy_file(agents_tmpl, repo / "AGENTS.md", repo, plan,
                   overwrite=overwrite, dry_run=dry_run, render=render_ctx,
                   backup_root=backup_root)

    # 3) CLAUDE.md -> CLAUDE.md
    claude = templates / "CLAUDE.md"
    if claude.is_file():
        _copy_file(claude, repo / "CLAUDE.md", repo, plan,
                   overwrite=overwrite, dry_run=dry_run, render=render_ctx,
                   backup_root=backup_root)

    # 4) agents-skills/ -> .agents/skills/
    skills_src = templates / "agents-skills"
    if skills_src.is_dir():
        for root, dirs, files in os.walk(skills_src):
            dirs.sort()
            root_p = Path(root)
            rel_dir = root_p.relative_to(skills_src)
            for name in sorted(files):
                src = root_p / name
                dst = repo / ".agents" / "skills" / rel_dir / name
                _copy_file(src, dst, repo, plan, overwrite=overwrite,
                           dry_run=dry_run, render=render_ctx,
                           backup_root=backup_root)

    # 5) 生命周期目录 .gitkeep
    for d in LIFECYCLE_DIRS:
        dst = repo / d / ".gitkeep"
        _copy_file_bytes(b"", dst, repo, plan, overwrite=overwrite,
                         dry_run=dry_run, backup_root=backup_root)

    # 6) .gitignore 追加 aiDoc/.harness-backups/
    gitignore = repo / ".gitignore"
    existing = ""
    if gitignore.is_file():
        try:
            existing = gitignore.read_text(encoding="utf-8")
        except OSError:
            existing = ""
    lines = [ln.strip() for ln in existing.splitlines()]
    if GITIGNORE_LINE in lines:
        plan.skipped.append(".gitignore (已含 aiDoc/.harness-backups/)")
    elif gitignore.exists():
        plan.created.append(".gitignore  (追加 aiDoc/.harness-backups/)")
        if not dry_run:
            with gitignore.open("a", encoding="utf-8") as fh:
                if existing and not existing.endswith("\n"):
                    fh.write("\n")
                fh.write(GITIGNORE_LINE + "\n")
    else:
        plan.created.append(".gitignore  (新建，含 aiDoc/.harness-backups/)")
        if not dry_run:
            gitignore.write_text(GITIGNORE_LINE + "\n", encoding="utf-8")

    # 7) 索引引用裁剪：删除 aiDoc/README.md 与 AGENTS.md 中指向被跳过文件的行
    _prune_deferred_refs(repo, skip_set, plan, dry_run=dry_run)

    return plan


def _copy_file_bytes(data: bytes, dst: Path, repo: Path, plan: Plan, *,
                     overwrite: bool, dry_run: bool, backup_root: Path) -> None:
    rel = dst.relative_to(repo)
    if dst.exists():
        if not overwrite:
            plan.skipped.append(str(rel))
            return
        backup = backup_root / rel
        plan.overwritten.append(f"{rel}  (备份 -> {backup.relative_to(repo)})")
        if not dry_run:
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup)
    else:
        plan.created.append(str(rel))
        if dry_run:
            return
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)


# ---------------------------------------------------------------- 报告

def print_report(plan: Plan, *, dry_run: bool) -> None:
    title = "执行计划（dry-run，未写入任何文件）" if dry_run else "执行结果"
    print(f"\n===== {title} =====")
    verb_create = "CREATE" if dry_run else "已创建"
    verb_skip = "SKIP"
    verb_over = "BACKUP+OVERWRITE" if dry_run else "已覆盖(含备份)"
    groups = (
        (f"created [{verb_create}]", plan.created),
        (f"skipped [{verb_skip}]", plan.skipped),
        (f"overwritten [{verb_over}]", plan.overwritten),
        ("deferred [未探测到前端，跳过]", plan.deferred),
        ("auto-filled [扫描填充]", plan.auto_filled),
    )
    for label, items in groups:
        print(f"\n-- {label}: {len(items)} 项")
        for it in items:
            print(f"   {it}")
    print("\n下一步:")
    print("  1. 在 Agent 工具中运行 project-harness 的 generate 工作流，")
    print("     扫描代码库并填充 aiDoc/ 各区域内容（relations/modules/examples 等）。")
    print("  2. 运行 python3 check_sync.py <repo> 校验骨架一致性。")


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="把 project-harness 的 aiDoc 骨架安装到目标仓库。")
    parser.add_argument("repo_path", help="目标仓库根目录")
    parser.add_argument("--project-name", default=None,
                        help="项目名（默认取仓库目录名）")
    parser.add_argument("--lang", choices=("zh", "en"), default="zh",
                        help="模板语言（默认 zh）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印 CREATE/SKIP/BACKUP+OVERWRITE 计划，不写文件")
    parser.add_argument("--overwrite", action="store_true",
                        help="覆盖已存在文件（先备份到 aiDoc/.harness-backups/）")
    parser.add_argument("--no-scan", action="store_true",
                        help="关闭静态扫描填充（保留骨架 TODO，不生成 code-index.md）")
    args = parser.parse_args(argv)

    repo = Path(args.repo_path).expanduser().resolve()
    if not repo.is_dir():
        print(f"错误: 路径不存在或不是目录: {repo}", file=sys.stderr)
        return 2

    # git 根校验
    git_root = find_git_root(repo)
    if git_root is None:
        print(f"警告: {repo} 不是 git 仓库（未找到 .git），仍将继续。"
              "建议先 git init。", file=sys.stderr)
    elif git_root != repo:
        print(f"错误: {repo} 是 git 仓库 {git_root} 的子目录。\n"
              f"请传仓库根目录: {git_root}", file=sys.stderr)
        return 2

    # 模板目录
    templates = TEMPLATES_ROOT / args.lang
    if not templates.is_dir():
        print(f"错误: 模板目录不存在: {templates}", file=sys.stderr)
        return 2

    project_name = args.project_name or repo.name

    # 静态扫描（只读）：项目探测与扫描填充共用同一份结果
    scan = scan_repo.scan_repo(repo)

    # 项目探测
    ptype, clues, has_frontend = detect_project(repo, scan=scan)
    print("===== 项目探测 =====")
    print(f"仓库: {repo}")
    print(f"项目类型: {ptype}")
    components = scan["components"]
    if components:
        print("组件清单:")
        for c in components:
            print(f"  {c['path']}: {c['kind']} — {c['stack']}")
            if ptype == "mixed":
                for ev in c["evidence"]:
                    print(f"      依据: {ev}")
    for c in clues:
        print(f"  线索: {c}")

    plan = build_and_run(repo, templates, project_name, has_frontend,
                         overwrite=args.overwrite, dry_run=args.dry_run)

    # 扫描填充（--no-scan 关闭；dry-run 只读扫描照跑、只记录计划）
    if args.no_scan:
        print("\n(--no-scan：跳过扫描填充，保留骨架 TODO)")
    else:
        apply_scan_fill(repo, templates, scan, plan, lang=args.lang,
                        project_name=project_name, dry_run=args.dry_run)

    print_report(plan, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
