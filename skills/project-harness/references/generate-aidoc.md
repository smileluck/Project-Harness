# Generate workflow

Probe the target codebase and generate/update the `AGENTS.md` + `aiDoc/` documentation system. This is an agent-driven workflow: probing, judgment, and writing are done by the agent. Per-file content requirements and the directory contract are defined **only** in [aidoc-structure.md](aidoc-structure.md) — do not restate them elsewhere.

## Run modes

Parse `$ARGUMENTS`:

| Argument | Behavior |
|---|---|
| (empty) | Full generation: probe the project, generate/refresh all aiDoc files |
| `--incremental` | Read existing aiDoc, compare with code changes, regenerate only stale files |
| `--scope backend` | Regenerate `modules/backend-layer-rules.md`, `examples/backend/`, backend parts of `modules/module-development.md` |
| `--scope frontend` | Regenerate `frontend-backend/frontend-rules.md`, `frontend-utils.md`, `examples/frontend/` |
| `--scope relations` | Regenerate the 3 files under `relations/` |
| `--scope memory` | Regenerate files under `memory/` (preserve user-written records) |
| `--scope notes` | Refresh notes indexes/templates only — never rewrite existing decision notes |
| `--scope plans` | Refresh plans indexes/templates only — never rewrite existing plans |
| `--scope core` | Regenerate `AGENTS.md` + `aiDoc/README.md` (load contract and routing layer) |
| `--dry-run` | Output Phase 1 probe results and the generation plan; write nothing |
| `--lang zh\|en` | Language of generated prose (identifiers stay English). Default: match the repo's existing docs language |

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
| `Cargo.toml` | Rust dependencies |
| `.nvmrc`, `.node-version`, `.python-version` | Runtime versions |
| `Dockerfile`, `docker-compose.yml` | Deployment setup |

**Framework identification**: match from the dependency list, not hardcoded file features. Keyword table:

| Dependency keyword | Framework/tech |
|---|---|
| `fastapi`, `uvicorn` | FastAPI |
| `django` | Django |
| `flask` | Flask |
| `hono` | Hono |
| `fastify` | Fastify |
| `express`, `koa`, `nestjs` | Node.js backend |
| `gin`, `gorm`, `fiber` | Go (Gin/Fiber) |
| `spring-boot` | Spring Boot |
| `actix`, `axum` | Rust (Actix/Axum) |
| `vue`, `vite` + `.vue` | Vue |
| `react`, `.jsx`/`.tsx` | React |
| `angular` | Angular |
| `svelte`, `@sveltejs` | Svelte/SvelteKit |
| `next` | Next.js |
| `nuxt` | Nuxt |

Uncovered frameworks: judge from dependency names + directory structure combined.

### 1.3 Code patterns

- Backend: read 2–3 typical endpoint/controller, service, and model files; identify the layering pattern.
- Frontend: read 2–3 typical page components, API wrappers, state-management files; identify the component pattern.
- Identify unified request/response formats, auth mechanism, and data-access pattern (ORM/raw/...).

**Example module selection** (highest priority first):

1. Complete CRUD modules (model + schema + service + endpoint all present).
2. Recently modified modules (use `git log --format="" --name-only`) — they reflect current style.
3. Feature-rich modules (pagination, auth, relations) — broader coverage.

### 1.4 Project type

`fullstack` (both sides) / `backend-only` / `frontend-only`. This drives the adaptive rules below.

## Phase 2: Generate per the structure contract

Generate files per [aidoc-structure.md](aidoc-structure.md), which defines the tree, per-file requirements, and writing style.

**Adaptive rules**:

| Project type | Skip | `boundary.md` becomes |
|---|---|---|
| backend-only | `frontend-backend/frontend-rules.md`, `frontend-utils.md`, `examples/frontend/` | API producer contract |
| frontend-only | `modules/backend-layer-rules.md`, `examples/backend/` | API consumer contract |
| fullstack | nothing | full two-sided contract |

**Parallel groups** — files within a group may be generated in parallel; groups run in order. With `--scope`, generate only the matching group(s).

| Order | Group | Files |
|---|---|---|
| 1 | — | `AGENTS.md` |
| 2 | — | `aiDoc/README.md` |
| 3 | A | `aiDoc/relations/` (3 files) |
| 4 | B | `aiDoc/modules/` (2 files) |
| 5 | C | `aiDoc/frontend-backend/` (≤3 files) |
| 6 | D | `aiDoc/examples/backend/*` |
| 7 | D | `aiDoc/examples/frontend/*` |
| 8 | E | `aiDoc/examples/README.md` |
| 9 | F | `aiDoc/memory/` (all) |

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

What the script cannot prove, verify yourself:

1. **Symbol consistency**: Grep class/function names cited in `boundary.md` and layer-rules docs; confirm they exist in the code.
2. **Example fidelity**: examples match the current style of the modules they were extracted from.
3. **AGENTS.md call logic**: the quick-reference table covers exactly the aiDoc areas that exist; the "when to regenerate" section is present with complete triggers.
4. **No invented facts**: every stack item, command, and path traces to a probed source.

## Report format

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
