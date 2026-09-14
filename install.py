#!/usr/bin/env python3
"""install.py — 把 skills/project-harness/ 安装到各 Agent 工具的 skills 发现路径。

用法:
    python3 install.py --tool agents|kimi|claude|codex|all
                       [--scope user|project] [--link] [--dry-run]
                       [--project-dir PATH] [--force] [--check]

目标路径:
    tool    user 级                                          project 级
    agents  ~/.agents/skills/project-harness                 .agents/skills/project-harness
    kimi    $KIMI_CODE_HOME/skills/project-harness           .kimi-code/skills/project-harness
            (默认 ~/.kimi-code/skills/project-harness)
    claude  ~/.claude/skills/project-harness                 .claude/skills/project-harness
    codex   ~/.codex/skills/project-harness                  不支持

默认 copy（覆盖前先删除旧安装）；--link 改为符号链接；--dry-run 只打印计划。
目标已存在且非本脚本安装的普通目录时，需要 --force 才覆盖。
版本判定：版本 = 源仓库 `git describe --tags --always --dirty`。copy 安装把
版本写入标识文件；已安装版本与源版本一致时 SKIP（不删重装），不同或缺失才
UPDATE。--link 恒指向源，视为最新。--check 只报告各目标版本不写入。

退出码: 0 成功（--check：全部最新）；1 有目标被拒绝/失败（--check：有旧版
或未安装）；2 参数错误。
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

sys.path.insert(0, str(SOURCE / "scripts"))
from harness_common import find_git_root, git_version  # noqa: E402

# 安装标识文件：copy 安装后写入，用于识别"本脚本安装的目录"
MARKER = ".installed-by-project-harness"


def installed_version(target: Path) -> str | None:
    """读取 copy 安装标识文件里的版本；非本脚本安装或无版本字段返回 None。"""
    try:
        for line in (target / MARKER).read_text(encoding="utf-8").splitlines():
            if line.startswith("version:"):
                return line.split(":", 1)[1].strip() or None
    except OSError:
        pass
    return None

TOOLS = ("agents", "kimi", "claude", "codex")

SKILL_USAGE_HINTS = {
    "agents": "在支持 .agents/skills 的工具中使用 project-harness skill（如 init 工作流）。",
    "kimi": "在 Kimi Code 中运行 /skill:project-harness init 初始化目标项目。",
    "claude": "在 Claude Code 中使用 project-harness skill（/project-harness 或对话中提及）。",
    "codex": "在 Codex 中使用 project-harness skill（skills 目录已就绪）。",
}




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
                force: bool, version: str = "unknown") -> tuple[bool, str]:
    """返回 (是否成功, 描述行)。"""
    mode = "link" if link else "copy"
    existed = target.exists() or target.is_symlink()

    if existed:
        if target.is_symlink():
            if target.resolve() == SOURCE.resolve():
                return True, f"[{tool}] SKIP (link 恒指向源，已是最新) {target}"
            action = "UPDATE"
        elif target.is_dir() and is_own_install(target):
            old = installed_version(target)
            if old is not None and old == version and version != "unknown":
                return True, f"[{tool}] SKIP (已是当前版本 {version}) {target}"
            action = f"UPDATE ({old or '未知版本'} -> {version})"
        elif force:
            action = "UPDATE(--force 覆盖非本脚本安装的目录)"
        else:
            return False, (f"[{tool}] 拒绝: {target} 已存在且非本脚本安装，"
                           "加 --force 才覆盖")
    else:
        action = f"INSTALL ({version})"

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
            f"source: {SOURCE}\nversion: {version}\n"
            f"installed: {datetime.now().isoformat()}\n",
            encoding="utf-8")
    return True, desc


def check_one(tool: str, target: Path, *, version: str) -> tuple[bool, str]:
    """--check：只报告目标版本状态，不写入。返回 (是否最新, 描述行)。"""
    if target.is_symlink():
        if target.resolve() == SOURCE.resolve():
            return True, f"[{tool}] 最新 (link -> {SOURCE}) {target}"
        return False, f"[{tool}] link 指向其他位置: {target} -> {target.resolve()}"
    if not target.is_dir():
        return False, f"[{tool}] 未安装: {target}"
    if not is_own_install(target):
        return False, f"[{tool}] 已存在但非本脚本安装: {target}"
    old = installed_version(target)
    if old is not None and old == version and version != "unknown":
        return True, f"[{tool}] 最新 ({version}) {target}"
    return False, f"[{tool}] 旧版 ({old or '未知版本'} -> {version}) {target}"


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
    parser.add_argument("--check", action="store_true",
                        help="只报告各目标已装版本 vs 源版本，不写入")
    args = parser.parse_args(argv)

    if not SOURCE.is_dir():
        print(f"错误: 源目录不存在: {SOURCE}", file=sys.stderr)
        return 2

    tools = list(TOOLS) if args.tool == "all" else [args.tool]
    project_dir = Path(args.project_dir).expanduser().resolve() \
        if args.project_dir else Path.cwd().resolve()
    version = git_version(REPO_ROOT)

    print(f"源: {SOURCE}")
    print(f"版本: {version}")

    if args.check:
        ok_all = True
        for tool in tools:
            try:
                target = user_target(tool) if args.scope == "user" \
                    else project_target(tool, project_dir)
            except ValueError as exc:
                if args.tool == "all":
                    print(f"[{tool}] 跳过: {exc}")
                    continue
                print(f"错误: {exc}", file=sys.stderr)
                return 2
            ok, desc = check_one(tool, target, version=version)
            print(desc)
            ok_all = ok_all and ok
        return 0 if ok_all else 1

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
                               dry_run=args.dry_run, force=args.force,
                               version=version)
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
