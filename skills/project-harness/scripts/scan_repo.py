#!/usr/bin/env python3
"""scan_repo.py — 目标仓库的只读静态扫描（project-harness 的事实来源）。

用法:
    python3 scan_repo.py <repo-path> [--json]
    python3 scan_repo.py <repo-path> --write-code-index [--lang zh|en]

输出结构化结果（纯 dict/list，可 JSON 序列化）:
    root / scanned_at / file_count
    manifests         清单层解析 {相对路径: {...}}（package.json / pyproject.toml /
                      requirements.txt / setup.py / go.mod / pom.xml /
                      build.gradle(.kts) / CMakeLists.txt / Makefile / *.pro /
                      Cargo.toml）
    configs           环境/配置存在性 [{path, kind, value}]
    components        组件探测 [{path, kind, stack, evidence}]
    label             仓库标签 fullstack/backend/frontend/library/cli/general/mixed
    has_frontend      是否含 web-frontend 组件
    languages         语言构成 {扩展名: 文件数}
    top_dirs          顶层目录 [{name, files, exts, convention}]
    modules           模块清单 [{name, path, files, truncated}]
    entry_points      入口点 [{name, type, location, value}]
    commands          命令索引 [{name, command, source, detail}]
    package_managers  包管理 [{tool, evidence}]
    notes             无判定价值的清单说明（如空 package.json）

仅使用标准库；toml 解析在 Python 3.11+ 用 tomllib，否则正则回退。
默认只读：不写任何文件、不执行 git 写操作（git ls-files 只读）。唯一例外是
显式传入 --write-code-index：只写入机器产物 aiDoc/relations/code-index.md，
这是 references 中 code-index.md 漂移修复路径的实现（agent 禁止手编该文件）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from render_data import DIR_CONVENTIONS

try:
    from harness_common import read_text_relaxed
except ImportError:  # 被拷贝到无同级模块的位置时兜底
    def read_text_relaxed(path: Path) -> str | None:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover - 3.9/3.10 环境
    tomllib = None

# ---------------------------------------------------------------- 常量

# 框架识别关键词表——唯一维护点（references/generate-aidoc.md 只放指针，不复制本表）。
# 框架依赖 -> 展示名（值用于组件 stack 字符串）
FRONTEND_DEPS = {
    "vue": "Vue", "react": "React", "react-dom": "React", "next": "Next.js",
    "nuxt": "Nuxt", "@nuxt/core": "Nuxt", "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit", "angular": "Angular",
    "@angular/core": "Angular", "solid-js": "Solid", "@builder.io/qwik": "Qwik",
}
NODE_WEB_DEPS = {
    "express": "Express", "fastify": "Fastify", "koa": "Koa",
    "@nestjs/core": "NestJS", "nestjs": "NestJS", "hono": "Hono",
    "hapi": "hapi", "@hapi/hapi": "hapi",
}
NODE_CLI_DEPS = {"commander": "Commander", "yargs": "Yargs"}
PY_WEB_DEPS = {"fastapi": "FastAPI", "uvicorn": "uvicorn (ASGI)",
               "django": "Django", "flask": "Flask"}
PY_CLI_DEPS = {"click": "Click", "typer": "Typer"}
GO_WEB_RE = re.compile(r"\b(gin|fiber|gorm)\b")
GO_WEB_NAMES = {"gin": "Gin", "fiber": "Fiber", "gorm": "Gorm"}
GO_CLI_RE = re.compile(r"\bcobra\b")
RUST_WEB_RE = re.compile(r"\b(actix-web|actix|axum)\b")
RUST_WEB_NAMES = {"actix": "Actix", "actix-web": "Actix", "axum": "Axum"}
RUST_CLI_RE = re.compile(r"\bclap\b")

# 语言构成统计覆盖的扩展名
LANG_EXTS = (
    ".py", ".js", ".jsx", ".ts", ".tsx", ".vue", ".java", ".go", ".c", ".cc",
    ".cpp", ".cxx", ".h", ".hpp", ".cs", ".rs", ".qml", ".ui", ".pro", ".kt",
    ".swift", ".rb", ".php",
)

C_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp"}

# os.walk 回退时排除的目录名
WALK_EXCLUDES = {
    ".git", "node_modules", ".venv", "__pycache__", "vendor", "dist",
    "build", "target", ".idea",
}

# 组件探测跳过的子目录名
DIR_SKIP = WALK_EXCLUDES | {"aiDoc"}

# 顶层目录约定名 -> (zh, en)
# 模块分组时剥掉的包装前缀
MODULE_STRIP = {"src", "lib", "app"}

MODULE_FILE_CAP = 200

# 组件优先级（同一目录允许多组件；排序/展示按此序）
KIND_ORDER = (
    "qt-app", "web-frontend", "web-backend", "cli", "java-app", "go-module",
    "cpp-app", "library", "generic",
)

SPECIAL_KINDS = {"qt-app", "go-module", "cpp-app"}

LOCKFILES = (
    ("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"),
    ("package-lock.json", "npm"), ("bun.lockb", "bun"), ("uv.lock", "uv"),
)


# ---------------------------------------------------------------- 基础工具

def _read_text(path: Path) -> str:
    # 公共实现在 harness_common.read_text_relaxed；此处保留 "" 语义的薄封装
    return read_text_relaxed(path) or ""


def _dep_name(spec: str) -> str:
    """'fastapi>=0.100' / 'requests[security]; python_version>...' -> 'fastapi'"""
    return re.split(r"[<>=!~;\[ (]", spec.strip(), 1)[0].strip().lower()


def _dedup(names):
    seen: dict = {}
    for n in names:
        seen.setdefault(n, None)
    return list(seen)


# ---------------------------------------------------------------- 文件清单

def list_files(repo: Path) -> list[str]:
    """优先 git ls-files（只读）；失败/为空退回 os.walk（排除常见噪音目录）。"""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"], cwd=str(repo),
            capture_output=True, timeout=30)
        if out.returncode == 0 and out.stdout:
            files = [p for p in out.stdout.decode(
                "utf-8", errors="replace").split("\0") if p]
            if files:
                return sorted(files)
    except (OSError, subprocess.SubprocessError):
        pass
    files = []
    for root, dirs, names in _walk(repo, repo):
        dirs.sort()
        for n in sorted(names):
            files.append(str((root / n).relative_to(repo)).replace("\\", "/"))
    return sorted(files)


def _walk(base: Path, repo: Path):
    import os

    for root, dirs, files in os.walk(base):
        root_p = Path(root)
        dirs[:] = [d for d in dirs
                   if d not in WALK_EXCLUDES and not d.startswith(".")]
        yield root_p, dirs, files


# ---------------------------------------------------------------- 清单层解析

def parse_package_json(path: Path, rel: str) -> dict:
    info = {"type": "package.json", "path": rel, "name": None, "version": None,
            "description": None, "scripts": {}, "bin": None, "main": None,
            "exports": False, "packageManager": None, "dependencies": [],
            "frontend_deps": [], "web_deps": [], "cli_deps": []}
    try:
        data = json.loads(_read_text(path))
    except ValueError:
        return info
    if not isinstance(data, dict):
        return info
    info["name"] = data.get("name")
    info["version"] = data.get("version")
    info["description"] = data.get("description")
    if isinstance(data.get("scripts"), dict):
        info["scripts"] = {str(k): str(v) for k, v in data["scripts"].items()}
    info["bin"] = data.get("bin")
    info["main"] = data.get("main")
    info["exports"] = "exports" in data
    info["packageManager"] = data.get("packageManager")
    deps: set = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        section = data.get(key)
        if isinstance(section, dict):
            deps.update(section.keys())
    info["dependencies"] = sorted(deps)
    info["frontend_deps"] = sorted(d for d in deps if d in FRONTEND_DEPS)
    info["web_deps"] = sorted(d for d in deps if d in NODE_WEB_DEPS)
    info["cli_deps"] = sorted(d for d in deps if d in NODE_CLI_DEPS)
    return info


def _pyproject_regex(text: str) -> dict:
    """tomllib 不可用时的正则回退解析。"""
    def sec(name: str) -> str:
        m = re.search(r"(?ms)^\[" + re.escape(name) + r"\][^\n]*\n(.*?)(?=^\[|\Z)",
                      text)
        return m.group(1) if m else ""

    def s(body: str, key: str):
        m = re.search(r"(?m)^\s*" + re.escape(key) +
                      r"\s*=\s*[\"']([^\"']*)[\"']", body)
        return m.group(1) if m else None

    proj = sec("project")
    deps: list = []
    dm = re.search(r"(?s)dependencies\s*=\s*\[(.*?)\]", proj)
    if dm:
        deps = re.findall(r"[\"']([^\"']+)[\"']", dm.group(1))
    scripts = {}
    for m in re.finditer(r"(?m)^\s*([A-Za-z0-9_.-]+)\s*=\s*[\"']([^\"']+)[\"']",
                         sec("project.scripts")):
        scripts[m.group(1)] = m.group(2)
    return {
        "name": s(proj, "name"), "version": s(proj, "version"),
        "description": s(proj, "description"),
        "requires_python": s(proj, "requires-python"),
        "deps": deps, "scripts": scripts,
        "build": re.search(r"(?m)^\[build-system\]", text) is not None,
        "tools": sorted(set(re.findall(r"(?m)^\[tool\.([A-Za-z0-9_-]+)", text))),
    }


def parse_pyproject(path: Path, rel: str) -> dict:
    text = _read_text(path)
    data = None
    if tomllib is not None:
        try:
            data = tomllib.loads(text)
        except Exception:
            data = None
    if data is not None:
        proj = data.get("project") or {}
        deps = list(proj.get("dependencies") or [])
        opt = proj.get("optional-dependencies") or {}
        if isinstance(opt, dict):
            for group in opt.values():
                if isinstance(group, list):
                    deps.extend(group)
        parsed = {
            "name": proj.get("name"), "version": proj.get("version"),
            "description": proj.get("description"),
            "requires_python": proj.get("requires-python"),
            "deps": [str(d) for d in deps],
            "scripts": dict(proj.get("scripts") or {}),
            "build": "build-system" in data,
            "tools": sorted((data.get("tool") or {}).keys()),
        }
    else:
        parsed = _pyproject_regex(text)
    dep_names = [_dep_name(d) for d in parsed["deps"]]
    # 解析不到依赖列表时回退为全文子串匹配（与旧探测行为一致）
    hay = dep_names if dep_names else [text.lower()]
    web = sorted(d for d in PY_WEB_DEPS if any(d in h for h in hay))
    cli = sorted(d for d in PY_CLI_DEPS if any(d in h for h in hay))
    return {"type": "pyproject.toml", "path": rel,
            "name": parsed["name"], "version": parsed["version"],
            "description": parsed["description"],
            "requires_python": parsed["requires_python"],
            "dependencies": dep_names, "scripts": parsed["scripts"],
            "build_system": parsed["build"], "tools": parsed["tools"],
            "web_deps": web, "cli_deps": cli}


def parse_requirements(path: Path, rel: str) -> dict:
    deps = []
    for line in _read_text(path).splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        name = _dep_name(line)
        if name:
            deps.append(name)
    return {"type": "requirements.txt", "path": rel, "dependencies": deps,
            "web_deps": sorted(d for d in PY_WEB_DEPS if d in deps),
            "cli_deps": sorted(d for d in PY_CLI_DEPS if d in deps)}


def parse_setup_py(path: Path, rel: str) -> dict:
    content = _read_text(path).lower()
    return {"type": "setup.py", "path": rel,
            "web_deps": sorted(d for d in PY_WEB_DEPS if d in content),
            "cli_deps": sorted(d for d in PY_CLI_DEPS if d in content)}


def parse_go_mod(path: Path, rel: str) -> dict:
    text = _read_text(path)
    module = re.search(r"(?m)^module\s+(\S+)", text)
    version = re.search(r"(?m)^go\s+(\S+)", text)
    return {"type": "go.mod", "path": rel,
            "module": module.group(1) if module else None,
            "go_version": version.group(1) if version else None,
            "web": sorted(set(GO_WEB_RE.findall(text))),
            "cli": ["cobra"] if GO_CLI_RE.search(text) else []}


def parse_pom(path: Path, rel: str) -> dict:
    text = _read_text(path)
    body = re.sub(r"(?s)<parent>.*?</parent>", "", text)

    def tag(name: str):
        m = re.search(r"<" + name + r">([^<]+)</" + name + r">", body)
        return m.group(1).strip() if m else None

    return {"type": "pom.xml", "path": rel, "group": tag("groupId"),
            "artifact": tag("artifactId"), "version": tag("version"),
            "spring": "spring-boot" in text,
            "servlet": bool(re.search(
                r"<artifactId>[^<]*(?:servlet|jakarta\.)[^<]*</artifactId>",
                text))}


def parse_gradle(path: Path, rel: str) -> dict:
    text = _read_text(path)
    plugins = re.findall(r"""id\s*\(?\s*['"]([\w.-]+)['"]""", text)
    plugins += re.findall(r"""apply\s+plugin:\s*['"]([\w.-]+)['"]""", text)
    pm = re.search(r"(?s)plugins\s*\{(.*?)\}", text)
    if pm:
        for word in ("java", "application", "java-library"):
            if re.search(r"(?m)^\s*" + word + r"\s*$", pm.group(1)):
                plugins.append(word)
    name = None
    for cand in (path.with_name("settings.gradle"),
                 path.with_name("settings.gradle.kts"), path):
        m = re.search(r"""rootProject\.name\s*=\s*['"]([^'"]+)['"]""",
                      _read_text(cand))
        if m:
            name = m.group(1)
            break
    spring = any("springframework" in p for p in plugins) \
        or "spring-boot" in text
    return {"type": path.name, "path": rel, "plugins": _dedup(plugins),
            "spring": spring, "name": name}


def parse_cmake(path: Path, rel: str) -> dict:
    text = _read_text(path)
    proj = re.search(r"project\s*\(\s*([A-Za-z0-9_.-]+)", text)
    qt = bool(re.search(r"find_package\s*\(\s*Qt[56]", text)
              or re.search(r"Qt[56]::", text))
    exes = re.findall(r"add_executable\s*\(\s*([A-Za-z0-9_.-]+)", text)
    libs = re.findall(r"add_library\s*\(\s*([A-Za-z0-9_.-]+)", text)
    return {"type": "CMakeLists.txt", "path": rel,
            "project": proj.group(1) if proj else None, "qt": qt,
            "executables": exes, "libraries": libs}


MAKE_TARGET_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:(?![=])")


def parse_makefile(path: Path, rel: str) -> dict:
    targets = []
    for line in _read_text(path).splitlines():
        m = MAKE_TARGET_RE.match(line)
        # .PHONY 行首为 '.' 不匹配；模式规则含 '%' 不在字符类内，天然排除
        if m:
            targets.append(m.group(1))
    return {"type": "Makefile", "path": rel, "targets": _dedup(targets)}


def parse_pro(path: Path, rel: str) -> dict:
    text = _read_text(path)
    # qmake 续行（行尾反斜杠）合并
    text = re.sub(r"\\\n", " ", text)
    target = re.search(r"(?m)^\s*TARGET\s*=\s*(\S+)", text)
    template = re.search(r"(?m)^\s*TEMPLATE\s*=\s*(\S+)", text)
    modules: list = []
    for m in re.finditer(r"(?m)^\s*QT\s*\+=\s*(.+)$", text):
        modules.extend(m.group(1).split())
    return {"type": "*.pro", "path": rel,
            "target": target.group(1) if target else None,
            "template": template.group(1) if template else None,
            "qt_modules": modules}


def parse_cargo(path: Path, rel: str) -> dict:
    text = _read_text(path)
    return {"type": "Cargo.toml", "path": rel,
            "lib": "[lib]" in text,
            "web": sorted(set(RUST_WEB_RE.findall(text))),
            "cli": ["clap"] if RUST_CLI_RE.search(text) else []}


MANIFEST_PARSERS = (
    ("package.json", parse_package_json),
    ("pyproject.toml", parse_pyproject),
    ("requirements.txt", parse_requirements),
    ("setup.py", parse_setup_py),
    ("go.mod", parse_go_mod),
    ("pom.xml", parse_pom),
    ("CMakeLists.txt", parse_cmake),
    ("Makefile", parse_makefile),
    ("Cargo.toml", parse_cargo),
)


def scan_manifests(repo: Path, dirs: list[Path]) -> dict:
    manifests: dict = {}
    for d in dirs:
        prefix = "" if d == repo else d.relative_to(repo).as_posix() + "/"
        for name, parser in MANIFEST_PARSERS:
            p = d / name
            if p.is_file():
                manifests[prefix + name] = parser(p, prefix + name)
        for gradle_name in ("build.gradle", "build.gradle.kts"):
            p = d / gradle_name
            if p.is_file():
                manifests[prefix + gradle_name] = parse_gradle(
                    p, prefix + gradle_name)
        for p in sorted(d.glob("*.pro")):
            manifests[prefix + p.name] = parse_pro(p, prefix + p.name)
    return manifests


# ---------------------------------------------------------------- 配置/环境存在性

def scan_configs(repo: Path, files: list[str]) -> list[dict]:
    configs: list = []
    root_files = {f for f in files if "/" not in f}

    def add(path: str, kind: str, value=None):
        configs.append({"path": path, "kind": kind, "value": value})

    if (repo / ".nvmrc").is_file():
        val = _read_text(repo / ".nvmrc").split()
        add(".nvmrc", "nvmrc", val[0] if val else None)
    if (repo / ".python-version").is_file():
        val = _read_text(repo / ".python-version").split()
        add(".python-version", "python-version", val[0] if val else None)
    if "Dockerfile" in root_files:
        add("Dockerfile", "dockerfile")
    for name in ("docker-compose.yml", "docker-compose.yaml"):
        if name in root_files:
            add(name, "docker-compose")
            break
    if "tox.ini" in root_files:
        add("tox.ini", "tox")
    wf = repo / ".github" / "workflows"
    if wf.is_dir():
        n = len(list(wf.glob("*.yml")) + list(wf.glob("*.yaml")))
        add(".github/workflows/", "gh-workflows", n)
    for f in files:
        if f.endswith(".sln"):
            add(f, "sln")
        elif f.endswith(".vcxproj"):
            add(f, "vcxproj")
    return configs


# ---------------------------------------------------------------- 结构层

def language_stats(files: list[str]) -> dict:
    known = set(LANG_EXTS)
    counter: Counter = Counter()
    for f in files:
        ext = Path(f).suffix.lower()
        if ext in known:
            counter[ext] += 1
    return {ext: n for ext, n in sorted(
        counter.items(), key=lambda kv: (-kv[1], kv[0]))}


def top_dirs(files: list[str]) -> list[dict]:
    stats: dict = {}
    for f in files:
        parts = f.split("/")
        if len(parts) < 2:
            continue
        entry = stats.setdefault(parts[0], {"files": 0, "exts": Counter()})
        entry["files"] += 1
        ext = Path(f).suffix.lower()
        if ext:
            entry["exts"][ext] += 1
    out = []
    for name, entry in sorted(stats.items(),
                              key=lambda kv: (-kv[1]["files"], kv[0])):
        top_exts = [e for e, _ in sorted(
            entry["exts"].items(), key=lambda kv: (-kv[1], kv[0]))[:3]]
        out.append({"name": name, "files": entry["files"], "exts": top_exts,
                    "convention": name if name in DIR_CONVENTIONS else ""})
    return out


def module_listing(files: list[str]) -> list[dict]:
    groups: dict = {}
    for f in files:
        parts = f.split("/")
        if len(parts) >= 3 and parts[0] in MODULE_STRIP:
            key, path = parts[1], parts[0] + "/" + parts[1]
        elif len(parts) >= 2:
            key, path = parts[0], parts[0]
        else:
            key, path = "(root)", "."
        groups.setdefault((key, path), 0)
        groups[(key, path)] += 1
    out = []
    for (key, path), n in sorted(groups.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append({"name": key, "path": path, "files": min(n, MODULE_FILE_CAP),
                    "truncated": n > MODULE_FILE_CAP})
    return out


# ---------------------------------------------------------------- 组件探测

def _candidate_dirs(repo: Path) -> list[Path]:
    dirs = [repo]
    try:
        for child in sorted(repo.iterdir()):
            if child.is_dir() and not child.name.startswith(".") \
                    and child.name not in DIR_SKIP:
                dirs.append(child)
    except OSError:
        pass
    return dirs


def _exts_under(files: list[str], prefix: str) -> set:
    exts = set()
    for f in files:
        if not prefix or f.startswith(prefix):
            ext = Path(f).suffix.lower()
            if ext:
                exts.add(ext)
    return exts


# ---------------------------------------------------------------- 组件检测器
# 每个检测器只看自己关心的清单，返回 (stack, evidence) 或 None；
# detect_components 负责编排、赋 kind、排序——加新组件类型 = 加一个检测器。

def _detect_qt(pros: list, cmake, sub_exts: set, prefix: str):
    qt_evi: list = []
    qt_stack = "Qt"
    if pros:
        qt_stack = "Qt (qmake)"
        for pro in pros:
            desc = pro["path"]
            if pro["target"]:
                desc += f" (TARGET={pro['target']}"
                if pro["template"]:
                    desc += f", TEMPLATE={pro['template']}"
                desc += ")"
            qt_evi.append(f"{desc}: qmake 工程")
    if cmake and cmake["qt"]:
        qt_stack = "Qt (CMake)" if not pros else qt_stack
        qt_evi.append(
            f"{cmake['path']}: find_package(Qt5/Qt6) 或 Qt:: 链接")
    if ".qml" in sub_exts:
        qt_evi.append(f"{prefix or '.'}: 存在 .qml 文件")
    if ".ui" in sub_exts:
        qt_evi.append(f"{prefix or '.'}: 存在 .ui 文件（Qt Designer）")
    return (qt_stack, qt_evi) if qt_evi else None


def _detect_web_frontend(pkg):
    if pkg and pkg["frontend_deps"]:
        names = _dedup(FRONTEND_DEPS[d] for d in pkg["frontend_deps"])
        return (" + ".join(names) + " (Node.js)",
                [f"{pkg['path']}: 前端依赖 {', '.join(pkg['frontend_deps'])}"])
    return None


def _detect_web_backend(pkg, pyproj, reqs, setup, gomod, pom, gradle, cargo):
    be_stack: list = []
    be_evi: list = []
    if pkg and pkg["web_deps"]:
        be_stack.extend(NODE_WEB_DEPS[d] for d in pkg["web_deps"])
        be_evi.append(
            f"{pkg['path']}: Node Web 框架依赖 {', '.join(pkg['web_deps'])}")
    for m in (pyproj, reqs, setup):
        if m and m.get("web_deps"):
            be_stack.extend(PY_WEB_DEPS[d] for d in m["web_deps"])
            be_evi.append(
                f"{m['path']}: Python Web 框架依赖 {', '.join(m['web_deps'])}")
    if gomod and gomod["web"]:
        be_stack.extend(GO_WEB_NAMES[d] for d in gomod["web"])
        be_evi.append(
            f"{gomod['path']}: Go Web 框架依赖 {', '.join(gomod['web'])}")
    if pom and pom["spring"]:
        be_stack.append("Spring Boot")
        be_evi.append(f"{pom['path']}: spring-boot 依赖"
                      + (f"（{pom['group']}:{pom['artifact']}）"
                         if pom["artifact"] else ""))
    if gradle and gradle["spring"]:
        be_stack.append("Spring Boot")
        be_evi.append(f"{gradle['path']}: org.springframework.boot 插件")
    if pom and pom.get("servlet") and not pom["spring"]:
        be_stack.append("Java Web (Servlet/Jakarta EE)")
        be_evi.append(f"{pom['path']}: servlet/jakarta 依赖（无 spring-boot）")
    if cargo and cargo["web"]:
        be_stack.extend(RUST_WEB_NAMES[d] for d in cargo["web"])
        be_evi.append(
            f"{cargo['path']}: Rust Web 框架依赖 {', '.join(cargo['web'])}")
    if be_stack:
        return " + ".join(_dedup(be_stack)), be_evi
    return None


def _detect_cli(pkg, pyproj, reqs, gomod, cargo):
    cli_stack: list = []
    cli_evi: list = []
    if pkg:
        if pkg["bin"]:
            cli_evi.append(f"{pkg['path']}: 含 \"bin\" 字段（CLI 入口）")
        if pkg["cli_deps"]:
            cli_stack.extend(NODE_CLI_DEPS[d] for d in pkg["cli_deps"])
            cli_evi.append(
                f"{pkg['path']}: CLI 依赖 {', '.join(pkg['cli_deps'])}")
    if pyproj:
        if pyproj["scripts"]:
            cli_evi.append(
                f"{pyproj['path']}: 含 [project.scripts] 节（CLI 入口）")
        if pyproj["cli_deps"]:
            cli_stack.extend(PY_CLI_DEPS[d] for d in pyproj["cli_deps"])
            cli_evi.append(
                f"{pyproj['path']}: CLI 依赖 {', '.join(pyproj['cli_deps'])}")
    if reqs and reqs["cli_deps"]:
        cli_stack.extend(PY_CLI_DEPS[d] for d in reqs["cli_deps"])
        cli_evi.append(
            f"{reqs['path']}: CLI 依赖 {', '.join(reqs['cli_deps'])}")
    if gomod and gomod["cli"]:
        cli_stack.append("Cobra")
        cli_evi.append(f"{gomod['path']}: CLI 依赖 cobra")
    if cargo and cargo["cli"]:
        cli_stack.append("Clap")
        cli_evi.append(f"{cargo['path']}: CLI 依赖 clap")
    if cli_evi:
        return " + ".join(_dedup(cli_stack)) or "CLI", cli_evi
    return None


def _detect_java_app(pom, gradle):
    """spring/servlet 已归入 web-backend；这里只认无 Web 框架的 Java 工程。"""
    if ((pom and not pom["spring"] and not pom.get("servlet"))
            or (gradle and not gradle["spring"])):
        evi = []
        tool = []
        if pom:
            tool.append("Maven")
            evi.append(f"{pom['path']}: Maven 工程（无 spring-boot）")
        if gradle:
            tool.append("Gradle")
            evi.append(f"{gradle['path']}: Gradle 工程（无 spring 插件）")
        return "Java (" + "/".join(tool) + ")", evi
    return None


def _detect_go_module(gomod):
    if gomod and not gomod["web"] and not gomod["cli"]:
        ver = f" {gomod['go_version']}" if gomod["go_version"] else ""
        return f"Go{ver} module", [f"{gomod['path']}: Go 模块（无 Web/CLI 框架信号）"]
    return None


def _detect_cpp_app(cmake, makefile, sub_exts: set, prefix: str):
    if (cmake or makefile) and (sub_exts & C_EXTS):
        evi = []
        tool = []
        if cmake:
            tool.append("CMake")
            evi.append(f"{cmake['path']}: CMake 工程"
                       + (f"（project={cmake['project']}）"
                          if cmake["project"] else ""))
        if makefile:
            tool.append("Make")
            evi.append(f"{makefile['path']}: Makefile")
        exts = sorted(sub_exts & C_EXTS)
        evi.append(f"{prefix or '.'}: C/C++ 源文件（{', '.join(exts)}）")
        return "C/C++ (" + "/".join(tool) + ")", evi
    return None


def _detect_library(pkg, pyproj, setup, cargo):
    """目录内无更强信号时的兜底：库打包标志。"""
    if pkg and (pkg["main"] or pkg["exports"]):
        fields = "/".join(
            f'"{k}"' for k in ("main", "exports")
            if (pkg["main"] if k == "main" else pkg["exports"]))
        return "Node.js 库", [f"{pkg['path']}: 含 {fields} 字段（库入口）"]
    if pyproj and pyproj["build_system"]:
        return "Python 包", [f"{pyproj['path']}: 含 [build-system] 节（可构建库）"]
    if setup:
        return "Python 包", [f"{setup['path']}: setup.py（可构建库）"]
    if cargo and cargo["lib"]:
        return "Rust 库", [f"{cargo['path']}: 含 [lib] 节（Rust 库）"]
    return None


def detect_components(repo: Path, dirs: list[Path], manifests: dict,
                      files: list[str]) -> tuple[list, list]:
    """返回 (components, notes)。同一目录允许多组件，按 KIND_ORDER 排序。"""
    components: list = []
    notes: list = []

    for d in dirs:
        rel = "." if d == repo else d.relative_to(repo).as_posix()
        prefix = "" if rel == "." else rel + "/"
        sub_exts = _exts_under(files, prefix)

        def mget(name: str):
            return manifests.get(prefix + name)

        pkg = mget("package.json")
        pyproj = mget("pyproject.toml")
        reqs = mget("requirements.txt")
        setup = mget("setup.py")
        gomod = mget("go.mod")
        pom = mget("pom.xml")
        gradle = mget("build.gradle") or mget("build.gradle.kts")
        cmake = mget("CMakeLists.txt")
        makefile = mget("Makefile")
        cargo = mget("Cargo.toml")
        pros = [m for r, m in sorted(manifests.items())
                if r.startswith(prefix) and r.endswith(".pro")
                and "/" not in r[len(prefix):]]

        comps: list = []

        def comp(kind: str, stack: str, evidence: list):
            comps.append({"path": rel, "kind": kind, "stack": stack,
                          "evidence": evidence})

        qt = _detect_qt(pros, cmake, sub_exts, prefix)
        if qt:
            comp("qt-app", *qt)
        web_fe = _detect_web_frontend(pkg)
        if web_fe:
            comp("web-frontend", *web_fe)
        web_be = _detect_web_backend(pkg, pyproj, reqs, setup, gomod,
                                     pom, gradle, cargo)
        if web_be:
            comp("web-backend", *web_be)
        cli = _detect_cli(pkg, pyproj, reqs, gomod, cargo)
        if cli:
            comp("cli", *cli)
        java = _detect_java_app(pom, gradle)
        if java:
            comp("java-app", *java)
        gomod_comp = _detect_go_module(gomod)
        if gomod_comp:
            comp("go-module", *gomod_comp)
        # Qt 信号存在时不再判 cpp-app
        if qt is None:
            cpp = _detect_cpp_app(cmake, makefile, sub_exts, prefix)
            if cpp:
                comp("cpp-app", *cpp)
        if not comps:
            lib = _detect_library(pkg, pyproj, setup, cargo)
            if lib:
                comp("library", *lib)

        # 无判定价值的清单说明
        if pkg and not (pkg["frontend_deps"] or pkg["web_deps"]
                        or pkg["cli_deps"] or pkg["bin"] or pkg["main"]
                        or pkg["exports"]):
            notes.append(
                f"{pkg['path']}: package.json（无明确依赖线索，不计入判定）")

        order = {k: i for i, k in enumerate(KIND_ORDER)}
        comps.sort(key=lambda c: order[c["kind"]])
        components.extend(comps)

    if not components:
        components.append({"path": ".", "kind": "generic", "stack": "未识别",
                           "evidence": ["未发现任何技术栈标志文件"]})
    return components, notes


def repo_label(components: list) -> tuple[str, bool, list]:
    """组件集合 -> (仓库标签, has_frontend, 补充 clues)。"""
    kinds = {c["kind"] for c in components if c["kind"] != "generic"}
    has_frontend = "web-frontend" in kinds
    extra: list = []
    if not kinds:
        extra.append("未发现任何技术栈标志文件，按 general 处理（全量模板）")
        return "general", False, extra

    paths = {c["path"] for c in components if c["kind"] != "generic"}
    strong = kinds - {"library"}
    fe = "web-frontend" in kinds
    be = bool(kinds & {"web-backend", "java-app"})

    # 多路径且多强信号种类 -> mixed
    if len(paths) > 1 and len(strong) > 1:
        return "mixed", has_frontend, extra
    if fe and be:
        return "fullstack", has_frontend, extra
    if fe:
        return "frontend", has_frontend, extra
    if be:
        return "backend", has_frontend, extra
    if "cli" in kinds:
        return "cli", has_frontend, extra
    if kinds == {"library"}:
        return "library", has_frontend, extra
    if kinds <= SPECIAL_KINDS:
        noted = ", ".join(f"{c['kind']}({c['path']})" for c in components
                          if c["kind"] in SPECIAL_KINDS)
        extra.append(f"组件 {noted} 不属于六类型标签，按 general 处理")
        return "general", has_frontend, extra
    return "mixed", has_frontend, extra


# ---------------------------------------------------------------- 入口点 / 命令 / 包管理

def collect_entry_points(manifests: dict) -> list:
    eps: list = []
    for rel, m in sorted(manifests.items()):
        t = m["type"]
        if t == "package.json":
            binv = m.get("bin")
            if isinstance(binv, dict):
                for name, target in sorted(binv.items()):
                    eps.append({"name": str(name), "type": "package.json bin",
                                "location": rel, "value": str(target)})
            elif isinstance(binv, str):
                eps.append({"name": m.get("name") or binv,
                            "type": "package.json bin", "location": rel,
                            "value": binv})
            if m.get("main"):
                eps.append({"name": m.get("name") or m["main"],
                            "type": "package.json main", "location": rel,
                            "value": m["main"]})
        elif t == "pyproject.toml":
            for name, target in sorted((m.get("scripts") or {}).items()):
                eps.append({"name": name, "type": "project.scripts",
                            "location": rel, "value": str(target)})
        elif t == "go.mod" and m.get("module"):
            eps.append({"name": m["module"], "type": "go module",
                        "location": rel, "value": m["module"]})
        elif t == "pom.xml" and m.get("artifact"):
            gav = ":".join(x for x in (m.get("group"), m.get("artifact"),
                                       m.get("version")) if x)
            eps.append({"name": m["artifact"], "type": "maven artifact",
                        "location": rel, "value": gav})
        elif t == "CMakeLists.txt":
            for name in m.get("executables") or []:
                eps.append({"name": name, "type": "add_executable",
                            "location": rel, "value": name})
            for name in m.get("libraries") or []:
                eps.append({"name": name, "type": "add_library",
                            "location": rel, "value": name})
        elif t == "*.pro" and m.get("target"):
            eps.append({"name": m["target"], "type": "qmake TARGET",
                        "location": rel, "value": m["target"]})
    return eps


def _pm_for(m: dict, lock_pms: list) -> str:
    pmf = m.get("packageManager")
    if pmf:
        return str(pmf).split("@", 1)[0]
    return lock_pms[0] if lock_pms else "npm"


def collect_commands(manifests: dict, configs: list,
                     lock_pms: list) -> list:
    """命令索引。weight 用于工作流表排序：install < run < test < build < 其他。"""
    cmds: list = []

    def add(name, command, source, detail="", weight=4):
        cmds.append({"name": name, "command": command, "source": source,
                     "detail": detail, "weight": weight})

    for rel, m in sorted(manifests.items()):
        t = m["type"]
        if t == "package.json":
            pm = _pm_for(m, lock_pms)
            add("install", f"{pm} install", rel, weight=0)
            for name, cmd in sorted((m.get("scripts") or {}).items()):
                if name in ("dev", "start", "serve"):
                    w = 1
                elif name == "test":
                    w = 2
                elif name == "build":
                    w = 3
                else:
                    w = 4
                run = f"{pm} {'test' if name == 'test' and pm == 'npm' else 'run ' + name}"
                add(name, run, rel, detail=cmd, weight=w)
        elif t == "Makefile":
            for target in m.get("targets") or []:
                w = 2 if target == "test" else (3 if target == "build" else 4)
                add(target, f"make {target}", rel, weight=w)
        elif t == "pyproject.toml":
            add("install", "pip install -e .", rel, weight=0)
            if "pytest" in (m.get("tools") or []):
                add("test", "pytest", rel, weight=2)
        elif t == "requirements.txt":
            add("install", f"pip install -r {rel}", rel, weight=0)
        elif t == "go.mod":
            add("build", "go build ./...", rel, weight=3)
            add("test", "go test ./...", rel, weight=2)
        elif t == "pom.xml":
            add("build", "mvn package", rel, weight=3)
            add("test", "mvn test", rel, weight=2)
        elif m["type"] in ("build.gradle", "build.gradle.kts"):
            add("build", "gradle build", rel, weight=3)
            add("test", "gradle test", rel, weight=2)
    for c in configs:
        if c["kind"] == "tox":
            add("test", "tox", c["path"], weight=2)
    cmds.sort(key=lambda c: (c["weight"], c["source"], c["name"]))
    return cmds


def infer_package_managers(manifests: dict, files: list[str]) -> tuple[list, list]:
    """返回 ([{tool, evidence}], node 侧锁定文件推出的 pm 列表)。"""
    root_files = {f for f in files if "/" not in f}
    lock_pms = [pm for name, pm in LOCKFILES if name in root_files]
    pms: list = []
    node = [m for m in manifests.values() if m["type"] == "package.json"]
    if node:
        pmf = next((str(m["packageManager"]).split("@", 1)[0]
                    for m in node if m.get("packageManager")), None)
        tool = pmf or (lock_pms[0] if lock_pms else "npm")
        evi = [m["path"] for m in node]
        evi += [n for n, pm in LOCKFILES if n in root_files and pm == tool]
        pms.append({"tool": tool, "evidence": sorted(set(evi))})
    py = [m for m in manifests.values()
          if m["type"] in ("pyproject.toml", "requirements.txt", "setup.py")]
    if py:
        tool = "uv" if "uv" in lock_pms else "pip"
        evi = [m["path"] for m in py]
        if "uv" in lock_pms:
            evi.append("uv.lock")
        pms.append({"tool": tool, "evidence": sorted(set(evi))})
    if any(m["type"] == "go.mod" for m in manifests.values()):
        pms.append({"tool": "go mod", "evidence": [
            m["path"] for m in manifests.values() if m["type"] == "go.mod"]})
    if any(m["type"] == "pom.xml" for m in manifests.values()):
        pms.append({"tool": "Maven", "evidence": [
            m["path"] for m in manifests.values() if m["type"] == "pom.xml"]})
    if any(m["type"] in ("build.gradle", "build.gradle.kts")
           for m in manifests.values()):
        pms.append({"tool": "Gradle", "evidence": [
            m["path"] for m in manifests.values()
            if m["type"] in ("build.gradle", "build.gradle.kts")]})
    if any(m["type"] == "Cargo.toml" for m in manifests.values()):
        pms.append({"tool": "Cargo", "evidence": [
            m["path"] for m in manifests.values() if m["type"] == "Cargo.toml"]})
    return pms, lock_pms


# ---------------------------------------------------------------- 顶层扫描

def scan_repo(repo) -> dict:
    repo = Path(repo).expanduser().resolve()
    files = list_files(repo)
    dirs = _candidate_dirs(repo)
    manifests = scan_manifests(repo, dirs)
    configs = scan_configs(repo, files)
    components, notes = detect_components(repo, dirs, manifests, files)
    label, has_frontend, label_clues = repo_label(components)
    entry_points = collect_entry_points(manifests)
    pms, lock_pms = infer_package_managers(manifests, files)
    commands = collect_commands(manifests, configs, lock_pms)
    clues = []
    for c in components:
        clues.extend(c["evidence"])
    clues.extend(notes)
    clues.extend(label_clues)
    return {
        "root": str(repo),
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "file_count": len(files),
        "label": label,
        "has_frontend": has_frontend,
        "components": components,
        "clues": clues,
        "manifests": manifests,
        "configs": configs,
        "languages": language_stats(files),
        "top_dirs": top_dirs(files),
        "modules": module_listing(files),
        "entry_points": entry_points,
        "commands": commands,
        "package_managers": pms,
        "notes": notes,
    }


# ---------------------------------------------------------------- code-index 渲染

# 机器产物相对路径（init_project 注入与本脚本 --write-code-index 共用同一目标）
CODE_INDEX_REL = "aiDoc/relations/code-index.md"


def _path_disp(path: str, lang: str) -> str:
    if path == ".":
        return "（根）" if lang == "zh" else "(root)"
    return f"`{path}`"


def render_code_index(scan: dict, lang: str = "zh",
                      today: str | None = None) -> str:
    today = today or datetime.now().date().isoformat()
    zh = lang == "zh"
    L: list = []
    L.append("<!-- auto-generated by scan_repo.py; do not hand-edit -->")
    L.append(f"<!-- last-updated: {today} -->")
    L.append("# 代码索引（code index）" if zh else "# Code Index")
    L.append("")
    L.append("> 机器产物：由 scan_repo.py 生成，init/generate 工作流会整体重写本文件，"
             "请勿手工编辑。" if zh else
             "> Machine-generated by scan_repo.py. init/generate workflows rewrite "
             "this file wholesale — do not hand-edit.")
    L.append("")

    # 组件清单
    L.append("## 组件清单" if zh else "## Components")
    L.append("")
    L.append("| 路径 | 种类 | 语言/框架 | 依据 |" if zh else
             "| Path | Kind | Language / framework | Evidence |")
    L.append("|---|---|---|---|")
    comps = [c for c in scan["components"] if c["kind"] != "generic"]
    if comps:
        for c in comps:
            evi = c["evidence"][0]
            if len(c["evidence"]) > 1:
                evi += f"（+{len(c['evidence']) - 1} 条）" if zh else \
                    f" (+{len(c['evidence']) - 1} more)"
            L.append(f"| {_path_disp(c['path'], lang)} | {c['kind']} | "
                     f"{c['stack']} | {evi} |")
    else:
        L.append("| - | - | "
                 + ("无组件信号" if zh else "no component signals") + " | - |")
    L.append("")

    # 语言构成
    L.append("## 语言构成" if zh else "## Language Composition")
    L.append("")
    L.append("| 扩展名 | 文件数 |" if zh else "| Extension | Files |")
    L.append("|---|---|")
    if scan["languages"]:
        for ext, n in scan["languages"].items():
            L.append(f"| {ext} | {n} |")
    else:
        L.append("| - | 0 |")
    L.append("")

    # 模块清单
    L.append("## 模块清单" if zh else "## Modules")
    L.append("")
    L.append("| 模块 | 路径 | 文件数 |" if zh else "| Module | Path | Files |")
    L.append("|---|---|---|")
    for m in scan["modules"]:
        n = str(m["files"])
        if m["truncated"]:
            n += ("+（截断，实际更多）" if zh else "+ (truncated)")
        path = m["path"] if m["path"] == "." else f"`{m['path']}`"
        L.append(f"| {m['name']} | {path} | {n} |")
    L.append("")

    # 入口点
    L.append("## 入口点" if zh else "## Entry Points")
    L.append("")
    L.append("| 入口 | 类型 | 位置 |" if zh else "| Entry | Type | Location |")
    L.append("|---|---|---|")
    if scan["entry_points"]:
        for e in scan["entry_points"]:
            L.append(f"| {e['name']} | {e['type']} | `{e['location']}` |")
    else:
        L.append("| - | "
                 + ("未发现明确入口点" if zh else "no entry points found")
                 + " | - |")
    L.append("")

    # 命令索引
    L.append("## 命令索引" if zh else "## Command Index")
    L.append("")
    L.append("| 命令 | 来源 | 说明 |" if zh else "| Command | Source | Detail |")
    L.append("|---|---|---|")
    if scan["commands"]:
        for c in scan["commands"]:
            L.append(f"| `{c['command']}` | `{c['source']}` | {c['detail']} |")
    else:
        L.append("| - | - | "
                 + ("未发现命令定义" if zh else "no commands found") + " |")
    L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- 人读摘要

def print_summary(scan: dict) -> None:
    print(f"scan_repo: {scan['root']}")
    print(f"文件数: {scan['file_count']}  标签: {scan['label']}  "
          f"has_frontend: {scan['has_frontend']}")
    print("\n组件:")
    for c in scan["components"]:
        print(f"  {c['path']}: {c['kind']} — {c['stack']}")
        for ev in c["evidence"]:
            print(f"      依据: {ev}")
    print("\n语言构成:")
    for ext, n in scan["languages"].items():
        print(f"  {ext}: {n}")
    print("\n顶层目录:")
    for d in scan["top_dirs"]:
        conv = DIR_CONVENTIONS[d["convention"]][0] if d["convention"] else ""
        print(f"  {d['name']}/ — {d['files']} 文件"
              f" ({', '.join(d['exts'])})" + (f" [{conv}]" if conv else ""))
    print("\n模块:")
    for m in scan["modules"]:
        mark = "（截断）" if m["truncated"] else ""
        print(f"  {m['name']} ({m['path']}) — {m['files']} 文件{mark}")
    print("\n入口点:")
    for e in scan["entry_points"]:
        print(f"  {e['name']} [{e['type']}] @ {e['location']} -> {e['value']}")
    print("\n命令:")
    for c in scan["commands"]:
        print(f"  {c['command']:<28} ({c['source']}) {c['detail']}")
    print("\n包管理:")
    for p in scan["package_managers"]:
        print(f"  {p['tool']} — 依据: {', '.join(p['evidence'])}")
    if scan["configs"]:
        print("\n配置/环境:")
        for c in scan["configs"]:
            val = f" = {c['value']}" if c["value"] is not None else ""
            print(f"  {c['path']} [{c['kind']}]{val}")


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="只读静态扫描目标仓库，输出结构化事实（供 project-harness 使用）。")
    parser.add_argument("repo_path", help="目标仓库根目录")
    parser.add_argument("--json", action="store_true",
                        help="打印完整 JSON 结果（默认打印人读摘要）")
    parser.add_argument("--write-code-index", action="store_true",
                        help="扫描后重新生成机器产物 "
                             "aiDoc/relations/code-index.md（默认只读不写文件）")
    parser.add_argument("--lang", choices=("zh", "en"), default="zh",
                        help="--write-code-index 的渲染语言（默认 zh）")
    args = parser.parse_args(argv)

    repo = Path(args.repo_path).expanduser().resolve()
    if not repo.is_dir():
        print(f"错误: 路径不存在或不是目录: {repo}", file=sys.stderr)
        return 2
    result = scan_repo(repo)
    if args.write_code_index:
        dst = repo / CODE_INDEX_REL
        content = render_code_index(result, lang=args.lang)
        try:
            unchanged = dst.is_file() and \
                dst.read_text(encoding="utf-8") == content
        except OSError:
            unchanged = False
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
        status = "已是最新（内容无变化）" if unchanged else "已重新生成"
        print(f"code-index {status}: {dst}")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_summary(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
