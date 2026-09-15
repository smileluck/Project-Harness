#!/usr/bin/env python3
"""update_harness.py — 把目标仓库的 harness 托管文件机械更新到当前模板版本。

用法:
    python3 update_harness.py <repo-path> [--dry-run] [--force] [--lang auto|zh|en]

判定依据：init_project.py 生成的 aiDoc/.harness-manifest.json（工具包版本 +
每个托管文件的 sha256 基线）。逐文件分类：

    当前哈希 == 基线   -> 项目未改过，刷新为「新模板渲染 + 裁剪 + 扫描填充」
                          的期望内容（先备份），不丢失 init 时的机械内容
    当前哈希 != 基线   -> 项目已改，跳过，交给 generate/sync 语义层合入
    文件已被项目删除   -> 不复活，从 manifest 移除
    模板侧已移除       -> 报告保留，首版不自动删项目文件

无 manifest 的旧仓库进入 adopt 模式：与期望内容比对（忽略 last-updated 行，
消除日期漂移），一致的登记基线；含 auto-scan 标记的扫描填充产物直接登记；
其余视为项目已改不登记——adopt 只建立基线。

版本相同且未 --force 时直接报告"已是最新"。code-index.md 是机器产物，
总是重新生成。

退出码: 0 成功；2 参数错误 / 前置条件不满足（嵌套 git、缺 AGENTS.md/aiDoc）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_ROOT = SCRIPT_DIR.parent / "templates"

try:
    import init_project
    import scan_repo
    from harness_common import detect_doc_lang, find_git_root
except ImportError:  # 被其他脚本 import 时兜底
    sys.path.insert(0, str(SCRIPT_DIR))
    import init_project
    import scan_repo
    from harness_common import detect_doc_lang, find_git_root

# 需要做裁剪模拟的索引文件（无前端项目剔除 frontend 引用行）
_PRUNE_SIM_RELS = ("AGENTS.md", "aiDoc/README.md")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized(text: str) -> str:
    """忽略 last-updated 行（{{DATE}} 渲染差异），用于 adopt 模式比对。"""
    return "\n".join(ln for ln in text.splitlines()
                     if "last-updated:" not in ln)


def _load_manifest(repo: Path) -> dict | None:
    f = repo / init_project.MANIFEST_REL
    if not f.is_file():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def iter_managed(templates: Path) -> list[tuple[str, str]]:
    """(仓库相对路径, 模板相对路径) 清单，与 init_project 的注入逻辑一致。"""
    out: list[tuple[str, str]] = []
    aidoc = templates / "aidoc"
    if aidoc.is_dir():
        for f in sorted(aidoc.rglob("*")):
            if not f.is_file():
                continue
            name = f.name
            if name.endswith(".tmpl"):
                name = name[:-len(".tmpl")]
            repo_rel = (Path("aiDoc") / f.parent.relative_to(aidoc) / name)
            out.append((repo_rel.as_posix(),
                        f.relative_to(templates).as_posix()))
    if (templates / "AGENTS.md.tmpl").is_file():
        out.append(("AGENTS.md", "AGENTS.md.tmpl"))
    if (templates / "CLAUDE.md").is_file():
        out.append(("CLAUDE.md", "CLAUDE.md"))
    skills = templates / "agents-skills"
    if skills.is_dir():
        for f in sorted(skills.rglob("*")):
            if f.is_file():
                out.append((".agents/skills/" + f.relative_to(skills).as_posix(),
                            f.relative_to(templates).as_posix()))
    return out


def _expected_content(src: Path, rel: str, render_ctx: dict,
                      fill_map: dict, skip_set: set[str]) -> str | None:
    """计算托管文件的期望内容：模板渲染 -> 扫描填充（relations）-> 引用裁剪。

    与 init_project 的产出管线一致；文件不可读返回 None。
    """
    try:
        text = init_project._render(src.read_text(encoding="utf-8"),
                                    render_ctx)
    except (OSError, UnicodeDecodeError):
        return None
    if rel in fill_map:
        text, _, _ = init_project._fill_sections(text, fill_map[rel])
    if skip_set and rel in _PRUNE_SIM_RELS:
        kept, _ = init_project._prune_lines(text.splitlines(), skip_set)
        text = "\n".join(kept) + "\n"
    return text


class UpdateReport:
    def __init__(self) -> None:
        self.refreshed: list[str] = []      # 未改过 -> 已刷新到期望内容
        self.unchanged: list[str] = []      # 未改过且内容已一致
        self.user_modified: list[str] = []  # 项目已改 -> 跳过
        self.removed_in_template: list[str] = []  # 模板已删 -> 项目文件保留
        self.deleted_by_user: list[str] = []      # 项目已删 -> 不复活

    def print(self) -> None:
        groups = (
            ("refreshed [已刷新]", self.refreshed),
            ("unchanged [内容已一致]", self.unchanged),
            ("user-modified [项目已改，跳过]", self.user_modified),
            ("removed-in-template [模板已移除，项目文件保留]",
             self.removed_in_template),
            ("deleted-by-user [项目已删除，不复活]", self.deleted_by_user),
        )
        for label, items in groups:
            print(f"\n-- {label}: {len(items)} 项")
            for it in items:
                print(f"   {it}")


def _write_with_backup(dst: Path, rel: str, new_text: str,
                       backup_root: Path, *, dry_run: bool) -> None:
    if dry_run:
        return
    backup = backup_root / rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dst, backup)
    dst.write_text(new_text, encoding="utf-8")


def adopt(repo: Path, templates_lang: Path, render_ctx: dict,
          backup_root: Path, *, fill_map: dict, skip_set: set[str],
          dry_run: bool) -> dict:
    """无 manifest 的旧仓库：建立基线。返回 manifest 的 files 字典。"""
    files: dict[str, dict] = {}
    adopted: list[str] = []
    user_modified: list[str] = []
    for rel, trel in iter_managed(templates_lang):
        if rel in skip_set or rel == init_project.CODE_INDEX_REL:
            continue
        dst = repo / rel
        src = templates_lang / trel
        if not dst.is_file() or not src.is_file():
            continue
        try:
            cur_text = dst.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        expected = _expected_content(src, rel, render_ctx, fill_map, skip_set)
        if init_project.AUTO_SCAN_MARK in cur_text:
            # init 扫描填充产物：机械事实由扫描再生成，直接登记当前内容为基线
            target_text = None
        elif expected is None or _normalized(cur_text) != _normalized(expected):
            user_modified.append(rel)
            continue
        else:
            # 仅 last-updated 等渲染差异时刷新到期望内容
            target_text = expected if cur_text != expected else None
        if target_text is not None:
            _write_with_backup(dst, rel, target_text, backup_root,
                               dry_run=dry_run)
        files[rel] = {"sha256": "dry-run" if dry_run else _sha256(dst),
                      "template": trel}
        adopted.append(rel)
    print(f"\n-- adopt 建立基线: {len(adopted)} 项")
    for it in adopted:
        print(f"   {it}")
    print(f"\n-- 项目已改，不登记（需人工或 generate/sync 合入）: "
          f"{len(user_modified)} 项")
    for it in user_modified:
        print(f"   {it}")
    return files


def main(argv: list[str] | None = None, *,
         templates_root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="把目标仓库的 harness 托管文件更新到当前模板版本。")
    parser.add_argument("repo_path", help="目标仓库根目录")
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印更新计划，不写文件")
    parser.add_argument("--force", action="store_true",
                        help="版本相同也逐文件重检（默认版本一致直接报已是最新）")
    parser.add_argument("--lang", choices=("auto", "zh", "en"), default=None,
                        help="模板语言（auto=探测仓库既有文档语言；默认取 "
                             "manifest 登记值；adopt 时默认 zh）")
    args = parser.parse_args(argv)

    repo = Path(args.repo_path).expanduser().resolve()
    if not repo.is_dir():
        print(f"错误: 路径不存在或不是目录: {repo}", file=sys.stderr)
        return 2
    git_root = find_git_root(repo)
    if git_root is None:
        print(f"警告: {repo} 不是 git 仓库，仍将继续。", file=sys.stderr)
    elif git_root != repo:
        print(f"错误: {repo} 是 git 仓库 {git_root} 的子目录。\n"
              f"请传仓库根目录: {git_root}", file=sys.stderr)
        return 2
    if not (repo / "AGENTS.md").is_file() or not (repo / "aiDoc").is_dir():
        print(f"错误: {repo} 缺 AGENTS.md 或 aiDoc/，请先运行 init_project.py。",
              file=sys.stderr)
        return 2

    version = init_project.harness_version()
    manifest = _load_manifest(repo)
    if args.lang == "auto":
        lang = detect_doc_lang(repo)
    else:
        lang = args.lang or (manifest or {}).get("lang") or "zh"
    templates_root = templates_root or TEMPLATES_ROOT
    templates_lang = templates_root / lang
    if not templates_lang.is_dir():
        print(f"错误: 模板目录不存在: {templates_lang}", file=sys.stderr)
        return 2

    today = date.today().isoformat()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = repo / "aiDoc" / ".harness-backups" / timestamp
    scan = scan_repo.scan_repo(repo)
    skip_set = set() if scan["has_frontend"] else set(init_project.FRONTEND_SKIP)

    print(f"仓库: {repo}")
    print(f"工具包版本: {version}  模板语言: {lang}"
          f"{'  (dry-run)' if args.dry_run else ''}")

    if manifest is None:
        # adopt 模式：首次仅建立基线
        print("未找到 manifest，进入 adopt 模式（建立基线）。")
        project_name = repo.name
        render_ctx = init_project.make_render_ctx(project_name, today)
        fill_map = dict(init_project._fill_specs(scan, lang, project_name))
        files = adopt(repo, templates_lang, render_ctx, backup_root,
                      fill_map=fill_map, skip_set=skip_set,
                      dry_run=args.dry_run)
        new_manifest = {"harness_version": version,
                        "project_name": project_name, "lang": lang,
                        "generated": today, "files": files}
    else:
        old_version = manifest.get("harness_version", "unknown")
        project_name = manifest.get("project_name") or repo.name
        print(f"产物版本: {old_version}")
        if old_version == version and version != "unknown" and not args.force:
            print("\n已是当前版本，无需更新（--force 可逐文件重检）。")
            return 0

        render_ctx = init_project.make_render_ctx(project_name, today)
        fill_map = dict(init_project._fill_specs(scan, lang, project_name))
        report = UpdateReport()
        new_files: dict[str, dict] = {}
        for rel, info in sorted(manifest.get("files", {}).items()):
            trel = info.get("template", "")
            src = templates_lang / trel
            dst = repo / rel
            if not src.is_file():
                report.removed_in_template.append(rel)
                new_files[rel] = info
                continue
            if not dst.is_file():
                report.deleted_by_user.append(rel)
                continue
            if _sha256(dst) != info.get("sha256"):
                report.user_modified.append(rel)
                new_files[rel] = info  # 保留旧基线，避免误刷项目改动
                continue
            expected = _expected_content(src, rel, render_ctx, fill_map,
                                         skip_set)
            if expected is None:
                report.user_modified.append(rel)
                new_files[rel] = info
                continue
            try:
                cur_text = dst.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                report.user_modified.append(rel)
                new_files[rel] = info
                continue
            if cur_text == expected:
                report.unchanged.append(rel)
            else:
                _write_with_backup(dst, rel, expected, backup_root,
                                   dry_run=args.dry_run)
                report.refreshed.append(rel)
            new_files[rel] = {"sha256": "dry-run" if args.dry_run
                              else _sha256(dst), "template": trel}
        report.print()
        new_manifest = {"harness_version": version,
                        "project_name": project_name, "lang": lang,
                        "generated": today, "files": new_files}

    # code-index.md：机器产物，总是重新生成
    if args.dry_run:
        print(f"\n-- {init_project.CODE_INDEX_REL}  (dry-run 计划重新生成)")
        print(f"-- {init_project.MANIFEST_REL}  (dry-run 计划更新)")
    else:
        (repo / init_project.CODE_INDEX_REL).write_text(
            scan_repo.render_code_index(scan, lang=lang, today=today),
            encoding="utf-8")
        (repo / init_project.MANIFEST_REL).write_text(
            json.dumps(new_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print(f"\n-- {init_project.CODE_INDEX_REL}  (已重新生成)")
        print(f"-- {init_project.MANIFEST_REL}  (已更新)")

    print("\n下一步:")
    print("  1. 「项目已改，跳过」的文件如需新模板规则，由 generate/sync "
          "工作流语义合入。")
    print("  2. 运行 python3 check_sync.py <repo> 校验一致性。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
