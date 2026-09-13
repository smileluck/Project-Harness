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
    code-index.md                # machine-generated scan facts: components, languages, entry points, commands
  modules/
    architecture-rules.md        # architecture & module organization rules
    module-development.md        # step-by-step module/feature guide
  contracts/
    boundary.md                  # contract layer: web-api / library / cli variant
  frontend/
    frontend-rules.md            # frontend conventions (frontend projects only)
    frontend-utils.md            # shared-utils reuse rules (frontend projects only)
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
    lessons/README.md            # lesson capture rules + promotion discipline + index
    lessons/TEMPLATE.md          # template for a new lesson record
  notes/<lifecycle>/<class>/     # decision records (see change-docs.md)
  plans/active|completed/        # change plans (see change-docs.md)
.agents/skills/                  # two project-local workflow skills
<tool dirs>                      # thin adapters only (see tool-adapters.md)
```

Adaptivity: the harness supports six project types — `fullstack`, `backend`, `frontend`, `library`, `cli`, `general` — plus `mixed` for multi-component repositories. The component model and the derivation of the repo-level label are defined in [generate-aidoc.md](generate-aidoc.md) Phase 1.4; this file owns only the per-type file sets and content emphasis. The **only** conditional area is `frontend/` (generated only when a real frontend exists — i.e. any component is `web-frontend`); every other area is generated for all types, with content shaped by paradigm:

| Project type | `frontend/` area | `contracts/boundary.md` | `modules/architecture-rules.md` | `modules/module-development.md` | `examples/` |
|---|---|---|---|---|---|
| fullstack | generated | web-api variant, two-sided | layered-service paradigm | backend module + frontend feature steps | backend-layer + frontend examples |
| backend | skipped | web-api variant, producer side | layered-service paradigm | backend module steps | backend-layer examples |
| frontend | generated | web-api variant, consumer side | component-structure paradigm | frontend feature steps | frontend examples |
| library | skipped | library variant (public API surface) | package-module paradigm | new public module/feature steps | public-API usage examples |
| cli | skipped | cli variant (command spec) | command/plugin paradigm | new command/subcommand steps | command usage examples |
| general | skipped | closest-fitting variant | dominant structure, documented as found | dominant development flow | examples matching the dominant structure |
| mixed (multi-component) | generated if any component is `web-frontend` | inter-component contracts (e.g. web frontend ↔ server API, Qt UI ↔ core library interface) | one section per component, each in its own paradigm | per-component steps + cross-component change order | examples per component |

For `mixed` projects: `modules/architecture-rules.md` is organized per component (each component gets a section in its matching paradigm variant), `contracts/boundary.md` documents the contracts **between** components, and `relations/system-map.md` organizes the root-directory table by component (one annotated row per component). The component inventory itself lives in `relations/code-index.md`.

Do not generate `frontend/` files for projects without a frontend.

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

Project positioning (inferred from manifests + README + user prompt), primary stack (language, framework, ORM, database, cache, migrations, auth), frontend stack if a frontend exists (framework, build tool, UI library, state management, routing, styling), package manager, and a table of project-specific key features (response format, ID strategy, auth mechanism, …). All from real probing.

### `aiDoc/relations/development-workflow.md`

Recommended development order matching the real structure, collaboration flow across components (e.g. frontend ↔ backend, caller ↔ library) where more than one exists, branch strategy, commit message convention, concrete install/start/migrate commands, API doc URLs if any.

### `aiDoc/relations/system-map.md`

Table of top-level directory responsibilities; the real layering flow (e.g. Router → Controller → Service → Model); infrastructure directories and their roles; frontend data flow if a frontend exists; module ↔ consumer mapping where applicable (e.g. backend-module ↔ frontend-page); key configuration files and their purpose.

### `aiDoc/relations/code-index.md`

Machine artifact written by `scripts/scan_repo.py` (header: `<!-- auto-generated by scan_repo.py; do not hand-edit -->`): component inventory table (path | kind | language/framework | evidence), language composition, module inventory, entry points, command index. Agents never hand-edit it; it is the factual base other aiDoc content is calibrated against. When it drifts, rerun `scan_repo.py` — do not patch it by hand. With `--no-scan` the skeleton template is kept as-is.

### `aiDoc/modules/architecture-rules.md`

- Prime directive: architecture boundaries are strict — no cross-layer/cross-module shortcuts.
- Paradigm variants (pick per project type): **layered service** (Model, Schema/DTO, Service, Controller/Endpoint, Router), **package module** (public vs internal packages, import discipline), **plugin/command system** (registration, lifecycle, command wiring). Document the paradigm actually probed; note the variant in the file header.
- Per layer/module: base-class inheritance, field declaration style, naming, location, method-signature patterns, exception handling, pagination where applicable.
- Error-code allocation table if the project has one.
- **Every rule must cite real class names and file paths** (e.g. `app/models/common/page.py:PageRequest`).

### `aiDoc/modules/module-development.md`

Complete steps for adding a unit of work in the project's paradigm: a backend module (directory → model → schema → service → endpoint → router → registration → migration), a frontend feature (types → API function → i18n → page → routing), a library feature (implementation → public export → version-compatibility check), or a cli command (implementation → registration → help/usage text). Design principles: self-contained, follow existing patterns. Cite real reference file paths.

### `aiDoc/contracts/boundary.md`

The contract layer between the project and its consumers. Variant per project type:

- **web-api variant** (fullstack / backend / frontend): responsibility table per side; the actual unified response structure (JSON + field meanings); pagination structure if any; field naming convention (snake_case/camelCase); type bridging with conversion flow and code locations for any non-obvious conversion; time-field format/timezone if special; change rules and a pre-completion checklist. Single-sided projects document the producer or consumer contract only.
- **library variant**: the public API surface (exported symbols and their re-export locations); export/visibility contract (public vs internal); stability and version-compatibility rules (deprecation policy, SemVer mapping); change rules and a pre-completion checklist.
- **cli variant**: command specification (commands, subcommands, arguments, flags); I/O contract (stdin/stdout/stderr, output formats, stream vs file); exit-code table; backward-compatibility rules for flags and output; change rules and a pre-completion checklist.

### `aiDoc/frontend/frontend-rules.md` (frontend projects only)

Base rules (HTTP layer, state management, routing); naming conventions table (files, components, variables, API functions); type requirements; component rules (shared vs page components, props style); required steps for a new page; styling priority; i18n rules if present; environment variables; common script commands table; comment requirements.

### `aiDoc/frontend/frontend-utils.md` (frontend projects only)

Core principle: check existing utilities first, never rebuild. Inventory of the utils directory with purposes; workspace sub-package responsibilities in a monorepo; a mandatory-use table mapping scenarios to the required utility.

### `aiDoc/examples/`

- `README.md`: the example layer is instructive, not copy-paste; reading order per side; real code wins over examples when they disagree (and then the example must be updated).
- Backend-layer examples (one file per layer): `model-example.md`, `schema-example.md`/`dto-example.md`, `service-example.md`, `endpoint-example.md`/`controller-example.md`, `router-example.md`.
- Frontend: `api-example.md`, `view-example.md`, `utils-usage-example.md`.
- Library/cli: examples demonstrating the public API or command usage, one per major capability, extracted from real code (tests, docs, command definitions).
- Every example file: purpose, 2-3 core principles, an example **extracted from real project code** (sensitive data stripped), key-point explanations, and a **Real reference files** list of actual paths. If the project lacks suitable code, write code that matches the probed project style — never generic boilerplate.

### `aiDoc/memory/`

- `README.md`: long-term/ = stable user preferences; business/ = one record per business requirement; drafts are not committed.
- `project-memory.md`: index with `## Long-term` and `## Business requirements` sections, plus maintenance notes. Must be updated whenever a memory file is added or removed.
- `long-term/README.md`: record only repeatedly confirmed stable patterns; each entry has rule, applicable scenarios, source; delete stale entries.
- `business/README.md` + `business/TEMPLATE.md`: the template carries description, status (pending/in-progress/done/cancelled), backend scope, frontend scope, constraints, related files, record date. New records use the template and update both indexes.
- `lessons/README.md` + `lessons/TEMPLATE.md`: staging area for pitfalls and recurring patterns. The template carries context, pitfall/pattern, occurrence count, status (pending/promoted/dropped), promotion target, record date. Promotion discipline (second occurrence or user confirmation → rule written into the constraint body's home document in the same change) is defined in [change-docs.md](change-docs.md); `lessons/README.md` states the capture rules and carries the lesson index pointer.

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
