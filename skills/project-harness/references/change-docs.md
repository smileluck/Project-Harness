# Record workflow: decision notes, change plans, handoffs

Use separate records because execution state and durable rationale age differently. Paths below are inside the target repository. Templates: `templates/<lang>/aidoc/notes/` and `templates/<lang>/aidoc/plans/` (relative to this skill directory).

## Decision notes

### When to write one

Add or update a note when a change alters any of:

- Observable behavior
- Architecture or layering
- A shared contract (API, schema, wire format, config format)
- Process or tooling
- Testing strategy
- Persistent data or migrations
- Any decision likely to be revisited later

Mechanical, behavior-preserving edits (renames, formatting, refactors with identical behavior) need no note.

### Location and naming

```
aiDoc/notes/<lifecycle>/<class>/yyyy-mm-dd-topic.md
```

**Lifecycle**:

| Lifecycle | Meaning |
|---|---|
| `proposed` | Substantial future work under review |
| `implemented` | Shipped current decision; keep paths and facts current |
| `rejected` | Declined proposal, retained only while its rationale prevents a plausible mistake |

**Classes**: `feature`, `bug-fix`, `simplification`, `architecture`, `process`, `testing`. Extend only when the project has a real classification gap.

### Content and discipline

Every note includes: the problem, the proposal/decision, genuine alternatives considered, and acceptance criteria + risks (proposed) or consequences (implemented).

- **Never invent alternatives** to make the note look thorough — record only what was actually considered.
- **Constraints are rewritten, not just noted**: when the decision changes an architecture, contract, or process constraint, update the constraint's home document (`modules/architecture-rules.md`, `contracts/boundary.md`, or `AGENTS.md`) in the same change. The note records why; the rule doc must say what now holds.
- An `implemented` note is updated **in place** as facts change; do not append a change log.
- A reversal gets a **new** note, cross-linked to the one it supersedes; move the old note per its new status.
- Update `aiDoc/notes/` indexes (and the `aiDoc/README.md` routing metadata if the file set changed) in the same change.

## Change plans

### When to write one

Create `aiDoc/plans/active/yyyy-mm-dd-topic.md` for work that is multi-step, cross-component, risky, or delegated. Single-file, low-risk changes need no plan.

### Content

- Objective, non-goals, assumptions, affected areas, acceptance criteria.
- Work items with owners, dependencies, and advisory write scopes (see [collaboration.md](collaboration.md)).
- Validation commands and rollback/migration requirements.
- Current decisions, blockers, and handoff state.

### Discipline

- Update the plan as work changes; it is the live execution record.
- On completion: summarize the delivered outcome and move the file to `aiDoc/plans/completed/`. Delete it only if it has no durable value.
- A completed plan is evidence of execution, **not** the authority for current behavior — that authority lives in `AGENTS.md`/`aiDoc/` docs and the decision notes.

## Lessons

Lessons are the capture layer of rule self-evolution: pitfalls and recurring patterns recorded at `aiDoc/memory/lessons/yyyy-mm-dd-topic.md` (templates: `templates/<lang>/aidoc/memory/lessons/`). **Once is an incident, twice is a pattern.**

Every lesson carries a header `lesson-meta` marker — `<!-- lesson-meta: status=pending count=1 post=0 target= -->` — which is the sole basis for mechanical scanning (`check_sync.py` checks 5/6). Keep the marker in sync with the human-readable sections on every add/increment/promote; machines never parse heading text.

### When to record one

Record a lesson in the same change when work hits a pitfall, review flags the same class of problem repeatedly, or a reusable pattern emerges. Keep it light — five lines per the template. On recurrence of an equivalent lesson, increment its occurrence count in place (and `count` in the marker); never file a duplicate.

### Promotion discipline

- Trigger: the same lesson occurs a 2nd time, or the user confirms explicitly.
- Action: in the **same change**, write the rule into the constraint body's home document (`modules/architecture-rules.md`, `contracts/boundary.md`, `frontend/frontend-rules.md`, or `AGENTS.md` — by content ownership); set the lesson status to `promoted` with a cross-link to the target section, and set the marker's `status=promoted` plus `target=<rule-home-file>`.
- Deferral: a `pending` entry with count ≥ 2 whose promotion is deliberately postponed must be marked `deferred` with the reason recorded in the lesson's promotion-target section; the [sync workflow](sync-aidoc.md) re-examines whether the reason still holds.
- If the promotion alters behavior, architecture, or contracts, a decision note is still required (the note records why; the constraint doc says what now holds).
- Mark `dropped` only for entries confirmed to have no general value, with the reason recorded.
- Never stockpile lessons without promoting; `check_sync.py` check 5 fails the drift gate on unhandled `pending` entries with count ≥ 2.
- Update the lesson index in `aiDoc/memory/project-memory.md` in the same change as any lesson add/increment/promote.

### Recurrence after promotion

If the same problem recurs after promotion, the promoted rule was ineffective: increment `post` in the marker, **revise the promoted rule body** in the same change (never file a new lesson for it), and record a decision note on why the first rule failed to prevent it. `check_sync.py` check 6 lists `post ≥ 1` entries as hints so the sync workflow re-validates them.

## Handoffs

Use a handoff when another agent or person must continue unfinished work. Include:

- Exact current state (branch, base, dirty files).
- Changed files and why.
- Commands run and their results.
- Remaining work, ordered.
- Blockers and risky assumptions.
- The next safe action, named precisely.

**Discipline**: never describe an interrupted command as completed; preserve uncertainty rather than smoothing it over. Handoffs are transient — deliver them as the final message or as a task message, not as permanent repo docs, unless the project explicitly keeps a handoff log.
