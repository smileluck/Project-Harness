# Review, verification, and reporting

Evidence must be proportional to the affected surface. Never claim checks that were not run.

## Inspect the complete change

Before reviewing or reporting, establish the full picture:

- Git root, current branch, merge base, dirty state, untracked files.
- Review **all** of: committed changes, staged changes, unstaged changes, and relevant generated artifacts.
- After any merge or rebase, re-establish the base — earlier inspection results are void.

## Select evidence by affected surface

| Affected surface | Evidence |
|---|---|
| Logic change | Focused owning tests; add adjacent tests when a shared contract changes |
| Types or public interfaces | Typecheck plus consumer or contract tests |
| User/model-visible output | Snapshot, E2E, or runnable example at the real entry path |
| Build, exports, manifests, workers, generated artifacts | Build plus built-artifact smoke test |
| Documentation | Link checks, generation, formatting, example verification owned by the project |
| Provider/integration behavior | Real integration test when credentials and authority are available; never print secrets |
| aiDoc documentation | `scripts/check_sync.py` plus the semantic checks in [sync-aidoc.md](sync-aidoc.md) |

Do not run a full suite by reflex. Reserve it for repository-wide changes, CI diagnosis, or explicit requests. Never weaken filters or thresholds merely to produce green output.

## Semantic review checklist

- **Contract symmetry**: trace both sides of every changed contract (producer and consumer, caller and callee).
- **Lifecycle**: creation, cancellation, disposal, and cleanup of anything the change introduces.
- **Error reporting**: failures surface with actionable information at the right layer.
- **Security boundaries**: authority enforced at the executing operation, not assumed from the caller; no secrets in logs or output.
- **Migration and rollback**: persistent-data changes have a migration path and a rollback story.
- **State ownership**: retained state has one authoritative owner.
- **Test efficacy**: the tests would actually fail on the intended regression — verify, don't assume.
- **Doc-behavior consistency**: documentation matches behavior, defaults, errors, configuration, persistent/wire fields, and public interfaces. Automated checks do not prove prose accuracy.

## Reporting discipline

- Report exact commands and their results.
- Separate **passed / failed / skipped / unavailable / not-run** — five distinct categories, never merged.
- A push, merge, deployment, or interrupted process is not successful until its observable acceptance check passes.
- Final responses summarize outcome, material files, validation, and remaining risks without requiring the reader to reconstruct earlier status messages.
- Handoffs name the exact next action and preserve uncertainty (see [change-docs.md](change-docs.md)).
