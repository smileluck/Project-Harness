<!-- last-updated: {{DATE}} -->
# Lesson Memory

Stores pitfalls hit during development and patterns observed recurring. This directory is a **staging area for experience**: lessons are captured here at low cost, and once the promotion condition is met the rule is written into the constraint body's home document (`/AGENTS.md`, `modules/architecture-rules.md`, `contracts/boundary.md`, etc.) — this directory keeps only the record and the outbound link.

## Rules

- When work hits a pitfall, review flags the same class of problem repeatedly, or a reusable pattern emerges, one lesson must be recorded in the same change.
- When an equivalent lesson already exists, **increment its occurrence count in place** — never file a duplicate.
- Use [TEMPLATE.md](TEMPLATE.md) for new records (keep it light — five lines).
- After recording or incrementing, update the index in [../project-memory.md](../project-memory.md).
- Naming: `yyyy-mm-dd-topic.md`.

## Promotion Discipline

- Trigger: the same lesson occurs a 2nd time, or the user confirms explicitly — **once is an incident, twice is a pattern**.
- Action: in the same change, write the rule into the constraint body's home document; set this record's status to `promoted` and fill in the promotion target link.
- If the promotion alters behavior, architecture, or contracts, a decision note per `aiDoc/notes/README.md` is still required.
- Entries confirmed to have no general value are marked `dropped`, with the reason recorded.
- Never stockpile lessons without promoting; the sync workflow sweeps `pending` entries with count ≥ 2 as a backstop.

## Lesson Index

None yet.
