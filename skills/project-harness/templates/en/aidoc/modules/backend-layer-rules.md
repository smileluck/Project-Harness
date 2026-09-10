<!-- last-updated: {{DATE}} -->
# Backend Layer Rules

## General Principle

- Strict layering: never skip layers or call across layers in the wrong direction.
- Every rule below cites real class names and file paths; when the code changes, update this file in the same change.

TODO: state the actual layer order and data-flow direction (e.g. `Router → Endpoint → Service → Model`).

## Model Layer

TODO: base class inheritance, field declaration style, table-naming rule, storage location — cite real paths and symbols (e.g. `app/models/common/base.py:BaseModel`).

## Schema / DTO Layer

TODO: request/response base classes, serialization rules, validation approach — cite real paths and symbols.

## Service Layer

TODO: pure business logic rules, method signature pattern, exception handling, query optimization expectations — cite real paths and symbols.

## Controller / Endpoint Layer

TODO: parameter extraction, response formatting, pagination handling — cite real paths and symbols.

## Router Layer

TODO: how routes are registered and where a new module hooks in — cite the real registration file.

## Error Code Allocation

TODO: list used error-code ranges per module if the project has an error-code system; otherwise remove this section.

| Range | Module / purpose |
|---|---|
| TODO | TODO |
