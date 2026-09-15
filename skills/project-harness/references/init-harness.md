# Init workflow

Non-destructive skeleton bootstrap of a target repository. Creates only missing files; never replaces established conventions without explicit approval. Script: `scripts/init_project.py` (relative to this skill directory, `<skill-dir>/scripts/init_project.py`).

## When to use

- New or lightly documented repositories that need the full harness skeleton (`AGENTS.md`, `CLAUDE.md`, `aiDoc/` tree, `.agents/skills/`; tool adapters are added by the generate workflow, not by init).
- Mature repositories as a **gap audit**: fill only missing pieces, merge with what exists.

## Preflight

Resolve the real Git root — never initialize into the shell's working directory merely because it is the workspace root. Then inspect:

- `git status --short --branch`, remotes, default branch.
- Manifests and the actual lockfile (determine the real package manager).
- Existing `AGENTS.md`, `CLAUDE.md`, `docs/`, `.claude/`, `.cursor/`, contribution docs, ADR/RFC folders, issue templates, local skills.
- Build/lint/typecheck/test/CI commands from manifests and workflows.
- Monorepo boundaries and subtrees that might need nested `AGENTS.md`.

## Always preview first

```sh
python3 <skill-dir>/scripts/init_project.py <repo-root> --dry-run
python3 <skill-dir>/scripts/init_project.py <repo-root>
```

The script creates only missing files and reports existing destinations as `SKIP`. Review the dry-run output with the user before the real run.

### Static scan (default)

Init runs a zero-dependency static scan (`scripts/scan_repo.py`) by default; `--no-scan` disables it. The scan parses language manifests (`package.json`, `pyproject.toml`/`requirements.txt`, `go.mod`, `pom.xml`/`build.gradle`, `CMakeLists.txt`/`Makefile`, `*.pro`), takes `git ls-files` structure statistics, and detects components — mixed projects supported, each component a `(path, kind, language/framework, evidence)` tuple. It produces:

1. Pre-filled sections in the newly generated `relations/repo-profile.md`, `relations/development-workflow.md`, and `relations/system-map.md` — each auto-filled section carries the marker `<!-- auto-scan: init 扫描生成，generate 工作流校订后移除此标记 -->`. Fill points are explicit `<!-- scan-fill:<key> -->` markers embedded in the templates (next to the section heading), so section titles can be reworded freely without breaking the fill.
2. The machine artifact `aiDoc/relations/code-index.md`, always regenerated on each run (lifecycle and regeneration command: [aidoc-structure.md](aidoc-structure.md)).

In the completion report, group scan-filled files under **auto-filled** (distinct from plain `created`), so the user knows which content still needs `generate`-workflow calibration. With `--no-scan`, `code-index.md` keeps its skeleton template and no sections are pre-filled; it can be generated later with the regeneration command defined in [aidoc-structure.md](aidoc-structure.md).

`--overwrite` requires explicit user approval. State exactly which files would be replaced before running it; the script writes backups before replacing anything.

Every run finishes by writing `aiDoc/.harness-manifest.json` — the toolkit version plus a sha256 baseline of every file the run wrote. It is the mechanical baseline the [update workflow](update-harness.md) uses to tell template-faithful files from project-modified ones; never hand-edit it.

## Path A: new / lightly documented repo

1. Run the initializer (after dry-run approval). The skeleton adapts to six project types — `fullstack` / `backend` / `frontend` / `library` / `cli` / `general` — plus `mixed` for multi-component repos detected by the scan, and only the `frontend/` area is conditional (created only when a real frontend exists); all other aiDoc areas are created for every type.
2. Tailor every generated command, path, and rule against the real project — remove placeholders that cannot be resolved, mark genuine unknowns instead of inventing them.
3. **Default: continue directly into the `generate` workflow** (see [generate-aidoc.md](generate-aidoc.md)) — calibrate the auto-filled sections (removing their markers), probe the codebase, and fill `AGENTS.md` + `aiDoc/` with real project facts. Init and generate are one continuous onboarding run; do not stop after scaffolding. Stop at the skeleton only when the user asked for skeleton-only or passed `--no-generate` — in that case state explicitly that `generate` remains the pending next step.

## Path B: mature repo (gap audit)

1. Inventory what already exists: root/nested `AGENTS.md`, `CLAUDE.md`, `docs/`, ADRs/RFCs, `.claude/commands/`, other tool directories, CI workflows.
2. Classify each harness component as **present / missing / conflicting**.
3. Create only missing pieces. For existing files, **merge** — add the missing load-model or routing sections into the established file; never replace an established ADR, RFC, or contribution workflow with the aiDoc system wholesale.
4. Where conventions conflict (e.g. an existing docs tree vs `aiDoc/`), present the conflict and let the user choose; a new documentation system is not automatically better.
5. Add tool adapters only for tool directories actually present (see [tool-adapters.md](tool-adapters.md)).

## Completion checklist

Before handing off an initialized harness:

1. Remove or resolve every generated `TODO` that can be learned from the repository; mark the rest as explicit unknowns.
2. Verify every link and command points to a real file or script that executes.
3. Run the dry-run again — a second default run must create nothing and change nothing (idempotence).
4. Confirm the load chain works: `CLAUDE.md` contains `@AGENTS.md` (where applicable), `AGENTS.md` routes to `aiDoc/README.md`, adapters point at the canonical files.
5. Report by category: **created / auto-filled / merged / skipped / intentionally deferred**, each with a one-line reason. **auto-filled** covers the scan-filled `relations/` sections and `relations/code-index.md`. When the run continues into `generate` (the default), this checklist applies after `generate` completes and "markers await calibration" never appears in the final report; in a skeleton-only run (`--no-generate`), the pending `generate` step must be stated as an explicit deferral, not silently dropped.
