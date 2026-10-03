# Init-set workflow (project set)

Batch onboarding for a **project set**: one parent folder holding several independent projects. Discovers member candidates, initializes project-harness in each member that lacks it, and writes a single root `AGENTS.md` at the set root for cross-project coordination. Script: `scripts/init_project_set.py` (relative to this skill directory, `<skill-dir>/scripts/init_project_set.py`).

Single-project onboarding uses [init-harness.md](init-harness.md); this workflow only adds set-level discovery, batching, and the root `AGENTS.md`. Per-member behavior is exactly the init workflow's.

## When to use

- A folder ("set root") contains several independent projects the user wants to process in one pass.
- Members that already have a harness (`aiDoc/.harness-manifest.json`) are left untouched; only unconfigured members are initialized.

The set root itself gets **only** a root `AGENTS.md` — no root-level `aiDoc/`, no root-level manifest. Each member keeps its own independent harness.

## Step 1: discovery (no writes)

```sh
python3 <skill-dir>/scripts/init_project_set.py <set-root>
```

Without `--members`/`--all` the script prints a candidate table and writes nothing: every non-hidden first-level subdirectory, annotated with whether it is an independent git root, whether a harness is already configured, which manifest files it has, and whether it is **blocked** (nested inside a parent git repo without being a git root itself — `init_project.py` refuses nested initialization there).

## Step 2: confirm the member list

Review the candidate table with the user. Directories that are neither git roots nor manifest-bearing are the user's call — never silently include or exclude them. Excluded directories simply stay out of `--members`.

## Step 3: batch run (preview first)

```sh
python3 <skill-dir>/scripts/init_project_set.py <set-root> --members a,b,c --dry-run
python3 <skill-dir>/scripts/init_project_set.py <set-root> --members a,b,c
```

(`--all` selects every candidate.) The script runs the full per-member init pipeline (skeleton + scan fill + manifest) on each unconfigured, unblocked member, skips configured members outright, and finishes by writing the set-root `AGENTS.md` from `templates/<lang>/project-set/AGENTS.md.tmpl` with the member index table filled at the `<!-- scan-fill:members -->` marker. One member's failure does not abort the batch; failures are grouped in the final report (exit code 1 if any member failed). `--overwrite` requires explicit user approval — state exactly which files would be replaced (member files are backed up per `init_project.py` rules; the root `AGENTS.md` is backed up under `<set-root>/.harness-backups/`).

## Step 4: per-member generate (default)

Every member initialized in this run continues into the `generate` workflow, one member at a time, each run anchored at that member's root (see [generate-aidoc.md](generate-aidoc.md)). There is no batch generate — run it per member. If the user asked for skeleton-only (`--no-generate` at the skill level), state explicitly that per-member generate remains the pending next step.

## Step 5: calibrate the root AGENTS.md

The member index table arrives with the auto-scan marker. Calibrate it, then write the **Inter-project relationships** section from real evidence — who depends on whom, data/interface flows, shared release cadence or contracts — backing each claim with a relative-path pointer into a member repo. Remove the auto-scan marker once calibrated. Respect the boundary rules in the template: the root file carries cross-project facts only and never duplicates member-internal content.

## Completion checklist

1. Re-run the batch command — it must create nothing and change nothing (idempotence: members report already-configured, root `AGENTS.md` reports SKIP).
2. Every member link in the root `AGENTS.md` points at a real member `AGENTS.md` / `aiDoc/README.md`.
3. The auto-scan marker in the root `AGENTS.md` is removed after calibration (or the calibration is stated as an explicit deferral).
4. Report by category per member: **initialized / skipped-configured / blocked / failed**, each with a one-line reason, plus the root `AGENTS.md` outcome.
