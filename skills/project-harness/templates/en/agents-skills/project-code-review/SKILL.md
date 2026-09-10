---
name: project-code-review
description: Semantic code review for this project — inspect the complete change, trace both sides of changed contracts, select evidence proportional to the affected surface, and report with strict pass/fail separation.
whenToUse: Use when reviewing a change before merge, when asked to review code, or before finalizing any non-trivial task in this repository.
---

# Project Code Review

## 1. Inspect the Complete Change

- Confirm the git root, branch, base, dirty state, and untracked files.
- Review committed, staged, unstaged, and relevant generated output.
- Re-establish the base after merges or rebases.

## 2. Semantic Review Checklist

- [ ] Both sides of every changed contract traced (producer and consumer)
- [ ] Lifecycle, cancellation, and disposal handled wherever resources are acquired
- [ ] Error reporting surfaces actionable information at the right layer
- [ ] Security boundaries enforced at the executing operation, not assumed upstream
- [ ] Migration and rollback paths exist for persistent data and wire/config format changes
- [ ] Retained state has one authoritative owner
- [ ] Documentation matches behavior, defaults, errors, configuration, persistent/wire fields, and public interfaces
- [ ] For each test claimed as evidence: verify the test would actually fail on the intended regression

Automated checks do not prove prose accuracy — verify docs against behavior by reading both.

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

- Report exact commands and results.
- Separate passed, failed, skipped, unavailable, and not-run checks.
- A push, merge, deployment, or interrupted process is not successful until its observable acceptance check passes.
- Name the exact next action and preserve uncertainty; the reader must not need to reconstruct earlier status messages.
