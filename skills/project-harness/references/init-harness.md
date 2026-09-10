# Init workflow

Non-destructive skeleton bootstrap of a target repository. Creates only missing files; never replaces established conventions without explicit approval. Script: `scripts/init_project.py` (relative to this skill directory, e.g. `${KIMI_SKILL_DIR}/scripts/init_project.py`).

## When to use

- New or lightly documented repositories that need the full harness skeleton (`AGENTS.md`, `aiDoc/` tree, `CLAUDE.md`, tool adapters, `.agents/skills/`).
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

`--overwrite` requires explicit user approval. State exactly which files would be replaced before running it; the script writes backups before replacing anything.

## Path A: new / lightly documented repo

1. Run the initializer (after dry-run approval).
2. Tailor every generated command, path, and rule against the real project — remove placeholders that cannot be resolved, mark genuine unknowns instead of inventing them.
3. Remind the user that the skeleton is content-thin: the next step is `generate`, which probes the codebase and fills `AGENTS.md` + `aiDoc/` with real project facts (see [generate-aidoc.md](generate-aidoc.md)). Offer to run it immediately.

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
5. Report by category: **created / merged / skipped / intentionally deferred**, each with a one-line reason. Deferrals (typically: run `generate` to fill content) must be stated, not silently dropped.
