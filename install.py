#!/usr/bin/env python3
"""install.py — 把 skills/project-harness/ 安装到各 Agent 工具的 skills 发现路径。

用法:
    python3 install.py --tool agents|kimi|claude|codex|all
                       [--scope user|project] [--link] [--dry-run]
                       [--project-dir PATH] [--force]

目标路径:
    tool    user 级                                          project 级
    agents  ~/.agents/skills/project-harness                 .agents/skills/project-harness
    kimi    $KIMI_CODE_HOME/skills/project-harness           .kimi-code/skills/project-harness
            (默认 ~/.kimi-code/skills/project-harness)
    claude  ~/.claude/skills/project-harness                 .claude/skills/project-harness
    codex   ~/.codex/skills/project-harness                  不支持

默认 copy（覆盖前先删除旧安装）；--link 改为符号链接；--dry-run 只打印计划。
目标已存在且非本脚本安装的普通目录时，需要 --force 才覆盖。

退出码: 0 成功；1 有目标被拒绝/失败；2 参数错误。
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SOURCE = REPO_ROOT / "skills" / "project-harness"

# 安装标识文件：copy 安装后写入，用于识别"本脚本安装的目录"
MARKER = ".installed-by-project-harness"

TOOLS = ("agents", "kimi", "claude", "codex")

SKILL_USAGE_HINTS = {
    "agents": "在支持 .agents/skills 的工具中使用 project-harness skill（如 init 工作流）。",
    "kimi": "在 Kimi Code 中运行 /skill:project-harness init 初始化目标项目。",
    "claude": "在 Claude Code 中使用 project-harness skill（/project-harness 或对话中提及）。",
    "codex": "在 Codex 中使用 project-harness skill（skills 目录已就绪）。",
}


def find_git_root(path: Path) -> Path | None:
    for cand in (path, *path.parents):
        if (cand / ".git").exists():
            return cand
    return None


def user_target(tool: str) -> Path:
    home = Path.home()
    if tool == "agents":
        return home / ".agents" / "skills" / "project-harness"
    if tool == "kimi":
        base = Path(os.environ.get("KIMI_CODE_HOME") or home / ".kimi-code")
        return base.expanduser() / "skills" / "project-harness"
    if tool == "claude":
        return home / ".claude" / "skills" / "project-harness"
    if tool == "codex":
        return home / ".codex" / "skills" / "project-harness"
    raise ValueError(tool)


def project_target(tool: str, project_dir: Path) -> Path:
    if tool == "codex":
        raise ValueError("codex 不支持 project 级安装（无 project 级 skills 目录约定）")
    root = find_git_root(project_dir)
    if root is None:
        raise ValueError(f"未找到 git 根目录（从 {project_dir} 向上无 .git），"
                         "请用 --project-dir 指定仓库内路径")
    return root / f".{tool}" / "skills" / "project-harness"


def is_own_install(target: Path) -> bool:
    """判断目标是否为本脚本安装的（符号链接或含标识文件的目录）。"""
    if target.is_symlink():
        return True
    if target.is_dir():
        return (target / MARKER).is_file()
    return False


def install_one(tool: str, target: Path, *, link: bool, dry_run: bool,
                force: bool) -> tuple[bool, str]:
    """返回 (是否成功, 描述行)。"""
    mode = "link" if link else "copy"
    existed = target.exists() or target.is_symlink()

    if existed:
        if target.is_symlink() or (target.is_dir() and is_own_install(target)):
            action = "UPDATE"
        elif force:
            action = "UPDATE(--force 覆盖非本脚本安装的目录)"
        else:
            return False, (f"[{tool}] 拒绝: {target} 已存在且非本脚本安装，"
                           "加 --force 才覆盖")
    else:
        action = "INSTALL"

    desc = f"[{tool}] {action} ({mode}) {target}"
    if link:
        desc += f" -> {SOURCE}"
    if dry_run:
        return True, desc + "  [dry-run]"

    # 删除旧安装
    if existed:
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    if link:
        target.symlink_to(SOURCE, target_is_directory=True)
    else:
        shutil.copytree(SOURCE, target)
        marker = target / MARKER
        marker.write_text(
            f"source: {SOURCE}\ninstalled: {datetime.now().isoformat()}\n",
            encoding="utf-8")
    return True, desc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="把 project-harness skill 安装到各 Agent 工具的 skills 路径。")
    parser.add_argument("--tool", required=True,
                        choices=(*TOOLS, "all"), help="目标工具")
    parser.add_argument("--scope", choices=("user", "project"), default="user",
                        help="安装级别（默认 user）")
    parser.add_argument("--link", action="store_true",
                        help="用符号链接指向仓库内源目录（默认 copy）")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划")
    parser.add_argument("--project-dir", default=None,
                        help="project 级时的项目目录（默认 cwd，向上解析 git 根）")
    parser.add_argument("--force", action="store_true",
                        help="覆盖非本脚本安装的已存在目录")
    args = parser.parse_args(argv)

    if not SOURCE.is_dir():
        print(f"错误: 源目录不存在: {SOURCE}", file=sys.stderr)
        return 2

    tools = list(TOOLS) if args.tool == "all" else [args.tool]
    project_dir = Path(args.project_dir).expanduser().resolve() \
        if args.project_dir else Path.cwd().resolve()

    print(f"源: {SOURCE}")
    print(f"级别: {args.scope}  模式: {'link' if args.link else 'copy'}"
          f"{'  (dry-run)' if args.dry_run else ''}\n")

    ok_all = True
    installed_tools: list[str] = []
    for tool in tools:
        try:
            if args.scope == "user":
                target = user_target(tool)
            else:
                target = project_target(tool, project_dir)
        except ValueError as exc:
            if args.tool == "all":
                print(f"[{tool}] 跳过: {exc}")
                continue
            print(f"错误: {exc}", file=sys.stderr)
            return 2
        ok, desc = install_one(tool, target, link=args.link,
                               dry_run=args.dry_run, force=args.force)
        print(desc)
        if ok:
            installed_tools.append(tool)
        else:
            ok_all = False

    if installed_tools:
        print("\n===== 安装后用法 =====")
        for tool in installed_tools:
            print(f"  {SKILL_USAGE_HINTS[tool]}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
