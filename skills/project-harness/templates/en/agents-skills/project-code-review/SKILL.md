---
name: project-code-review
description: Semantic code review for this project — inspect the complete change, trace both sides of changed contracts, select evidence proportional to the affected surface, and report with strict pass/fail separation.
whenToUse: Use when reviewing a change before merge, when asked to review code, or before finalizing any non-trivial task in this repository.
---

# Project Code Review

Full, semantic-level review of changes in this repository. The goal is not style nitpicks but confirming the change holds up on contracts, lifecycle, error paths, and test validity.

## 1. Inspect the Complete Change

- Confirm the git root, branch, base, dirty state, and untracked files.
- Review committed, staged, unstaged, and relevant generated output.
- Re-establish the base after merges or rebases.
- Never review only a local fragment of `git diff` without its context.

## 2. Semantic Review Checklist

Check item by item; every finding must cite file and line number:

- **Both sides of changed contracts**: producer and all consumers of a changed interface / data structure / config are synchronized; renames, removed fields, and changed semantics leave no missed call sites
- **Lifecycle**: resource creation/destruction, cancellation paths, async task exit, and subscription cleanup are complete
- **Error reporting**: errors swallowed, misclassified, or losing context; error responses predictable for callers
- **Security boundaries**: auth is enforced where the operation actually executes, not only at the outer layer; input validation covers new paths; never output sensitive information
- **Migration and rollback**: persistent data, config, and wire-format changes have a migration path and a rollback route
- **State ownership**: retained state has a single authoritative owner; no double maintenance
- **Test validity**: verify the relevant tests would actually fail on the intended regression (not always-green); tests assert behavior, not implementation details
- **Documentation consistency**: docs match behavior, defaults, errors, config options, and public interfaces — automated checks passing does not prove prose accuracy

## 3. Evidence Selection

Evidence must be proportional to the affected surface.

| Affected surface | Minimum evidence |
|---|---|
| Logic change | Focused owning tests; add adjacent tests when a shared contract changes |
| Types or public interfaces | Typecheck plus consumer or contract tests |
| User/model-visible output | Snapshot, E2E, or runnable example at the real entry path |
| Build, exports, manifests, generated artifacts | Build plus built-artifact smoke |
| Documentation | Link, formatting, and example checks owned by the project |
| Provider or integration behavior | Real integration test when credentials and authority are available; never print secrets |

- Never run the full suite by reflex; reserve it for repository-wide changes, CI diagnosis, or explicit requests.
- Never weaken filters or thresholds merely to produce green output.

## 4. Reporting Discipline

- Report exact commands and real results.
- Classify results as passed / failed / skipped / unavailable / not-run — never merge categories.
- An interrupted process is not successful; judge by the observable acceptance check.
- Output format:

```
## Review conclusion
[pass / blocking issues / suggestions only]

## Blocking issues (must fix)
- [file:line] problem description and suggestion

## Suggestions (optional)
- [file:line] problem description

## Verification evidence
| Command | Result |
|---|---|
| `...` | passed/failed/skipped/unavailable/not-run |

## Uncovered risks
[what this review could not verify]
```
