#!/usr/bin/env python3
"""init_project_set.py — 项目集批量初始化（init-set）与索引刷新（update-set）。

用法:
    python3 init_project_set.py <set-root>            # discovery：只打印候选表，零写入
    python3 init_project_set.py <set-root> --members a,b,c [--lang auto|zh|en]
                                [--dry-run] [--overwrite] [--no-scan]
    python3 init_project_set.py <set-root> --all      # 全部候选都作为成员
    python3 init_project_set.py <set-root> --refresh [--lang auto|zh|en] [--dry-run]
                                                      # update-set：刷新根 AGENTS.md 成员索引

行为概述:
    1. 发现：枚举 <set-root> 下非隐藏一级子目录，标注机械事实——是否独立
       git 根、是否已配置 harness（aiDoc/.harness-manifest.json）、根下是否
       含已知清单文件；嵌套在父 git 仓库内且自身非 git 根的子目录标记
       blocked（init_project.py 会拒绝嵌套初始化）。
    2. 不带 --members/--all/--refresh 时为 discovery 模式：只打印候选表，不写文件。
    3. 批量模式：对确认的、未配置且未阻塞的成员，复用 init_project 的产出管线
       （build_and_run / apply_scan_fill / write_manifest）逐项目初始化；
       已配置成员一律跳过；单成员失败不中断整批。
    4. 收尾在项目集根写 AGENTS.md（模板 templates/<lang>/project-set/
       AGENTS.md.tmpl），用 scan-fill:members 标记填入成员索引表（5 列：项目/
       路径/类型/简介/harness 状态）；已存在则 SKIP，--overwrite 先备份到
       <set-root>/.harness-backups/。不写根级 manifest、不建根级 aiDoc/。
    5. --refresh 模式（update-set）：只重写根 AGENTS.md 成员索引表——目录已
       删的成员删行、新目录追加行（简介 TODO 占位）、存续成员保留已校订简介
       仅机械刷新 harness 状态列；兼容旧版 4 列表迁移。有变化才写（先备份），
       无变化零写入。绝不触碰任何成员目录。
    6. 幂等：二次运行成员全部「已配置跳过」、根 AGENTS.md SKIP；--refresh
       二次运行输出「已是最新」。

退出码: 0 成功（含全部成员被跳过/索引已是最新）；1 有成员初始化失败；
        2 参数错误/路径不存在/refresh 前置不满足（缺根 AGENTS.md 或 scan-fill 标记）。
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_ROOT = SCRIPT_DIR.parent / "templates"

try:
    import scan_repo
    import init_project
    from harness_common import find_git_root, detect_doc_lang
except ImportError:  # 被打包移动后兜底
    sys.path.insert(0, str(SCRIPT_DIR))
    import scan_repo
    import init_project
    from harness_common import find_git_root, detect_doc_lang

SET_AGENTS_TMPL = Path("project-set") / "AGENTS.md.tmpl"
HARNESS_MANIFEST_REL = "aiDoc/.harness-manifest.json"
ROOT_AGENTS_REL = "AGENTS.md"
MEMBERS_FILL_KEY = "members"


# ---------------------------------------------------------------- 发现

def discover_members(set_root: Path) -> list[dict]:
    """枚举非隐藏一级子目录，返回候选成员清单（按名字排序）。

    每项: {name, path, is_git_root, has_harness, manifests, blocked}。
    blocked = 处于某个 git 仓库内但自身不是 git 根（init 会拒绝嵌套初始化）。
    """
    manifest_names = sorted(name for name, _ in scan_repo.MANIFEST_PARSERS)
    members = []
    for d in sorted(set_root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        git_root = find_git_root(d)
        members.append({
            "name": d.name,
            "path": d,
            "is_git_root": git_root == d,
            "has_harness": (d / HARNESS_MANIFEST_REL).is_file(),
            "manifests": [n for n in manifest_names if (d / n).is_file()],
            "blocked": git_root is not None and git_root != d,
        })
    return members


def print_candidates(set_root: Path, members: list[dict]) -> None:
    print("===== 项目集候选成员 =====")
    print(f"项目集根: {set_root}")
    if not members:
        print("（无非隐藏一级子目录）")
        return
    print(f"{'目录':<24} {'git根':<6} {'harness':<8} {'阻塞':<6} 清单文件")
    for m in members:
        mans = ", ".join(m["manifests"]) if m["manifests"] else "-"
        print(f"{m['name']:<24} {'是' if m['is_git_root'] else '否':<6} "
              f"{'已配置' if m['has_harness'] else '未配置':<8} "
              f"{'是' if m['blocked'] else '否':<6} {mans}")
    print("\n下一步: 与使用者确认成员清单后，用 --members <名,字,逗,号> "
          "或 --all 正式执行（先 --dry-run 预览）；已有根 AGENTS.md 的项目集"
          "用 --refresh 刷新成员索引。")


# ---------------------------------------------------------------- 成员初始化

def init_one_member(member: dict, templates: Path, *, lang: str,
                    overwrite: bool, dry_run: bool, no_scan: bool) -> dict:
    """对单个成员跑 init_project 产出管线，返回 {status, plan|error}。

    status ∈ initialized / skipped-configured / blocked / failed。
    """
    if member["has_harness"]:
        return {"status": "skipped-configured"}
    if member["blocked"]:
        return {"status": "blocked"}
    path = member["path"]
    try:
        scan = scan_repo.scan_repo(path)
        plan = init_project.build_and_run(
            path, templates, member["name"], scan["has_frontend"],
            overwrite=overwrite, dry_run=dry_run)
        if not no_scan:
            init_project.apply_scan_fill(
                path, templates, scan, plan,
                lang=lang, project_name=member["name"], dry_run=dry_run)
        init_project.write_manifest(
            path, templates, plan,
            version=init_project.harness_version(),
            project_name=member["name"], lang=lang, dry_run=dry_run)
        _name, desc = init_project._primary_identity(scan, member["name"])
        return {"status": "initialized", "plan": plan,
                "label": scan["label"],
                "desc": _sanitize_cell(desc) if desc else None}
    except Exception as exc:  # 单成员失败不中断整批
        return {"status": "failed", "error": f"{exc.__class__.__name__}: {exc}"}


def _plan_counts(plan) -> str:
    return (f"created {len(plan.created)} / skipped {len(plan.skipped)} / "
            f"auto-filled {len(plan.auto_filled)} / "
            f"overwritten {len(plan.overwritten)} / "
            f"deferred {len(plan.deferred)}")


# ---------------------------------------------------------------- 根 AGENTS.md

def _todo_desc(lang: str) -> str:
    return "TODO: 一句话说明" if lang == "zh" else "TODO: one-line role summary"


def _status_text(has_harness: bool, lang: str) -> str:
    if lang == "zh":
        return "已配置" if has_harness else "未配置"
    return "configured" if has_harness else "not configured"


def _sanitize_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _scan_identity(member: dict, lang: str) -> tuple[str, str]:
    """只读扫描取 (类型 label, 简介)。blocked 成员不扫（git 命令会误入父仓库）。"""
    unknown = "未知" if lang == "zh" else "unknown"
    if member["blocked"]:
        return unknown, _todo_desc(lang)
    try:
        scan = scan_repo.scan_repo(member["path"])
    except Exception:
        return unknown, _todo_desc(lang)
    _name, desc = init_project._primary_identity(scan, member["name"])
    return scan["label"], (_sanitize_cell(desc) if desc else _todo_desc(lang))


def _member_rows(results: list[dict], lang: str) -> list[str]:
    zh = lang == "zh"
    status_disp = {
        "initialized": ("本次初始化", "initialized this run"),
        "skipped-configured": ("已配置（跳过）", "already configured (skipped)"),
        "blocked": ("阻塞：嵌套于父 git 仓库", "blocked: nested in parent git repo"),
        "failed": ("初始化失败", "init failed"),
    }
    rows = ["| 项目 | 路径 | 类型 | 简介 | harness 状态 |" if zh else
            "| Project | Path | Type | Summary | Harness status |",
            "|---|---|---|---|---|"]
    for r in results:
        m = r["member"]
        label = r.get("label") or ("未知" if zh else "unknown")
        desc = r.get("desc") or _todo_desc(lang)
        status = status_disp[r["status"]][0 if zh else 1]
        rows.append(f"| **{m['name']}** | `{m['name']}/` | {label} "
                    f"| {desc} | {status} |")
    return rows


def write_root_agents(set_root: Path, templates: Path, results: list[dict], *,
                      lang: str, overwrite: bool, dry_run: bool) -> str:
    """渲染项目集根 AGENTS.md 并填入成员索引表，返回状态字符串。"""
    src = templates / SET_AGENTS_TMPL
    if not src.is_file():
        return f"{ROOT_AGENTS_REL}  (模板缺失: {src}，跳过)"
    today = date.today().isoformat()
    ctx = init_project.make_render_ctx(set_root.name, today)
    text = init_project._render(src.read_text(encoding="utf-8"), ctx)
    text, done, missing = init_project._fill_sections(
        text, [(MEMBERS_FILL_KEY, _member_rows(results, lang))])
    if missing:
        return (f"{ROOT_AGENTS_REL}  (scan-fill 标记未找到: "
                f"{','.join(missing)}，跳过)")
    plan = init_project.Plan()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = set_root / ".harness-backups" / timestamp
    if not init_project._prep_dst(set_root / ROOT_AGENTS_REL, set_root, plan,
                                  overwrite=overwrite, dry_run=dry_run,
                                  backup_root=backup_root):
        if plan.skipped:
            return f"{ROOT_AGENTS_REL}  (已存在，SKIP)"
        if plan.overwritten:
            return f"{ROOT_AGENTS_REL}  (dry-run 计划覆盖，含备份)"
        return f"{ROOT_AGENTS_REL}  (dry-run 计划创建)"
    (set_root / ROOT_AGENTS_REL).write_text(text, encoding="utf-8")
    tag = "dry-run 计划创建" if dry_run else ("已覆盖(含备份)" if plan.overwritten
                                             else "已创建")
    return f"{ROOT_AGENTS_REL}  ({tag}，成员索引表已填充)"


# ---------------------------------------------------------------- refresh（update-set）

LAST_UPDATED_RE = re.compile(r"^<!-- last-updated: [0-9-]+ -->")


def _parse_member_table(lines: list[str], i: int, j: int) -> list[list[str]]:
    """解析 scan-fill:members 小节（lines[i+1:j]）内的成员表行，返回 cells 列表。"""
    rows = []
    for ln in lines[i + 1:j]:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue  # 分隔行
        if cells[0].strip("*") in ("项目", "Project"):
            continue  # 表头
        rows.append(cells)
    return rows


def _refresh_body(existing: list[list[str]], members: list[dict],
                  lang: str) -> tuple[list[str], dict[str, list[str]]]:
    """三方合并成员表：保留存续行（简介/类型原样，机械刷新状态列）、
    删消失行、追加新行。返回 (新表 body 行, 分类报告)。"""
    zh = lang == "zh"
    todo = _todo_desc(lang)
    by_name = {m["name"]: m for m in members}
    report: dict[str, list[str]] = {"added": [], "removed": [],
                                    "status-refreshed": [], "unchanged": []}
    kept: list[list[str]] = []
    for cells in existing:
        name = cells[0].strip("*")
        if name not in by_name:
            report["removed"].append(name)
            continue
        if len(cells) == 4:  # 旧版 4 列表迁移为 5 列
            cells = [cells[0], cells[1], cells[2], todo, cells[3]]
        new_status = _status_text(by_name[name]["has_harness"], lang)
        if cells[4] != new_status:
            cells[4] = new_status
            report["status-refreshed"].append(name)
        else:
            report["unchanged"].append(name)
        kept.append(cells)
    existing_names = {c[0].strip("*") for c in existing}
    for name in sorted(by_name):
        if name in existing_names:
            continue
        m = by_name[name]
        label, desc = _scan_identity(m, lang)
        kept.append([f"**{name}**", f"`{name}/`", label, desc,
                     _status_text(m["has_harness"], lang)])
        report["added"].append(name)
    body = ["| 项目 | 路径 | 类型 | 简介 | harness 状态 |" if zh else
            "| Project | Path | Type | Summary | Harness status |",
            "|---|---|---|---|---|"]
    body += ["| " + " | ".join(c) + " |" for c in kept]
    return body, report


def refresh_root_agents(set_root: Path, *, lang: str, dry_run: bool) -> int:
    """update-set：只重写根 AGENTS.md 的成员索引表，绝不触碰成员目录。"""
    root = set_root / ROOT_AGENTS_REL
    if not root.is_file():
        print("错误: 项目集根无 AGENTS.md，请先运行 init-set 生成。",
              file=sys.stderr)
        return 2
    try:
        text = root.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"错误: 根 AGENTS.md 不可按 utf-8 读取: {exc}", file=sys.stderr)
        return 2
    lines = text.splitlines()
    found = init_project._find_section(lines, MEMBERS_FILL_KEY)
    if found is None:
        print(f"错误: 根 AGENTS.md 缺少 "
              f"<!-- scan-fill:{MEMBERS_FILL_KEY} --> 标记，无法机械刷新。\n"
              "若校订时删掉了标记，请在小节标题行后补回该标记，或手工维护表格。",
              file=sys.stderr)
        return 2
    existing = _parse_member_table(lines, found[0], found[1])
    body, report = _refresh_body(existing, discover_members(set_root), lang)
    new_text, _done, _missing = init_project._fill_sections(
        text, [(MEMBERS_FILL_KEY, body)])
    if init_project.AUTO_SCAN_MARK not in text:
        # 校订时已移除 auto-scan 标记的，刷新不重新引入
        new_text = "\n".join(
            ln for ln in new_text.splitlines()
            if ln.strip() != init_project.AUTO_SCAN_MARK) + "\n"

    def _strip_date(t: str) -> list[str]:
        return [ln for ln in t.splitlines() if not LAST_UPDATED_RE.match(ln)]

    if _strip_date(new_text) == _strip_date(text):
        print("成员索引已是最新，零写入。")
        return 0
    new_text = LAST_UPDATED_RE.sub(
        f"<!-- last-updated: {date.today().isoformat()} -->", new_text,
        count=1)

    title = "索引刷新计划（dry-run，未写入任何文件）" if dry_run else "索引刷新结果"
    print(f"\n===== 项目集{title} =====")
    for label, key in (("added [新增成员行]", "added"),
                       ("removed [目录已不存在，删行]", "removed"),
                       ("status-refreshed [harness 状态列刷新]",
                        "status-refreshed"),
                       ("unchanged [存续不变]", "unchanged")):
        items = report[key]
        print(f"-- {label}: {len(items)} 项"
              + (f"  ({', '.join(items)})" if items and key != "unchanged"
                 else ""))
    if dry_run:
        return 0
    backup = (set_root / ".harness-backups"
              / datetime.now().strftime("%Y%m%d-%H%M%S") / ROOT_AGENTS_REL)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root, backup)
    root.write_text(new_text, encoding="utf-8")
    print(f"\n根 AGENTS.md 已重写（备份 -> {backup.relative_to(set_root)}）")
    newcomers = [n for n in report["added"]
                 if not (set_root / n / HARNESS_MANIFEST_REL).is_file()]
    if newcomers:
        print("提示: 新增未配置成员如需初始化，可运行 init-set：")
        print(f"  --members {','.join(newcomers)}")
    return 0


# ---------------------------------------------------------------- 报告

def print_set_report(results: list[dict], root_status: str, *,
                     dry_run: bool) -> None:
    title = "执行计划（dry-run，未写入任何文件）" if dry_run else "执行结果"
    print(f"\n===== 项目集{title} =====")
    groups = (
        ("initialized [本次初始化]", [r for r in results
                                    if r["status"] == "initialized"]),
        ("skipped-configured [已配置，跳过]", [r for r in results
                                             if r["status"] == "skipped-configured"]),
        ("blocked [嵌套 git，跳过]", [r for r in results
                                    if r["status"] == "blocked"]),
        ("failed [初始化失败]", [r for r in results if r["status"] == "failed"]),
    )
    for label, items in groups:
        print(f"\n-- {label}: {len(items)} 项")
        for r in items:
            line = f"   {r['member']['name']}"
            if "plan" in r:
                line += f"  ({_plan_counts(r['plan'])})"
            if "error" in r:
                line += f"  ({r['error']})"
            print(line)
    print(f"\n项目集根: {root_status}")
    print("\n下一步:")
    print("  1. 对每个本次初始化的成员，在 Agent 工具中以其项目根为目标运行")
    print("     project-harness 的 generate 工作流，填充 aiDoc/ 各区域内容。")
    print("  2. 校订项目集根 AGENTS.md：撰写「项目间关系与协作」小节，")
    print("     确认成员索引表后移除 auto-scan 标记。")


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="项目集批量初始化：发现成员项目、对未配置成员执行 init、"
                    "生成项目集根 AGENTS.md。")
    parser.add_argument("set_root", help="项目集根目录")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--members", default=None,
                       help="确认的成员目录名，逗号分隔（不带则只打印候选表）")
    group.add_argument("--all", action="store_true",
                       help="全部候选目录都作为成员")
    group.add_argument("--refresh", action="store_true",
                       help="update-set 模式：只刷新根 AGENTS.md 成员索引表"
                            "（增删成员行、刷新 harness 状态列），不动成员目录")
    parser.add_argument("--lang", choices=("auto", "zh", "en"), default="auto",
                        help="模板语言（auto=探测项目集根既有文档语言，回退 zh）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印计划，不写文件")
    parser.add_argument("--overwrite", action="store_true",
                        help="覆盖已存在文件（成员内经 init_project 备份；根 "
                             "AGENTS.md 备份到 <set-root>/.harness-backups/）")
    parser.add_argument("--no-scan", action="store_true",
                        help="关闭成员扫描填充（保留骨架 TODO，不生成各成员 "
                             "code-index.md）")
    args = parser.parse_args(argv)

    set_root = Path(args.set_root).expanduser().resolve()
    if not set_root.is_dir():
        print(f"错误: 路径不存在或不是目录: {set_root}", file=sys.stderr)
        return 2

    members = discover_members(set_root)
    if args.members is None and not args.all and not args.refresh:
        print_candidates(set_root, members)
        return 0

    lang = args.lang if args.lang != "auto" else detect_doc_lang(set_root)

    if args.refresh:
        print("===== 项目集索引刷新（update-set） =====")
        print(f"项目集根: {set_root}")
        print(f"文档语言: {args.lang}"
              + (f"（探测为 {lang}）" if args.lang == "auto" else ""))
        return refresh_root_agents(set_root, lang=lang, dry_run=args.dry_run)

    if args.all:
        selected = members
    else:
        by_name = {m["name"]: m for m in members}
        unknown = [n for n in args.members.split(",") if n not in by_name]
        if unknown:
            print(f"错误: 未知成员目录: {', '.join(unknown)}\n"
                  f"候选: {', '.join(sorted(by_name)) or '（无）'}",
                  file=sys.stderr)
            return 2
        selected = [by_name[n] for n in args.members.split(",")]

    templates = TEMPLATES_ROOT / lang
    if not templates.is_dir():
        print(f"错误: 模板目录不存在: {templates}", file=sys.stderr)
        return 2

    print("===== 项目集初始化 =====")
    print(f"项目集根: {set_root}")
    print(f"文档语言: {args.lang}"
          + (f"（探测为 {lang}）" if args.lang == "auto" else ""))
    print(f"成员: {', '.join(m['name'] for m in selected) or '（无）'}")
    if args.no_scan:
        print("(--no-scan：成员扫描填充关闭，保留骨架 TODO)")

    results = []
    for m in selected:
        print(f"\n--- 成员: {m['name']} ---")
        r = init_one_member(m, templates, lang=lang, overwrite=args.overwrite,
                            dry_run=args.dry_run, no_scan=args.no_scan)
        r["member"] = m
        if "label" not in r and not args.no_scan:
            # 跳过/失败的成员也只读扫描一次，让根表有真实类型与简介
            r["label"], r["desc"] = _scan_identity(m, lang)
        results.append(r)
        if r["status"] == "initialized":
            print(f"类型: {r['label']}；{_plan_counts(r['plan'])}")
        elif r["status"] == "failed":
            print(f"失败: {r['error']}", file=sys.stderr)
        else:
            print({"skipped-configured": "已配置 harness，跳过",
                   "blocked": "嵌套于父 git 仓库且自身非 git 根，跳过"}
                  [r["status"]])

    root_status = write_root_agents(set_root, templates, results, lang=lang,
                                    overwrite=args.overwrite,
                                    dry_run=args.dry_run)
    print_set_report(results, root_status, dry_run=args.dry_run)
    return 1 if any(r["status"] == "failed" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
