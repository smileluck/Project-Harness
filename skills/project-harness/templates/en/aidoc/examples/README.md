<!-- last-updated: {{DATE}} -->
# Example Layer

`aiDoc/examples/` is the explanatory example layer: it tells AI the standard for organizing and writing each layer.

## Purpose

- Examples are not meant to be copied verbatim; they show the project's standard code organization.
- When AI needs to add a file to a layer, it reads the corresponding example first.

## Backend Reading Order

TODO: list backend example files in the order a new module is built (model → schema/DTO → service → endpoint → router). Remove this section when there is no backend.

## Frontend Reading Order

TODO: list frontend example files (api → view → utils-usage). Remove this section when there is no frontend.

## Principles

- Example code must be extracted from real project code, never invented. If no sufficient example exists, write code that matches the detected project patterns.
- When real code and an example disagree, the real code wins — update the example in the same change.
