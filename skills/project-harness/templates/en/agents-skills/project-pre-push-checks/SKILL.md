---
name: project-pre-push-checks
description: Smallest credible outgoing checks before pushing — doc drift detection, project validation proportional to the affected surface, and aiDoc / decision-record completeness.
whenToUse: Use when the user is about to push, merge a branch, or asks for "pre-push / pre-commit checks".
---

# Project Pre-Push Checks

Run the smallest credible set of outgoing checks before pushing. The goal is to catch three classes of problems — doc drift, missing validation, incomplete records — not to replace CI.

## Check flow

Execute in order; if any blocking item fails, stop and report. Never skip steps.

### 1. Confirm the change scope

- Confirm the git root, branch, and difference against the remote (list of commits to be pushed)
- List every file touched by this push

### 2. Doc drift detection (sync)

Run the harness drift check from the repository root:

```bash
python3 <harness>/skills/project-harness/scripts/check_sync.py .
```

> Note: the toolkit path in the command is rendered by init to the real executable path for this repository; if it is still in placeholder form, replace it manually with the Project-Harness checkout location. The script checks whether `AGENTS.md` / `aiDoc/` indexes, path references, and code have drifted.

- Drift reported by the script must be fixed, or the reason explicitly stated in the report
- If the target project has no aiDoc system yet (the script reports it missing), skip this step and mark it not-run in the report

### 3. Project validation (proportional to the affected surface)

<!-- TODO: init/generate fills these command placeholders from the project's real toolchain -->

| Check | Command | When required |
|---|---|---|
| Typecheck | `TODO:` | Interface / type changes |
| Focused tests | `TODO:` | Logic changes |
| Build | `TODO:` | Build config / exports / artifact changes |
| Lint / format | `TODO:` | When configured in the project |

- No reflexive full-suite runs; select per the `aiDoc/README.md` routing and the root `AGENTS.md` operating invariants
- Never weaken filters or thresholds to get green

### 4. Record completeness

Confirm against the actual change:

- [ ] Behavior / architecture / contract / process / testing-strategy change → a matching decision record exists in `aiDoc/notes/`
- [ ] Multi-step change → the plan in `aiDoc/plans/active/` is up to date
- [ ] aiDoc sub-documents added/removed → `aiDoc/README.md` index and routing table synchronized
- [ ] New business requirement from the user → recorded in `aiDoc/memory/business/` with the index updated

### 5. Outgoing report

```
## Pre-push check results

### Drift detection
[check_sync.py result: passed / failed (with output) / not-run (reason)]

### Project validation
| Command | Result |
|---|---|
| `...` | passed/failed/skipped/not-run |

### Record completeness
[item-by-item: passed / failed / not applicable]

### Conclusion
[ready to push / blockers: list them]
```

- The push itself is not this skill's success criterion; whether a push succeeded is judged by its observable result afterwards
