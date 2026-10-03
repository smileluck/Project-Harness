#!/usr/bin/env python3
"""init_project_set.py — 项目集批量初始化：一个根目录下的多个独立项目一次处理。

用法:
    python3 init_project_set.py <set-root>            # discovery：只打印候选表，零写入
    python3 init_project_set.py <set-root> --members a,b,c [--lang auto|zh|en]
                                [--dry-run] [--overwrite] [--no-scan]
    python3 init_project_set.py <set-root> --all      # 全部候选都作为成员

行为概述:
    1. 发现：枚举 <set-root> 下非隐藏一级子目录，标注机械事实——是否独立
       git 根、是否已配置 harness（aiDoc/.harness-manifest.json）、根下是否
       含已知清单文件；嵌套在父 git 仓库内且自身非 git 根的子目录标记
       blocked（init_project.py 会拒绝嵌套初始化）。
    2. 不带 --members/--all 时为 discovery 模式：只打印候选表，不写任何文件。
    3. 批量模式：对确认的、未配置且未阻塞的成员，复用 init_project 的产出管线
       （build_and_run / apply_scan_fill / write_manifest）逐项目初始化；
       已配置成员一律跳过；单成员失败不中断整批。
    4. 收尾在项目集根写 AGENTS.md（模板 templates/<lang>/project-set/
       AGENTS.md.tmpl），用 scan-fill:members 标记填入成员索引表；已存在则
       SKIP，--overwrite 先备份到 <set-root>/.harness-backups/。不写根级
       manifest、不建根级 aiDoc/。
    5. 幂等：二次运行成员全部「已配置跳过」，根 AGENTS.md SKIP。

退出码: 0 成功（含全部成员被跳过）；1 有成员初始化失败；2 参数错误/路径不存在。
"""

from __future__ import annotations

import argparse
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
          "或 --all 正式执行（先 --dry-run 预览）。")


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
        return {"status": "initialized", "plan": plan,
                "label": scan["label"]}
    except Exception as exc:  # 单成员失败不中断整批
        return {"status": "failed", "error": f"{exc.__class__.__name__}: {exc}"}


def _plan_counts(plan) -> str:
    return (f"created {len(plan.created)} / skipped {len(plan.skipped)} / "
            f"auto-filled {len(plan.auto_filled)} / "
            f"overwritten {len(plan.overwritten)} / "
            f"deferred {len(plan.deferred)}")


# ---------------------------------------------------------------- 根 AGENTS.md

def _member_rows(results: list[dict], lang: str) -> list[str]:
    zh = lang == "zh"
    status_disp = {
        "initialized": ("本次初始化", "initialized this run"),
        "skipped-configured": ("已配置（跳过）", "already configured (skipped)"),
        "blocked": ("阻塞：嵌套于父 git 仓库", "blocked: nested in parent git repo"),
        "failed": ("初始化失败", "init failed"),
    }
    rows = ["| 项目 | 路径 | 类型 | harness 状态 |" if zh else
            "| Project | Path | Type | Harness status |",
            "|---|---|---|---|"]
    for r in results:
        m = r["member"]
        label = r.get("label") or ("未知" if zh else "unknown")
        status = status_disp[r["status"]][0 if zh else 1]
        rows.append(f"| **{m['name']}** | `{m['name']}/` | {label} | {status} |")
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
    if args.members is None and not args.all:
        print_candidates(set_root, members)
        return 0

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

    lang = args.lang if args.lang != "auto" else detect_doc_lang(set_root)
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
