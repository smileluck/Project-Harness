<!-- last-updated: {{DATE}} -->
# Decision Notes

`aiDoc/notes/` stores the motivation, conclusion, and consequences of non-trivial decisions. A decision record answers "why", not "what is currently true" — current facts live in the corresponding aiDoc child documents.

## When to Write a Note

Add or update a note when a change involves any of:

- Behavior change (perceptible to users or callers)
- Architecture change (layering, module boundaries, dependency direction)
- Shared-contract change (APIs, data formats, config formats, persistent data structures)
- Process / tooling / test-strategy change
- Any other decision likely to be revisited or reversed

## Directory Structure and Naming

`notes/<lifecycle>/<class>/yyyy-mm-dd-topic.md`

- **Lifecycle**: `proposed/` (submitted, still under review) → `implemented/` (current shipped decision; update facts in place) → `rejected/` (declined proposal, kept only while its rationale prevents repeating a mistake)
- **Class**: `feature` / `bug-fix` / `simplification` / `architecture` / `process` / `testing`; extend only on a real classification gap, and register the extension in this file

## Maintenance Discipline

1. Use [TEMPLATE.md](TEMPLATE.md) for every new note.
2. **Never invent alternatives** — record only alternatives genuinely considered and the reasons they lost.
3. **No changelog on implemented notes**: update the body in place when facts change; a decision record is a snapshot of the current conclusion, not a history log.
4. **Reversing an old decision creates a new note**: the new and old records cross-link each other; the old one moves into `rejected/` or is marked superseded in place.
5. A note may be deleted when it is fully obsolete with no mistake-prevention value; every record must state its acceptance criteria / risks / consequences clearly enough for a later reader to judge whether it still holds.
