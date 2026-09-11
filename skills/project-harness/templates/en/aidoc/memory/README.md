<!-- last-updated: {{DATE}} -->
# Memory Layer

`aiDoc/memory/` is the AI memory layer.

## Directory Guide

- `long-term/` — stable user preferences and collaboration constraints, valid across tasks and sessions
- `business/` — one record per business requirement raised by the user
- `lessons/` — staging area for pitfalls and recurring patterns; once the promotion condition is met, the rule is written into the constraint body's home document
- `project-memory.md` — index of all memory entries

## Usage Rules

- When the user raises a business requirement, AI must add or update one `business/` record and update the index in `project-memory.md`.
- When work hits a pitfall, review flags the same class of problem repeatedly, or a reusable pattern emerges, one `lessons/` record must be added in the same change; on recurrence increment its count in place, and at the second occurrence promote it into the constraint body per `lessons/README.md`.
- When a pattern proves stable through repeated use, distill it into `long-term/`.
- Temporary drafts are never committed.
