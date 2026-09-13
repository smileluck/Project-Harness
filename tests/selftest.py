#!/usr/bin/env python3
"""selftest.py — project-harness 工具包自检（零依赖，stdlib only）。

用法:
    python3 tests/selftest.py

覆盖:
    1. init 行为：tmp fixture（python-cli / fullstack / mixed）首跑创建、
       二跑幂等全 SKIP、--dry-run 零写入、嵌套 git 拒绝、--overwrite 有备份。
    2. init 产物跑 check_sync.py 必须 exit 0。
    3. scan_repo.py --json 可运行且输出合法 JSON；--write-code-index 重生成/
       幂等/双语渲染（code-index 漂移修复路径）；关键词表单源化后的
       Rust axum/clap 探测。
    4. lessons 机械闸门：pending≥2 未处理 / promoted 缺 target → exit 1；
       deferred、promoted 有 target、缺 lesson-meta 标记（仅提示）→ exit 0。
    5. zh/en 模板镜像：文件清单一致 + 占位符计数一致 + 标题层级序列一致；
       本仓 .agents/skills == zh 模板渲染实例（逐字节）。
    6. aiDoc↔模板固定样板一致性（剥离首行后逐字节相等）。
    7. 耦合校验：FRONTEND_SKIP 文件存在；AIDOC_SECTIONS == 模板子目录；
       auto-scan 标记全文仅正典 init-harness.md 一处；冲突优先级链/
       lesson-meta 标记/--write-code-index 命令仅正典一处；generate-aidoc.md
       不复制关键词表；scan-fill 标记 zh/en 模板逐字各一次。

退出码: 0 全过；1 有失败。
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "project-harness"
SCRIPTS = SKILL_DIR / "scripts"
TEMPLATES = SKILL_DIR / "templates"
REFERENCES = SKILL_DIR / "references"

sys.path.insert(0, str(SCRIPTS))
import check_sync  # noqa: E402
import init_project  # noqa: E402

PY = sys.executable

PLACEHOLDERS = ("{{PROJECT_NAME}}", "{{DATE}}", "<harness>", "<skill-dir>")

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail and not ok else ""))
    if not ok:
        FAILURES.append(name)


def run_init(repo: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, str(SCRIPTS / "init_project.py"), str(repo), *extra],
        capture_output=True, text=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(base: Path, kind: str) -> Path:
    repo = base / kind
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    if kind == "python-cli":
        write(repo / "pyproject.toml",
              '[project]\nname = "demo-cli"\ndescription = "demo"\n'
              '[project.scripts]\ndemo = "demo:main"\n')
        write(repo / "demo.py", "def main():\n    pass\n")
    elif kind == "fullstack":
        write(repo / "package.json",
              '{"name": "demo-web", "dependencies": {"react": "*", "express": "*"}}')
        write(repo / "src" / "App.tsx", "export default function App() { return null }\n")
        write(repo / "server" / "index.js",
              "require('express')().listen(3000)\n")
    elif kind == "mixed":
        write(repo / "go.mod", "module example.com/demo\n\ngo 1.22\n")
        write(repo / "web" / "package.json", '{"name": "demo-fe"}\n')
        write(repo / "web" / "src" / "main.ts", "console.log(1)\n")
    return repo


def snapshot_files(repo: Path) -> dict[str, str]:
    return {str(p.relative_to(repo)): p.read_bytes().hex()
            for p in sorted(repo.rglob("*")) if p.is_file() and ".git" not in p.parts}


# ---------------------------------------------------------------- 1. init 行为

def test_init_behaviour(tmp: Path) -> None:
    print("\n[1] init 行为")
    for kind in ("python-cli", "fullstack", "mixed"):
        repo = make_fixture(tmp / "run1", kind)
        r = run_init(repo)
        check(f"{kind} 首跑 exit 0", r.returncode == 0, r.stderr[-300:])
        check(f"{kind} 首跑有 CREATE", "CREATE" in r.stdout or "已创建" in r.stdout)

        r2 = run_init(repo)
        check(f"{kind} 二跑幂等 exit 0", r2.returncode == 0, r2.stderr[-300:])
        created_again = "已创建: 0 项" in r2.stdout or "created [已创建]: 0 项" in r2.stdout
        check(f"{kind} 二跑零新建", created_again)

        r3 = run_init(repo, "--dry-run")
        check(f"{kind} --dry-run exit 0", r3.returncode == 0, r3.stderr[-300:])

        r4 = subprocess.run(
            [PY, str(SCRIPTS / "check_sync.py"), str(repo)],
            capture_output=True, text=True)
        check(f"{kind} 产物 check_sync 全过", r4.returncode == 0,
              (r4.stdout + r4.stderr)[-300:])

    # dry-run 零写入
    repo = make_fixture(tmp / "dry", "python-cli")
    before = snapshot_files(repo)
    r = run_init(repo, "--dry-run")
    check("dry-run 零写入", r.returncode == 0 and snapshot_files(repo) == before)

    # 嵌套 git 拒绝：目标是某 git 仓库的子目录（自身无 .git）
    repo = make_fixture(tmp / "nested", "python-cli")
    inner = repo / "sub"
    inner.mkdir()
    r = run_init(inner)
    check("嵌套 git 拒绝(exit 2)", r.returncode == 2)

    # --overwrite 有备份
    repo = make_fixture(tmp / "ovr", "python-cli")
    run_init(repo)
    write(repo / "AGENTS.md", "# 用户改过\n")
    r = run_init(repo, "--overwrite")
    backups = list((repo / "aiDoc" / ".harness-backups").rglob("AGENTS.md"))
    check("--overwrite 产生备份", r.returncode == 0 and len(backups) == 1)
    check("--overwrite 备份保留用户内容",
          bool(backups) and "用户改过" in backups[0].read_text(encoding="utf-8"))

    # 占位符渲染：<harness>/<skill-dir> 无残留且路径真实
    repo = make_fixture(tmp / "render", "fullstack")
    run_init(repo)
    leftovers = []
    for p in list(repo.rglob("*.md")) + list(repo.rglob("*.tmpl")):
        if ".git" in p.parts:
            continue
        text = p.read_text(encoding="utf-8")
        for ph in ("<harness>", "<skill-dir>", "{{PROJECT_NAME}}", "{{DATE}}"):
            if ph in text:
                leftovers.append(f"{p.relative_to(repo)}: {ph}")
    check("产物无占位符残留", not leftovers, "; ".join(leftovers[:3]))
    skill_md = repo / ".agents" / "skills" / "project-pre-push-checks" / "SKILL.md"
    if skill_md.is_file():
        for line in skill_md.read_text(encoding="utf-8").splitlines():
            if "check_sync.py" in line and line.strip().startswith("python3"):
                script = line.strip().split()[1]
                check("pre-push skill 中 check_sync 路径真实存在",
                      Path(script).is_file(), script)


# ---------------------------------------------------------------- 2/3. 脚本可运行

def test_scan_framework_keywords(tmp: Path) -> None:
    print("\n[2c] 框架关键词表（单源化后机械探测能力）")
    repo = tmp / "kw"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    write(repo / "Cargo.toml",
          '[dependencies]\naxum = "0.7"\n'
          'clap = { version = "4", features = ["derive"] }\n')
    write(repo / "src" / "main.rs", "fn main() {}\n")
    r = subprocess.run([PY, str(SCRIPTS / "scan_repo.py"), str(repo), "--json"],
                       capture_output=True, text=True)
    ok = r.returncode == 0
    if ok:
        data = json.loads(r.stdout)
        found = {(c["kind"], c["stack"]) for c in data["components"]}
        ok = (any(k == "web-backend" and "Axum" in s for k, s in found)
              and any(k == "cli" and "Clap" in s for k, s in found))
    check("Rust axum/clap 依赖可探测", ok, r.stdout[-200:])


def test_scripts_runnable(tmp: Path) -> None:
    print("\n[2] scan_repo.py --json")
    repo = make_fixture(tmp / "scan", "fullstack")
    r = subprocess.run([PY, str(SCRIPTS / "scan_repo.py"), str(repo), "--json"],
                       capture_output=True, text=True)
    ok = r.returncode == 0
    if ok:
        try:
            data = json.loads(r.stdout)
            ok = "components" in data and "label" in data
        except json.JSONDecodeError:
            ok = False
    check("scan_repo --json 输出合法", ok, r.stderr[-300:])


def test_write_code_index(tmp: Path) -> None:
    print("\n[2b] scan_repo.py --write-code-index（code-index 修复路径）")
    repo = make_fixture(tmp / "writeci", "python-cli")
    run_init(repo)
    ci = repo / "aiDoc" / "relations" / "code-index.md"
    check("init 后 code-index 存在", ci.is_file())

    ci.write_text("<!-- 手改导致漂移的旧内容 -->\n", encoding="utf-8")
    r = subprocess.run([PY, str(SCRIPTS / "scan_repo.py"), str(repo),
                        "--write-code-index"], capture_output=True, text=True)
    text = ci.read_text(encoding="utf-8") if ci.is_file() else ""
    ok = (r.returncode == 0
          and text.startswith("<!-- auto-generated by scan_repo.py")
          and "已重新生成" in r.stdout)
    check("--write-code-index 重生成机器产物", ok, (r.stdout + r.stderr)[-300:])

    r2 = subprocess.run([PY, str(SCRIPTS / "scan_repo.py"), str(repo),
                         "--write-code-index"], capture_output=True, text=True)
    check("重复执行幂等（已是最新）",
          r2.returncode == 0 and "已是最新" in r2.stdout, r2.stdout[-200:])

    r3 = subprocess.run([PY, str(SCRIPTS / "scan_repo.py"), str(repo),
                         "--write-code-index", "--lang", "en"],
                        capture_output=True, text=True)
    en_text = ci.read_text(encoding="utf-8")
    check("--lang en 渲染英文标题",
          r3.returncode == 0 and "# Code Index" in en_text
          and "# 代码索引" not in en_text, r3.stderr[-200:])


# ---------------------------------------------------------------- 3. lessons 机械闸门

LESSON_BODY = """<!-- last-updated: 2026-01-01 -->
<!-- lesson-meta: status={status} count={count} post=0 target={target} -->
# 测试 lesson

## 晋升去向

{note}
"""


def test_lessons_gate(tmp: Path) -> None:
    print("\n[3] lessons 机械闸门")
    repo = make_fixture(tmp / "lessons", "python-cli")
    run_init(repo)
    lesson = repo / "aiDoc" / "memory" / "lessons" / "2026-01-01-demo.md"

    def run_sync() -> subprocess.CompletedProcess:
        return subprocess.run(
            [PY, str(SCRIPTS / "check_sync.py"), str(repo)],
            capture_output=True, text=True)

    write(lesson, LESSON_BODY.format(status="pending", count=2, target="", note=""))
    r = run_sync()
    check("pending≥2 未处理 exit 1", r.returncode == 1, r.stdout[-200:])

    write(lesson, LESSON_BODY.format(
        status="deferred", count=2, target="", note="暂缓：等待上游接口稳定"))
    r = run_sync()
    check("deferred exit 0", r.returncode == 0, (r.stdout + r.stderr)[-200:])

    write(lesson, LESSON_BODY.format(status="promoted", count=2, target="", note=""))
    r = run_sync()
    check("promoted 缺 target exit 1", r.returncode == 1, r.stdout[-200:])

    write(lesson, LESSON_BODY.format(
        status="promoted", count=2, target="AGENTS.md", note="AGENTS.md 不变量节"))
    r = run_sync()
    check("promoted 有 target exit 0", r.returncode == 0, (r.stdout + r.stderr)[-200:])

    write(lesson, "<!-- last-updated: 2026-01-01 -->\n# 旧格式 lesson（无标记）\n")
    r = run_sync()
    check("缺标记仅提示 exit 0",
          r.returncode == 0 and "lesson-meta" in r.stdout, r.stdout[-200:])


# ---------------------------------------------------------------- 4. zh/en 镜像

def _heading_levels(text: str) -> list[int]:
    """标题层级序列（跳过代码块）——zh/en 语言不同，结构镜像按层级对比。"""
    out: list[int] = []
    in_code = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not in_code and line.startswith("#"):
            out.append(len(line) - len(line.lstrip("#")))
    return out


def test_template_mirror() -> None:
    print("\n[4] zh/en 模板镜像")
    zh = {str(p.relative_to(TEMPLATES / "zh"))
          for p in (TEMPLATES / "zh").rglob("*") if p.is_file()}
    en = {str(p.relative_to(TEMPLATES / "en"))
          for p in (TEMPLATES / "en").rglob("*") if p.is_file()}
    check("文件清单一致", zh == en,
          f"仅 zh: {sorted(zh - en)[:3]} 仅 en: {sorted(en - zh)[:3]}")
    bad = []
    for rel in sorted(zh & en):
        zt = (TEMPLATES / "zh" / rel).read_text(encoding="utf-8")
        et = (TEMPLATES / "en" / rel).read_text(encoding="utf-8")
        for ph in PLACEHOLDERS:
            if zt.count(ph) != et.count(ph):
                bad.append(f"{rel}: {ph} zh={zt.count(ph)} en={et.count(ph)}")
    check("占位符计数一致", not bad, "; ".join(bad[:3]))

    bad = []
    for rel in sorted(zh & en):
        zt = (TEMPLATES / "zh" / rel).read_text(encoding="utf-8")
        et = (TEMPLATES / "en" / rel).read_text(encoding="utf-8")
        if _heading_levels(zt) != _heading_levels(et):
            bad.append(f"{rel}: zh={_heading_levels(zt)} en={_heading_levels(et)}")
    check("标题层级序列镜像（结构一致）", not bad, "; ".join(bad[:2]))


def test_repo_agents_skills_rendered() -> None:
    """本仓 .agents/skills 必须是 zh 模板的渲染实例（<harness>/ 已替换为真实路径）。"""
    print("\n[4b] 本仓 .agents/skills == zh 模板渲染实例")
    src = TEMPLATES / "zh" / "agents-skills"
    bad = []
    for p in sorted(src.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(src)
        rendered = p.read_text(encoding="utf-8").replace("<harness>/", "")
        inst = REPO_ROOT / ".agents" / "skills" / rel
        if not inst.is_file():
            bad.append(f"实例缺失: .agents/skills/{rel}")
        elif inst.read_text(encoding="utf-8") != rendered:
            bad.append(f"实例与模板渲染不一致: .agents/skills/{rel}")
    check(".agents/skills 与 zh 模板渲染实例逐字节一致", not bad, "; ".join(bad[:2]))


# ---------------------------------------------------------------- 5. 耦合校验

# 固定样板区：仓库 aiDoc 实例必须与 zh 模板逐字节一致（除首行 last-updated）。
# 排除带仓库自维护内容的文件（lessons/README 的索引区、project-memory 的索引）。
BOILERPLATE_FILES = (
    "memory/README.md",
    "memory/business/README.md",
    "memory/business/TEMPLATE.md",
    "memory/lessons/TEMPLATE.md",
    "notes/README.md",
    "notes/TEMPLATE.md",
    "plans/README.md",
    "plans/change-plan.TEMPLATE.md",
    "plans/handoff.TEMPLATE.md",
)


def test_boilerplate_consistency() -> None:
    print("\n[5b] aiDoc↔模板样板一致性（dogfood 双家防漂移）")
    bad = []
    for rel in BOILERPLATE_FILES:
        tmpl = (TEMPLATES / "zh" / "aidoc" / rel).read_text(encoding="utf-8")
        inst_p = REPO_ROOT / "aiDoc" / rel
        if not inst_p.is_file():
            bad.append(f"仓库实例缺失: aiDoc/{rel}")
            continue
        inst = inst_p.read_text(encoding="utf-8")
        if tmpl.split("\n", 1)[1] != inst.split("\n", 1)[1]:
            bad.append(f"样板漂移: aiDoc/{rel} != templates/zh/aidoc/{rel}")
    check("固定样板区与模板逐字节一致（除首行）", not bad, "; ".join(bad[:3]))


def test_coupling() -> None:
    print("\n[5] 耦合校验")
    missing = [f for f in init_project.FRONTEND_SKIP
               if not (TEMPLATES / "zh" / "aidoc" / f).is_file()
               or not (TEMPLATES / "en" / "aidoc" / f).is_file()]
    check("FRONTEND_SKIP 文件在双语模板中存在", not missing, str(missing))

    for lang in ("zh", "en"):
        dirs = {p.name for p in (TEMPLATES / lang / "aidoc").iterdir() if p.is_dir()}
        check(f"AIDOC_SECTIONS == templates/{lang}/aidoc 子目录",
              dirs == set(check_sync.AIDOC_SECTIONS),
              f"diff: {dirs ^ set(check_sync.AIDOC_SECTIONS)}")

    mark = init_project.AUTO_SCAN_MARK
    refs_with = [p.name for p in REFERENCES.glob("*.md") if mark in
                 p.read_text(encoding="utf-8")]
    check("auto-scan 标记全文仅在正典 init-harness.md 出现一次",
          refs_with == ["init-harness.md"], f"实际: {refs_with}")

    # 规则正文唯一性抽检：同一规则全文只允许出现在唯一正典（skill 源内）
    skill_mds = [SKILL_DIR / "SKILL.md"] + sorted(REFERENCES.glob("*.md"))
    uniqueness = {
        "冲突优先级链":
            ("`AGENTS.md` > `aiDoc/README.md` > aiDoc sub-documents > "
             "tool adapter files", "SKILL.md"),
        "lesson-meta 示例标记":
            ("lesson-meta: status=pending count=1 post=0 target=",
             "change-docs.md"),
        "code-index 再生成命令":
            ("--write-code-index", "aidoc-structure.md"),
    }
    for name, (needle, home) in uniqueness.items():
        holders = [p.name for p in skill_mds
                   if needle in p.read_text(encoding="utf-8")]
        check(f"{name} 仅正典 {home} 出现", holders == [home], f"实际: {holders}")

    # 框架关键词表单源化：全文只在 scan_repo.py 常量维护
    ga = (REFERENCES / "generate-aidoc.md").read_text(encoding="utf-8")
    check("generate-aidoc.md 不复制关键词表（只留指针）",
          "| Dependency keyword |" not in ga)
    scan_src = (SCRIPTS / "scan_repo.py").read_text(encoding="utf-8")
    missing = [kw for kw in ("uvicorn", "gorm", "actix", "axum", "clap",
                             "servlet") if kw not in scan_src]
    check("scan_repo 关键词常量含合并后的全部关键词", not missing,
          f"缺: {missing}")

    # scan-fill 标记：zh/en 模板的填充点必须逐字一致（脚本按标记定位小节）
    fill_targets = {
        "relations/repo-profile.md":
            ("positioning", "stack", "pkgmgmt", "features"),
        "relations/development-workflow.md": ("env",),
        "relations/system-map.md": ("rootdirs", "config"),
    }
    bad = []
    for rel, keys in fill_targets.items():
        for lang in ("zh", "en"):
            text = (TEMPLATES / lang / "aidoc" / rel).read_text(encoding="utf-8")
            for key in keys:
                marker = f"{init_project.SCAN_FILL_PREFIX}{key}{init_project.SCAN_FILL_SUFFIX}"
                if text.count(marker) != 1:
                    bad.append(f"{lang}/{rel}: {key} 出现 {text.count(marker)} 次")
    check("scan-fill 标记在 zh/en 模板中逐字各出现一次", not bad,
          "; ".join(bad[:3]))


def main() -> int:
    print("project-harness selftest")
    with tempfile.TemporaryDirectory(prefix="ph-selftest-") as td:
        tmp = Path(td)
        test_init_behaviour(tmp)
        test_scripts_runnable(tmp)
        test_write_code_index(tmp)
        test_scan_framework_keywords(tmp)
        test_lessons_gate(tmp)
    test_template_mirror()
    test_repo_agents_skills_rendered()
    test_boilerplate_consistency()
    test_coupling()
    print(f"\n===== {'全部通过' if not FAILURES else f'{len(FAILURES)} 项失败'} =====")
    for f in FAILURES:
        print(f"  ❌ {f}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
