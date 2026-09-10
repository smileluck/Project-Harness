<!-- last-updated: {{DATE}} -->
# Frontend-Backend Boundary

Data contract and responsibility split between frontend and backend. Both sides of every changed contract must be traced before work is called done.

For backend-only projects, treat this file as the API contract for external consumers; for frontend-only projects, as the API consumption contract.

## Responsibility Boundary

TODO: who owns what. Example rows — replace with the real split:

| Concern | Backend | Frontend |
|---|---|---|
| Validation | TODO | TODO |
| Error presentation | TODO | TODO |
| Pagination state | TODO | TODO |

## Unified Response Structure

TODO: paste the real JSON envelope and explain each field. Cite the defining code path.

```json
TODO
```

| Field | Meaning |
|---|---|
| TODO | TODO |

## Unified Pagination Structure

TODO: fields and semantics; cite the defining code. Remove this section if the project has no shared pagination shape.

## Field Naming

TODO: `snake_case` / `camelCase` on the wire, and where any conversion happens (cite the code).

## Key Type Bridging

TODO: any non-obvious type conversions across the boundary (e.g. bool ↔ string, decimal ↔ string). For each, document the conversion flow and every code location involved.

## Time Fields

TODO: wire format and timezone handling, if the project has special handling; otherwise remove this section.

## Change Rules

- Never change a contract field unilaterally; change producer and consumer in the same change, or in a documented sequence recorded in `../notes/`.
- Update this file in the same change as any contract change.
- Record non-obvious contract decisions in `../notes/`.

## Pre-Completion Checklist

- [ ] Both sides of the changed contract traced and updated
- [ ] Field types and naming match this file
- [ ] Contract tests or real-entry smoke ran and passed
- [ ] This file updated if the contract changed
