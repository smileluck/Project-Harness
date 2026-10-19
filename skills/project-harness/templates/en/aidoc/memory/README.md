<!-- last-updated: {{DATE}} -->
# Memory Layer

`aiDoc/memory/` is the AI memory layer, preserving user preferences, business requirements, and lessons learned across sessions. It stores "context and preferences" only, never rule bodies — stable rules belong in `/AGENTS.md` or the matching aiDoc child document; decision rationale lives in [../notes/](../notes/).

## Directory Guide

| Directory | Contents |
|---|---|
| `long-term/` | Stable user preferences and collaboration style, valid across tasks and sessions |
| `business/` | One record per business requirement raised by the user |
| `lessons/` | Staging area for pitfalls and recurring patterns; once the promotion condition is met, the rule is written into the constraint body |
| `project-memory.md` | Index of all memory entries |

## Usage Rules

- When the user raises a business requirement, AI must add or update one `business/` record and update the index in `project-memory.md`.
- When work hits a pitfall, review flags the same class of problem repeatedly, or a reusable pattern emerges, one `lessons/` record must be added in the same change; on recurrence increment its count in place, and at the second occurrence promote it into the constraint body per `lessons/README.md`.
- When a lesson settles into a stable pattern, distill it into `long-term/`.
- Temporary drafts are never committed; stale memories are cleaned up promptly, with the index cleaned up in sync.
