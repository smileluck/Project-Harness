<!-- last-updated: {{DATE}} -->
# Decision Notes

`aiDoc/notes/` stores decision records: why a non-trivial decision won. Execution state lives in `../plans/`; durable rationale lives here — the two age differently.

## When to Write a Note

Add or update a note when a change alters: behavior, architecture, a shared contract, process/tooling, testing strategy, persistent data, wire/config formats, or any other decision likely to be revisited.

## Directory Structure and Naming

`notes/<lifecycle>/<class>/yyyy-mm-dd-topic.md`

### Lifecycle

| Lifecycle | Meaning |
|---|---|
| `proposed` | Substantial future work under review |
| `implemented` | Shipped current decision; keep paths and facts current |
| `rejected` | Declined proposal, retained only while its rationale prevents a plausible mistake |

### Class

`feature` / `bug-fix` / `simplification` / `architecture` / `process` / `testing` — extend only when the project has a real classification gap, and update this file when you do.

## Maintenance Discipline

- Use `TEMPLATE.md` for every new note.
- Never invent alternatives — record only alternatives that were genuinely considered.
- Do not append a changelog to an implemented note; update current facts in place.
- Reversing a decision creates a new note cross-linked to the old one; update the old note's lifecycle accordingly.
- Promote a note by moving the file between lifecycle directories; keep the filename stable so links survive.
