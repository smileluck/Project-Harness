---
name: project-pre-push-checks
description: Smallest credible set of outgoing checks before pushing — aiDoc drift sync check plus the project's own focused test/build commands, with strict pass/fail reporting.
whenToUse: Use before every push, merge request, or release handoff in this repository.
---

# Project Pre-Push Checks

Run the smallest credible set of outgoing checks. Evidence is proportional to the affected surface — do not run the full suite by reflex, and never weaken filters or thresholds to get green.

## 1. aiDoc Drift Sync Check

Run the harness drift check from the repository root:

```bash
python3 <harness>/skills/project-harness/scripts/check_sync.py .
```

`<harness>` is a placeholder — replace it with the actual install path of the Project-Harness toolkit on this machine. TODO(init): substitute the real path when this skill is installed into the project.

If the check reports drift between `AGENTS.md` / `aiDoc/` and the code, update the affected docs before pushing.

## 2. Project Test / Build Checks

TODO(init/generate): fill in this project's own commands. Select the smallest set that credibly covers the outgoing change.

| Check | Command | When required |
|---|---|---|
| Focused tests | TODO | Any logic change |
| Typecheck / lint | TODO | Any interface or type change |
| Contract tests | TODO | Any change touching `aiDoc/contracts/boundary.md` territory |
| Build / artifact smoke | TODO | Any change to build, exports, or manifests |
| Real-entry smoke | TODO | Any user-visible output change |

## 3. Reporting

- Report exact commands and results; separate passed / failed / skipped / not-run.
- A push is not successful until its observable acceptance check passes.
- If a check cannot run (missing credentials, unavailable service), say so explicitly — never mark it passed.
