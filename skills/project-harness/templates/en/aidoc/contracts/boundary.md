<!-- last-updated: {{DATE}} -->
# Contract Layer

Interface contract and responsibility split across this project's public boundary. Both sides of every changed contract must be traced before work is called done.

The body below is organized per paradigm. The generate workflow keeps the variant matching this project and deletes the rest.

<!-- mixed projects: describe the contracts between components (e.g. web frontend ↔ server API, Qt UI ↔ core library interface) -->

## Responsibility Boundary

TODO: who owns what, stated as producer side vs consumer side. Example rows — replace with the real split:

| Concern | Producer side | Consumer side |
|---|---|---|
| Validation | TODO | TODO |
| Error presentation | TODO | TODO |
| State ownership | TODO | TODO |

<!-- variant: web-api — the generate workflow keeps the matching variant and deletes the rest -->

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

<!-- variant: library — the generate workflow keeps the matching variant and deletes the rest -->

## Public API Surface

TODO: list the exported symbols that constitute the public API, with their defining paths.

## Export Contract

TODO: what is exported from where, naming and stability expectations for each export.

## Version Compatibility Promises

TODO: semantic-versioning policy, deprecation procedure, backward-compatibility guarantees.

<!-- variant: cli — the generate workflow keeps the matching variant and deletes the rest -->

## Command Spec

TODO: one entry per command — name, purpose, defining code path.

## Argument / IO Contract

TODO: flags, positional arguments, stdin/stdout/stderr expectations, output formats.

## Exit-Code Conventions

TODO: exit-code meanings and which conditions map to which code.

## Change Rules

- Never change a contract field unilaterally; change producer and consumer in the same change, or in a documented sequence recorded in `../notes/`.
- Update this file in the same change as any contract change.
- Record non-obvious contract decisions in `../notes/`.

## Pre-Completion Checklist

- [ ] Both sides of the changed contract traced and updated
- [ ] Field types and naming match this file
- [ ] Contract tests or real-entry smoke ran and passed
- [ ] This file updated if the contract changed
