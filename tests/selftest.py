#!/usr/bin/env python3
"""selftest.py — project-harness 工具包自检（零依赖，stdlib only）。

用法:
    python3 tests/selftest.py

覆盖:
    1. init 行为：tmp fixture（python-cli / fullstack / mixed）首跑创建、
       二跑幂等全 SKIP、--dry-run 零写入、嵌套 git 拒绝、--overwrite 有备份。
    2. init 产物跑 check_sync.py 必须 exit 0。
    3. scan_repo.py --json 可运行且输出合法 JSON。
    4. zh/en 模板镜像：文件清单一致 + 每对文件占位符计数一致。
    5. 耦合校验：FRONTEND_SKIP 文件在模板中存在；AIDOC_SECTIONS 与模板
       aidoc/ 子目录集合一致；auto-scan 标记在脚本与 references 中逐字相同；
       scan-fill 标记在 zh/en 模板中逐字各出现一次。
    6. lessons 机械闸门：pending≥2 未处理 / promoted 缺 target → exit 1；
       deferred、promoted 有 target、缺 lesson-meta 标记（仅提示）→ exit 0。

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


# ---------------------------------------------------------------- 5. 耦合校验

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
    check("auto-scan 标记在 references 中逐字出现", len(refs_with) >= 2,
          f"仅 {refs_with}")

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
        test_lessons_gate(tmp)
    test_template_mirror()
    test_coupling()
    print(f"\n===== {'全部通过' if not FAILURES else f'{len(FAILURES)} 项失败'} =====")
    for f in FAILURES:
        print(f"  ❌ {f}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
