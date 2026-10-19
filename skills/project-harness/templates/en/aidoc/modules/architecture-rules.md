<!-- last-updated: {{DATE}} -->
# Architecture / Module Organization Rules

> Constraints this project's architecture must obey. Every rule must cite real class names and file paths from the actual code; TODO items are filled by the generate workflow from real code.

## General Principle

- Strict layering: never skip layers, never depend backwards
- Each layer interacts only through the public interface of the layer below
- TODO: this project's actual layered call chain (e.g. Endpoint → Service → Model)

<!-- variants: layered service / package-module structure / plugin system, etc. — the generate workflow keeps the matching variant and deletes the rest; the layer section titles below adapt to the actual paradigm -->

## Data Layer

<!-- TODO: fill from real code, citing actual class names and paths; adapt the section title to the actual paradigm (e.g. Model layer / core data module) -->

- Base-class inheritance: TODO: (cite the real base class, e.g. `app/models/base.py:Base`)
- Field declaration style: TODO:
- Table/collection naming rule: TODO:
- Storage location: TODO:

## Contract Layer

<!-- TODO: fill from real code, citing actual class names and paths; adapt the section title to the actual paradigm (e.g. Schema/DTO layer / public types and interfaces layer) -->

- Request/response base classes: TODO:
- Serialization rules: TODO:
- Validation approach: TODO:
- Location: TODO:

## Business-Logic Layer

<!-- TODO: fill from real code, citing actual class names and paths; adapt the section title to the actual paradigm (e.g. Service layer / core logic module) -->

- Pure business logic only; never handle transport/entry-layer details
- Method signature pattern: TODO:
- Exception handling: TODO: (cite the real exception classes)
- Query optimization: TODO: (e.g. pagination, N+1 avoidance conventions)

## Entry Layer

<!-- TODO: fill from real code, citing actual class names and paths; adapt the section title to the actual paradigm (e.g. Controller/Endpoint layer / public export module) -->

- Only parameter extraction, calling the business-logic layer, and output formatting
- Pagination handling: TODO:
- Response format: must follow the unified contract structure in [../contracts/boundary.md](../contracts/boundary.md)

## Registration Mechanism

<!-- TODO: how and where routes/commands/plugins are registered; remove this section if the project has no registration mechanism -->

TODO:

## Error Code Allocation

<!-- TODO: if the project has an error-code system, list the used ranges; otherwise remove this section -->

| Range | Purpose |
|---|---|
| TODO: | TODO: |
