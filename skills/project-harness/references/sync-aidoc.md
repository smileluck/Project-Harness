# Sync workflow

Detect drift between the aiDoc documentation system and the code, then resync incrementally. Mechanical checks run first via `scripts/check_sync.py` (relative to this skill directory); semantic drift is handled by the agent.

## When to trigger

- **Mandatory completion gate**: before closing out any code or doc change, run the Step 1 mechanical check (or the scoped manual equivalent against the `aiDoc/README.md` routing table when the script is unavailable). This is a required step of every change, not an optional audit; drift found here is fixed in the same change, never deferred.
- Architecture changed: layering adjustments, top-level directories added/removed, stack replaced.
- Backend modules or frontend pages added/removed — `aiDoc/modules/`, `aiDoc/examples/`, `aiDoc/relations/system-map.md` may be stale.
- aiDoc sub-documents added/removed — the `aiDoc/README.md` routing table and the `AGENTS.md` quick-reference may be stale.
- Routing tables or examples visibly diverge from real code.
- Before relying on aiDoc docs for a large task, when their freshness is unknown.

Small changes (one endpoint, one page) do not need full sync — a targeted `--scope` update is enough.

## Step 1: mechanical check

```sh
python3 <skill-dir>/scripts/check_sync.py <repo-root>
```

Interpret the report:

| Finding | Meaning | Action |
|---|---|---|
| Indexed path missing | Routing table or entries reference a deleted file | Regenerate `aiDoc/README.md`; fix the referencing doc |
| Unindexed aiDoc file (entries dictionary) | A doc-type aiDoc file is not registered in the `aiDoc/README.md` common-entries dictionary | Register it in the entries dictionary (+ routing table if also unlisted), same change |
| Referenced code path missing | Docs cite moved/deleted source | Regenerate the citing document via `--scope` |
| Missing / invalid `last-updated` header | An aiDoc doc lacks `<!-- last-updated: YYYY-MM-DD -->` in its first 5 lines | Add the header when updating the doc |
| Section mismatch (hint) | `AGENTS.md` mentions aiDoc areas that don't exist, or existing areas go unmentioned | Fix the `AGENTS.md` quick-reference |
| Unhandled lesson (`pending` count ≥ 2, or `promoted` without `target`) | Lesson promotion discipline violated | Apply the promotion discipline in [change-docs.md](change-docs.md) |
| Lesson not scannable / recurrence after promotion (hint) | Missing `lesson-meta` marker, or `post ≥ 1` | Add the marker; re-verify the promoted rule per the recurrence loop in [change-docs.md](change-docs.md) |

The script does **not** check example validity ("real reference files" freshness) — that is Step 2 item 3 below — nor whether a doc is newer than the code it describes; both are semantic judgments.

The script only proves mechanical facts. A clean report does **not** mean the docs are semantically correct.

### `relations/code-index.md` lifecycle

`code-index.md` is machine-owned; its lifecycle and the regeneration command are defined in [aidoc-structure.md](aidoc-structure.md) (single source) — never patch it by hand. Drift findings in the hand-written `relations/` docs (repo-profile, system-map, development-workflow) are resolved by the generate workflow, using the fresh `code-index.md` as the fact base.

## Step 2: semantic drift checklist

Verify by reading code and docs together:

1. **Symbol existence**: class/function names cited in `contracts/boundary.md` and `modules/architecture-rules.md` still exist in code (Grep each).
2. **Contract fidelity**: response/pagination structures in `boundary.md` match the actual serializers; field naming convention matches real payloads.
3. **Example validity**: each example's "real reference files" exist **and** the example still matches those files' current patterns.
4. **Routing consistency**: `aiDoc/README.md` routing table and common entries match the actual aiDoc file set; `AGENTS.md`'s "task family → aiDoc area" quick-reference matches existing aiDoc areas.
5. **Stack accuracy**: `relations/repo-profile.md` matches current manifests (dependencies added/removed).
6. **Command validity**: commands in `relations/development-workflow.md` and `AGENTS.md` still run (spot-check the risky ones).
7. **Lesson promotion sweep**: consume the mechanical results of `check_sync.py` checks 5/6 — resolve blocking items per the promotion and deferral discipline in [change-docs.md](change-docs.md); for every `deferred` entry, re-examine whether the recorded reason still holds. For `post ≥ 1` entries the promoted rule proved ineffective — apply the recurrence-after-promotion loop in [change-docs.md](change-docs.md).

## Step 3: resync

Choose the narrowest sufficient mode of the [generate workflow](generate-aidoc.md):

| Drift scope | Mode |
|---|---|
| Scattered staleness across areas, uncertain extent | `generate --incremental` |
| One area (modules / contracts / frontend / relations / memory / notes / plans / core) | `generate --scope <area>` |
| Widespread drift, most docs stale | full `generate` |

Always regenerate `aiDoc/README.md`'s routing table and the `AGENTS.md` quick-reference whenever the aiDoc file set changed — they are cross-file metadata and do not self-heal.

## Step 4: report

Report: mechanical findings (verbatim from the script), semantic findings (file → drift → evidence), files regenerated, and anything intentionally left stale with the reason. Reporting discipline (passed / failed / skipped / unavailable / not-run) is defined in [quality-workflow.md](quality-workflow.md).
