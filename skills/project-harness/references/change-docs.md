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

## Handoffs

Use a handoff when another agent or person must continue unfinished work. Include:

- Exact current state (branch, base, dirty files).
- Changed files and why.
- Commands run and their results.
- Remaining work, ordered.
- Blockers and risky assumptions.
- The next safe action, named precisely.

**Discipline**: never describe an interrupted command as completed; preserve uncertainty rather than smoothing it over. Handoffs are transient — deliver them as the final message or as a task message, not as permanent repo docs, unless the project explicitly keeps a handoff log.
