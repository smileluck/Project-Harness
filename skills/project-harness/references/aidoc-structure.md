# aiDoc structure contract

This file is the single maintained source for the target repository's `AGENTS.md` + `aiDoc/` layout and per-file content requirements. Other workflow docs (e.g. [generate-aidoc.md](generate-aidoc.md)) point here instead of restating them. Templates live under `templates/<lang>/aidoc/`; this file defines what generated content must satisfy.

## Directory tree

```
AGENTS.md                        # L0 sole source of standing rules
CLAUDE.md                        # one line: @AGENTS.md
aiDoc/
  README.md                      # L1 index + task→required-docs routing table
  relations/
    repo-profile.md              # project identity & tech stack
    development-workflow.md      # dev flow, branches, commits, commands
    system-map.md                # architecture & component relations
  modules/
    backend-layer-rules.md       # backend layering constraints (backend projects)
    module-development.md        # step-by-step module/feature guide
  frontend-backend/
    boundary.md                  # contract between sides (API contract if one side only)
    frontend-rules.md            # frontend conventions (frontend projects)
    frontend-utils.md            # shared-utils reuse rules (frontend projects)
  examples/
    README.md                    # reading order & purpose of the example layer
    backend/*.md                 # one example per backend layer
    frontend/*.md                # api / view / utils-usage examples
  memory/
    README.md                    # memory-layer rules
    project-memory.md            # memory index (must be updated on every new memory)
    long-term/README.md          # stable cross-session preferences
    business/README.md           # business-requirement records + index
    business/TEMPLATE.md         # template for a new business record
  notes/<lifecycle>/<class>/     # decision records (see change-docs.md)
  plans/active|completed/        # change plans (see change-docs.md)
.agents/skills/                  # two project-local workflow skills
<tool dirs>                      # thin adapters only (see tool-adapters.md)
```

Adaptivity: backend-only projects skip the frontend-only files; frontend-only projects skip the backend-only files; `boundary.md` becomes a pure API contract (producer or consumer side) when only one side exists. Do not generate files for absent layers.

Every generated file starts with `<!-- last-updated: YYYY-MM-DD -->`.

## Per-file requirements

### `AGENTS.md` (root, L0)

- States it is the sole source of agent collaboration rules, carrying only the minimal high-level rules every agent must always know; details route to `aiDoc/`.
- Documents the load model: L0 auto-load (via `CLAUDE.md @AGENTS.md` where supported), L1 routing via `aiDoc/README.md`, L2 deep reads; and the conflict priority `AGENTS.md` > `aiDoc/README.md` > aiDoc sub-documents > tool adapter files.
- Contains a **tool loading table** (see [tool-adapters.md](tool-adapters.md)) — the sole registry of adapter state.
- Repository overview: top-level directories by responsibility, from real probing. Tool-private directories are not listed here; their loading is covered by the tool table.
- Engineering rules (architecture layering, API contract, module/directory conventions), each traceable to real code.
- Fixed short sections: examples layer purpose, memory rules (long-term = stable preferences, business = each requirement), doc maintenance rule (routing table maintained only in `aiDoc/README.md` — AGENTS.md keeps only a coarse "task family → aiDoc area" quick-reference, never a duplicated detailed list), code-reading exclusions (`node_modules/`, `.venv/`, `__pycache__/`, `vendor/`, …).
- A "when to regenerate aiDoc" section listing the trigger conditions for the `generate` workflow (architecture change, module/page added or removed, routing table drift, example drift), noting small changes only need `--incremental` or `--scope`.

### `aiDoc/README.md` (L1 routing layer)

- Explains the load model (L0/L1/L2) in 3-4 steps.
- One-line description per directory.
- **Common entries** dictionary: every aiDoc file, one line each — path + one-sentence purpose.
- **Task → required-docs routing table**: every task type the project supports, paths relative to `aiDoc/`. This table is the sole detailed routing index; AGENTS.md must not duplicate it.
- Maintenance rules: stable rules live here, not in tool-private dirs; session drafts are not committed; **adding/removing any aiDoc sub-document requires updating this file's entries and routing table in the same change** — otherwise the document is not checked in.

### `aiDoc/relations/repo-profile.md`

Project positioning (inferred from manifests + README + user prompt), backend stack (language, framework, ORM, database, cache, migrations, auth), frontend stack (framework, build tool, UI library, state management, routing, styling), package manager, and a table of project-specific key features (response format, ID strategy, auth mechanism, …). All from real probing.

### `aiDoc/relations/development-workflow.md`

Recommended development order matching the real layering, frontend/backend collaboration flow, branch strategy, commit message convention, concrete install/start/migrate commands, API doc URLs if any.

### `aiDoc/relations/system-map.md`

Table of top-level directory responsibilities; the real layering flow (e.g. Router → Controller → Service → Model); infrastructure directories and their roles; frontend data flow if a frontend exists; backend-module ↔ frontend-page mapping; key configuration files and their purpose.

### `aiDoc/modules/backend-layer-rules.md` (backend projects)

- Prime directive: strict layering, no cross-layer calls.
- Per layer (Model, Schema/DTO, Service, Controller/Endpoint, Router): base-class inheritance, field declaration style, naming, location, method-signature patterns, exception handling, pagination.
- Error-code allocation table if the project has one.
- **Every rule must cite real class names and file paths** (e.g. `app/models/common/page.py:PageRequest`).

### `aiDoc/modules/module-development.md` (backend projects)

Complete steps for a new backend module (directory → model → schema → service → endpoint → router → registration → migration) and, if a frontend exists, for a new frontend feature (types → API function → i18n → page → routing). Design principles: self-contained, follow existing patterns. Cite real reference file paths.

### `aiDoc/frontend-backend/boundary.md`

Responsibility table per side; the actual unified response structure (JSON + field meanings); pagination structure if any; field naming convention (snake_case/camelCase); type bridging with conversion flow and code locations for any non-obvious conversion; time-field format/timezone if special; change rules and a pre-completion checklist. For single-sided projects, the producer or consumer API contract only.

### `aiDoc/frontend-backend/frontend-rules.md` (frontend projects)

Base rules (HTTP layer, state management, routing); naming conventions table (files, components, variables, API functions); type requirements; component rules (shared vs page components, props style); required steps for a new page; styling priority; i18n rules if present; environment variables; common script commands table; comment requirements.

### `aiDoc/frontend-backend/frontend-utils.md` (frontend projects)

Core principle: check existing utilities first, never rebuild. Inventory of the utils directory with purposes; workspace sub-package responsibilities in a monorepo; a mandatory-use table mapping scenarios to the required utility.

### `aiDoc/examples/`

- `README.md`: the example layer is instructive, not copy-paste; reading order per side; real code wins over examples when they disagree (and then the example must be updated).
- Backend (one file per layer): `model-example.md`, `schema-example.md`/`dto-example.md`, `service-example.md`, `endpoint-example.md`/`controller-example.md`, `router-example.md`.
- Frontend: `api-example.md`, `view-example.md`, `utils-usage-example.md`.
- Every example file: purpose, 2-3 core principles, an example **extracted from real project code** (sensitive data stripped), key-point explanations, and a **Real reference files** list of actual paths. If the project lacks suitable code, write code that matches the probed project style — never generic boilerplate.

### `aiDoc/memory/`

- `README.md`: long-term/ = stable user preferences; business/ = one record per business requirement; drafts are not committed.
- `project-memory.md`: index with `## Long-term` and `## Business requirements` sections, plus maintenance notes. Must be updated whenever a memory file is added or removed.
- `long-term/README.md`: record only repeatedly confirmed stable patterns; each entry has rule, applicable scenarios, source; delete stale entries.
- `business/README.md` + `business/TEMPLATE.md`: the template carries description, status (pending/in-progress/done/cancelled), backend scope, frontend scope, constraints, related files, record date. New records use the template and update both indexes.

### `aiDoc/notes/` and `aiDoc/plans/`

Decision records and change plans. Lifecycle/class rules, naming, and discipline are defined in [change-docs.md](change-docs.md); templates in `templates/<lang>/aidoc/notes/` and `templates/<lang>/aidoc/plans/`.

### Nested `AGENTS.md`

Create only where a subtree materially differs from the root in commands, architecture, generated/source ownership, safety, testing, or documentation. A nested file supplements the root and must not repeat it. Do not mirror the directory tree mechanically. Typical candidates: frontend, infrastructure, database migrations, generated SDKs, vendored code.

## Writing style

1. **Concise imperative language** — must / should / never; no filler.
2. **Precise path references** — rules cite real file paths and class/function symbols (`path/file.py:Symbol`).
3. **Clear Markdown hierarchy** — `##`/`###`, tables preferred over prose lists.
4. **Relative-path cross references** between aiDoc files.
5. **Content from real probing** — every technical detail must come from actual code and manifests; never invent.
6. Document language follows the workflow's `--lang` parameter (default: the repo's existing docs language); code identifiers and technical terms stay in English.
