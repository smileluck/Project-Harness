<!-- last-updated: {{DATE}} -->
# Memory Layer

`aiDoc/memory/` is the AI memory layer.

## Directory Guide

- `long-term/` — stable user preferences and collaboration constraints, valid across tasks and sessions
- `business/` — one record per business requirement raised by the user

## Usage Rules

- When the user raises a business requirement, AI must add or update one `business/` record and update the index in `project-memory.md`.
- When a pattern proves stable through repeated use, distill it into `long-term/`.
- Temporary drafts are never committed.
