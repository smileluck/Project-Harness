#!/usr/bin/env python3
"""init_project.py — 把 project-harness 模板骨架安装到任意目标仓库。

用法:
    python3 init_project.py <repo-path> [--project-name NAME] [--lang zh|en]
                            [--dry-run] [--overwrite]

行为概述:
    1. 校验 <repo-path> 的 git 根（嵌套仓库拒绝，非 git 仓库警告后继续）。
    2. 探测项目类型（fullstack / backend-only / frontend-only）与技术栈线索。
    3. 从 skills/project-harness/templates/<lang>/ 拷贝 aiDoc 骨架、AGENTS.md、
       CLAUDE.md、.agents/skills，并创建 notes/plans 生命周期目录；
       按项目类型跳过的文件会同步裁剪索引（aiDoc/README.md、AGENTS.md）中
       引用它们的行。
    4. 默认绝不覆盖已存在文件；--overwrite 会先备份到 aiDoc/.harness-backups/。
    5. 幂等：第二次运行全部 SKIP。

退出码: 0 成功；2 参数错误 / 嵌套 git 拒绝。
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_ROOT = SCRIPT_DIR.parent / "templates"

# 与模板布局对应的“按项目类型跳过”清单（相对 aidoc/ 根）。
# 若模板文件名调整，这里需要同步修改。
BACKEND_ONLY_SKIP = (
    "frontend-backend/frontend-rules.md",
    "frontend-backend/frontend-utils.md",
)
FRONTEND_ONLY_SKIP = (
    "modules/backend-layer-rules.md",
    "modules/module-development.md",
)

# 技术栈探测线索
BACKEND_MARKERS = (
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Cargo.toml",
)
FRONTEND_DEPS = (
    "vue", "react", "react-dom", "next", "nuxt", "@nuxt/core", "svelte",
    "@sveltejs/kit", "angular", "@angular/core", "solid-js", "@builder.io/qwik",
)
NODE_BACKEND_DEPS = (
    "express", "fastify", "koa", "@nestjs/core", "hapi", "@hapi/hapi",
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

def _scan_marker_files(repo: Path) -> list[str]:
    """返回根目录及一级子目录中发现的技术栈标志文件（相对路径）。"""
    found: list[str] = []
    candidates = [repo]
    try:
        for child in sorted(repo.iterdir()):
            if child.is_dir() and not child.name.startswith(".") \
                    and child.name not in ("node_modules", "vendor"):
                candidates.append(child)
    except OSError:
        pass
    markers = BACKEND_MARKERS + ("package.json",)
    for base in candidates:
        for name in markers:
            if (base / name).is_file():
                found.append(str((base / name).relative_to(repo)))
    return found


def _package_json_deps(pkg: Path) -> set[str]:
    import json

    try:
        data = json.loads(pkg.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    deps: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        section = data.get(key)
        if isinstance(section, dict):
            deps.update(section.keys())
    return deps


def detect_project(repo: Path) -> tuple[str, list[str]]:
    """返回 (项目类型, 线索说明列表)。类型 ∈ fullstack/backend-only/frontend-only。"""
    clues: list[str] = []
    has_frontend = False
    has_backend = False

    for rel in _scan_marker_files(repo):
        p = repo / rel
        if p.name == "package.json":
            deps = _package_json_deps(p)
            fe = sorted(d for d in deps if d in FRONTEND_DEPS)
            be = sorted(d for d in deps if d in NODE_BACKEND_DEPS)
            if fe:
                has_frontend = True
                clues.append(f"{rel}: 前端依赖 {', '.join(fe)}")
            if be:
                has_backend = True
                clues.append(f"{rel}: Node 后端依赖 {', '.join(be)}")
            if not fe and not be:
                # 无明确依赖线索的 package.json 视为 Node 项目（前后端皆有可能，偏后端）
                has_backend = True
                clues.append(f"{rel}: package.json（无明显前端依赖，按 Node 后端计）")
        else:
            has_backend = True
            clues.append(f"{rel}: 后端标志文件")

    if has_frontend and has_backend:
        ptype = "fullstack"
    elif has_frontend:
        ptype = "frontend-only"
    elif has_backend:
        ptype = "backend-only"
    else:
        ptype = "fullstack"
        clues.append("未发现任何技术栈标志文件，默认按 fullstack 处理（全量模板）")
    return ptype, clues


# ---------------------------------------------------------------- 拷贝计划

class Plan:
    def __init__(self) -> None:
        self.created: list[str] = []       # CREATE / APPEND
        self.skipped: list[str] = []       # 已存在，SKIP
        self.overwritten: list[str] = []   # BACKUP+OVERWRITE
        self.deferred: list[str] = []      # 因项目类型跳过
        self.backups: list[str] = []       # 备份目标路径


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
    if set(FRONTEND_ONLY_SKIP) <= skip_set:
        area_tokens = ("`modules/`", "`aiDoc/modules/`")

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


def build_and_run(repo: Path, templates: Path, project_name: str, ptype: str,
                  *, overwrite: bool, dry_run: bool) -> Plan:
    plan = Plan()
    today = date.today().isoformat()
    render_ctx = (project_name, today)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = repo / "aiDoc" / ".harness-backups" / timestamp

    if ptype == "backend-only":
        skip_set = set(BACKEND_ONLY_SKIP)
    elif ptype == "frontend-only":
        skip_set = set(FRONTEND_ONLY_SKIP)
    else:
        skip_set = set()

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
                    plan.deferred.append(f"aiDoc/{rel_str}  (项目类型 {ptype})")
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
        ("deferred [按项目类型跳过]", plan.deferred),
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

    # 项目探测
    ptype, clues = detect_project(repo)
    print("===== 项目探测 =====")
    print(f"仓库: {repo}")
    print(f"项目类型: {ptype}")
    for c in clues:
        print(f"  线索: {c}")

    plan = build_and_run(repo, templates, project_name, ptype,
                         overwrite=args.overwrite, dry_run=args.dry_run)
    print_report(plan, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
