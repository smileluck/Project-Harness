# Update workflow

Refresh a target repo's harness-managed files after the toolkit (templates / scripts / references) moves to a new version.

## When to trigger

- The project-harness source repo advanced (new git tag/commit) since the target repo was initialized or last updated.
- `install.py --check` reported an outdated installed copy — update the install first (re-run `install.py`), then update the target repos initialized from it.
- Toolkit changes touched `templates/` and existing repos should pick them up.

## Version model

The harness version is the toolkit repo's `git describe --tags --always --dirty` (`unknown` when the skill runs from a detached copy). Install copies record it in their marker file; initialized repos record it in `aiDoc/.harness-manifest.json`. Equal versions short-circuit the update; `--force` re-checks file by file.

## Step 1: mechanical refresh

```sh
python3 <skill-dir>/scripts/update_harness.py <repo-root> --dry-run   # preview first
python3 <skill-dir>/scripts/update_harness.py <repo-root>
```

Interpret the report:

| Category | Meaning | Action |
|---|---|---|
| refreshed | File untouched by the project; rewritten to the expected content (template render + scan-fill + reference pruning), backup under `aiDoc/.harness-backups/` | None |
| unchanged | Already matches the expected content | None |
| user-modified | Project edited the file since the baseline; skipped | Semantic merge (Step 2) |
| removed-in-template | Template no longer ships this file; project copy kept | Review whether the copy is still wanted |
| deleted-by-user | Project deleted the file; not resurrected, dropped from the manifest | None |

The script never overwrites project-modified files. `aiDoc/.harness-manifest.json` is a machine artifact — never hand-edit it. Repos initialized before manifests existed get an `adopt` pass that only establishes the baseline (files matching the expected content are registered; diverging files are reported as project-modified and left alone).

## Step 2: semantic merge

For every `user-modified` file that should still pick up template changes:

1. Diff the project file against the current template (manifest entry's `template` path under the skill's `templates/<lang>/`).
2. Merge template-side rule changes that still apply; keep project-specific content.
3. If the merge changes rules or contracts, follow the decision-note and constraint-rewrite discipline in [change-docs.md](change-docs.md).

## Step 3: verify

Run `python3 <skill-dir>/scripts/check_sync.py <repo-root>` and resolve any drift in the same change. Report refreshed / merged / skipped / intentionally-left categories separately (see [quality-workflow.md](quality-workflow.md)).
