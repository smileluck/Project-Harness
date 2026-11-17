<!-- last-updated: {{DATE}} -->
# Contract Layer (boundary)

> Entry point for producer and consumer contracts. Use real code to document the conventions that apply to this project's paradigm.

## Contract Surface Index

<!-- Small projects can use one file. When surfaces change independently, move their details into sibling pages and keep shared conventions here. Index each page with its route prefix, public symbol, or subcommand and a link such as [Surface name](./<file>.md). -->

## Responsibility Boundary

<!-- TODO: fill per the actual responsibility split; describe the two sides as "producer side / consumer side" — not limited to frontend/backend -->

| Responsibility | Owner |
|---|---|
| TODO: e.g. data validation / business rules / auth | Producer side |
| TODO: e.g. instant form feedback / display formatting | Consumer side |

<!-- variants: web-api / library / cli — the generate workflow keeps the matching variant and deletes the rest -->
<!-- mixed projects: describe the contracts between components (e.g. web frontend ↔ server API, Qt UI ↔ core library interface) -->

## web-api variant: HTTP interface contract

### Unified Response Structure

<!-- TODO: fill the JSON structure and field explanations from real code, citing the code location that defines the structure -->

```json
TODO: real response structure example
```

| Field | Type | Description |
|---|---|---|
| TODO: | TODO: | TODO: |

Defined at: TODO: (e.g. `app/schemas/response.py:ResponseModel`)

### Unified Pagination Structure

<!-- TODO: if there is a pagination convention, fill field explanations and code location; otherwise remove this section -->

| Field | Type | Description |
|---|---|---|
| TODO: | TODO: | TODO: |

### Field Naming

<!-- TODO: the actual snake_case / camelCase convention, including whether the two sides convert and at which layer the conversion happens -->

TODO:

### Key Type Bridging

<!-- TODO: special type conversions (e.g. bool ↔ string, Decimal ↔ number, enum ↔ label) must be documented in detail with the conversion flow and every code location involved; write "none" if not applicable -->

TODO:

### Time Fields

<!-- TODO: format and timezone convention (e.g. ISO 8601 / UTC), including the serialization location; remove this section if there is no special handling -->

TODO:

## library variant: public API contract

### Public API Surface

<!-- TODO: list the public symbols exposed to callers (functions / classes / constants), citing their defining code locations; internal implementation symbols do not belong here -->

TODO:

### Export Contract

<!-- TODO: package entry, public export paths, and submodule visibility conventions (which submodules are stable exports) -->

TODO:

### Version Compatibility Promises

<!-- TODO: semantic-versioning policy, breaking-change criteria, and the deprecation process -->

TODO:

## cli variant: command-line contract

### Command Spec

<!-- TODO: list all commands and subcommands with their purpose, citing the defining location (e.g. the command registry) -->

TODO:

### Argument / IO Contract

<!-- TODO: naming conventions for arguments and options, input/output formats (stdout/stderr split, machine-readable output conventions) -->

TODO:

### Exit-Code Conventions

<!-- TODO: a complete table of exit-code meanings, citing the code location defining the exit-code constants -->

TODO:

## Change Rules

1. Adding / renaming / deleting a contract field is an interface change; both sides (producer and consumer) must be synchronized
2. Contract changes must run typecheck + contract-level tests (see the root `AGENTS.md` operating invariants)
3. Breaking changes require a decision note first (see [../notes/README.md](../notes/README.md)), describing migration and rollback

## Pre-Completion Checklist

- [ ] Field names, types, and nullability match on both sides
- [ ] Type bridging happens at the agreed location, not scattered around
- [ ] Error responses are predictable to the consumer (consistent error code/message structure)
- [ ] Tests cover the contract change points
