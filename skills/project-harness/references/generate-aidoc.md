# Generate workflow

Probe the target codebase and generate/update the `AGENTS.md` + `aiDoc/` documentation system. This is an agent-driven workflow: probing, judgment, and writing are done by the agent. Per-file content requirements and the directory contract are defined **only** in [aidoc-structure.md](aidoc-structure.md) — do not restate them elsewhere.

## Run modes

Parse `$ARGUMENTS`:

| Argument | Behavior |
|---|---|
| (empty) | Full generation: probe the project, generate/refresh all aiDoc files |
| `--incremental` | Read existing aiDoc, compare with code changes, regenerate only stale files |
| `--scope modules` | Regenerate `modules/architecture-rules.md`, `modules/module-development.md`, and module-layer examples under `examples/` |
| `--scope contracts` | Regenerate `contracts/boundary.md` |
| `--scope frontend` | Regenerate `frontend/frontend-rules.md`, `frontend/frontend-utils.md`, `examples/frontend/` |
| `--scope relations` | Regenerate the hand-written files under `relations/` (`code-index.md` is machine-owned; regenerate it via the command in [aidoc-structure.md](aidoc-structure.md)) |
| `--scope memory` | Regenerate files under `memory/` (preserve user-written records) |
| `--scope notes` | Refresh notes indexes/templates only — never rewrite existing decision notes |
| `--scope plans` | Refresh plans indexes/templates only — never rewrite existing plans |
| `--scope core` | Regenerate `AGENTS.md` + `aiDoc/README.md` (load contract and routing layer) |
| `--dry-run` | Output Phase 1 probe results and the generation plan; write nothing |
| `--lang auto\|zh\|en` | Language of generated prose (identifiers stay English). Default `auto`: detect from the repo's existing docs (CJK ratio > 30% → zh, else en; falls back to zh) — same rule as the scripts' `--lang auto` |

`--dry-run` may combine with any mode.

## Phase 1: Project probing

### 1.1 Structure

List top-level directories and key files; detect frontend/backend/fullstack separation; scan subdirectory structure 2–3 levels deep.

### 1.2 Tech stack

Read these files when present:

| File | Yields |
|---|---|
| `package.json`, `pnpm-workspace.yaml`, `lerna.json` | JS/TS dependencies and scripts |
| `pyproject.toml`, `requirements.txt`, `Pipfile`, `setup.py` | Python dependencies |
| `go.mod` / `go.sum` | Go dependencies |
| `pom.xml`, `build.gradle` | Java dependencies |
| `CMakeLists.txt`, `Makefile` | C/C++ build targets and layout |
| `*.pro`, qmake project files | Qt modules and app layout |
| `Cargo.toml` | Rust dependencies |
| `.nvmrc`, `.node-version`, `.python-version` | Runtime versions |
| `Dockerfile`, `docker-compose.yml` | Deployment setup |

**Framework identification**: match from the dependency list, not hardcoded file features. The authoritative keyword table is maintained solely in the constants at the top of `scripts/scan_repo.py` (`FRONTEND_DEPS`, `NODE_WEB_DEPS`, `PY_WEB_DEPS`, `GO_WEB_*`, `RUST_WEB_*`, and the CLI tables) — do not duplicate it here. When the table lacks a framework, extend the script constants in the same change; the agent-side fallback for uncovered frameworks is judging from dependency names + directory structure combined.

### 1.3 Code patterns

- Backend: read 2–3 typical endpoint/controller, service, and model files; identify the layering pattern.
- Frontend: read 2–3 typical page components, API wrappers, state-management files; identify the component pattern.
- CLI: read the command definitions, entry points, and I/O handling; identify the command-registration pattern.
- Library: read the public exports and a typical module; identify the public/internal boundary.
- Identify unified request/response formats, auth mechanism, and data-access pattern (ORM/raw/...).

**Example module selection** (highest priority first):

1. Complete CRUD modules (model + schema + service + endpoint all present).
2. Recently modified modules (use `git log --format="" --name-only`) — they reflect current style.
3. Feature-rich modules (pagination, auth, relations) — broader coverage.

### 1.4 Project type and components

The unit of detection is the **component**: a tuple `(path, kind, language/framework, evidence)` where kind ∈ `web-frontend` / `web-backend` / `cli` / `library` / `qt-app` / `java-app` / `go-module` / `cpp-app` / `generic`. A repository has one or more components; the repo-level label derives from them:

- Single component → one of the six types `fullstack` / `backend` / `frontend` / `library` / `cli` / `general`. Single-component `qt-app` / `go-module` / `cpp-app` maps to `general`.
- Multiple components → `mixed`.

Component kind table:

| Kind | Clues |
|---|---|
| `web-frontend` | frontend framework dependency (vue, react, angular, svelte, next, nuxt, …) |
| `web-backend` | web framework dependency (`fastapi`, `django`, `flask`, `express`, `nestjs`, `gin`, `spring-boot`, …) |
| `cli` | `[project.scripts]` / `bin` entries, `click`, `typer`, `commander`, `cobra` |
| `library` | `[build-system]`, `setup.py`, package `main`/`exports` fields, `[lib]` crate type |
| `qt-app` | `*.pro` / qmake project files, Qt dependencies, `.qml` / `.ui` files |
| `java-app` | `pom.xml` / `build.gradle` with an application entry point |
| `go-module` | `go.mod` with a buildable `main` package |
| `cpp-app` | `CMakeLists.txt` / `Makefile` defining an executable target |
| `generic` | none of the above matched |

Priority when several kinds match one component (first match wins): `web-frontend` > `web-backend` > `cli` > `library` > `qt-app` > `java-app` > `go-module` > `cpp-app` > `generic`.

One directory may host several components (e.g. a `package.json` with both a Vite frontend and an Express server); record each with its own evidence.

The repo-level label derives from the components: `fullstack` (web-frontend + web-backend in one repo) > `frontend` (web-frontend only) > `backend` (web-backend only) > `cli` > `library` > `general`; `has_frontend` = any component is `web-frontend` and still only drives conditional generation of the `frontend/` area. The result drives the adaptive rules in [aidoc-structure.md](aidoc-structure.md) — for `mixed`, content is organized per component.

### 1.5 Auto-scan base

When `init` ran with its default static scan, parts of `relations/` are pre-filled (sections carry the init `auto-scan` marker, defined verbatim in [init-harness.md](init-harness.md)) and `relations/code-index.md` exists as the machine-generated fact base. Treat these as **pre-probed facts**:

- Do not repeat the mechanical scan; start from `code-index.md` (component inventory, language composition, entry points, command index) and the auto-filled sections.
- Calibrate and correct them against the real code — the scan is zero-dependency heuristics and can be wrong.
- After calibrating a section, remove its `auto-scan` marker and the template's `scan-fill` marker. Never hand-edit `code-index.md`; if it is wrong or stale, regenerate it via the command defined in [aidoc-structure.md](aidoc-structure.md).
- With `--no-scan` repos, `code-index.md` remains a skeleton; probe per sections 1.1–1.4 as before.

## Phase 2: Generate per the structure contract

Generate files per [aidoc-structure.md](aidoc-structure.md), which defines the tree, per-file requirements, and writing style.

**Adaptive rules**: file sets and per-type content emphasis are defined solely in the adaptivity table in [aidoc-structure.md](aidoc-structure.md) (six types + `mixed`). Follow that table; do not restate or diverge from it here.

**Parallel groups** — files within a group may be generated in parallel; groups run in order. With `--scope`, generate only the matching group(s).

| Order | Group | Files |
|---|---|---|
| 1 | — | `AGENTS.md` |
| 2 | — | `aiDoc/README.md` |
| 3 | A | `aiDoc/relations/` (hand-written files; `code-index.md` is machine-owned) |
| 4 | B | `aiDoc/modules/` (2 files) |
| 5 | C | `aiDoc/contracts/` + `aiDoc/frontend/` (≤3 files) |
| 6 | D | `aiDoc/examples/` 分层示例（按范式：web 的 model→…→router、library 的公开 API→内部实现、cli 的命令注册→命令处理→核心逻辑；无适用层时可只在 examples/README.md 登记真实参考文件） |
| 7 | E | `aiDoc/examples/README.md` |
| 8 | F | `aiDoc/memory/` (all) |

Report brief progress after each group.

## Incremental update rules (`--incremental`)

- Every file carries a `<!-- last-updated: YYYY-MM-DD -->` header; update it on regeneration.
- Read existing aiDoc files first; use `git diff` since each file's last update to decide which code areas changed; regenerate only affected files.
- Preserve user-tuned content (sections not AI-generated) wherever possible.
- The routing table is cross-file metadata: if any file under `aiDoc/` was added or removed, regenerate `aiDoc/README.md`'s entries and routing table even when its own content is otherwise unchanged.
- Keep `AGENTS.md`'s call logic in sync: its "task family → aiDoc area" quick-reference and "when to regenerate aiDoc" sections must be updated whenever aiDoc areas are added/removed, even if AGENTS.md itself is otherwise unchanged.

## Phase 3: Tool loading adaptation

Full rules in [tool-adapters.md](tool-adapters.md); summary:

- Tools supporting `@import` (e.g. Claude Code): no adapter file. Ensure root `CLAUDE.md` contains exactly the line `@AGENTS.md`; `.claude/` holds only `commands/`.
- Tools without `@import`: write thin adapters **only** for tool directories actually detected, from `templates/<lang>/adapters/`. Adapters contain entry pointers only, never rule bodies.
- Register every tool's loading method in the `AGENTS.md` tool loading table — the sole adapter-state index.

## Verification after generation

Actually execute these steps; do not claim them without running.

### Mechanical (scripted)

Run the drift checker (relative to this skill directory):

```sh
python3 <skill-dir>/scripts/check_sync.py <repo-root>
```

It verifies mechanically checkable facts: aiDoc index completeness (every path in the `aiDoc/README.md` routing table and entries exists), referenced code paths exist, example "real reference files" exist.

### Semantic (agent self-check)

Run the semantic drift checklist in [sync-aidoc.md](sync-aidoc.md) Step 2 — it applies unchanged to freshly generated docs (symbol existence, contract fidelity, example validity, routing consistency, stack accuracy, command validity). Generation adds one requirement the sync checklist does not cover:

- **No invented facts**: every stack item, command, and path traces to a probed source.

## Report format

Reporting discipline (exact commands, passed / failed / skipped / unavailable / not-run) is defined in [quality-workflow.md](quality-workflow.md); the format below is this workflow's concrete instance.

```
## Verification results

### Passed
- [x] Index completeness: N/N files indexed (via aiDoc/README.md)
- [x] Path validity: N/N paths exist
- [x] Symbol consistency: N/N symbols verified
- [x] Example references: N/N reference files exist
- [x] AGENTS.md call logic: quick-reference matches aiDoc/ areas

### Failed (if any)
- [ ] Missing path: xxx
- [ ] Symbol not found: xxx

## Generated/updated files
[list each file with size]

## check_sync.py output
[summary; failures listed verbatim]
```
