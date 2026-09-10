<!-- last-updated: {{DATE}} -->
# Module Development Guide

## Create a New Module / Feature / Command

TODO: adjust the steps to the real architecture; each step cites a real reference file to imitate.

<!-- variant: layered-service — the generate workflow keeps the matching variant and deletes the rest -->

1. Create the module directory — TODO: location convention
2. Define the data layer — imitate TODO: real reference path
3. Define the contract layer (schemas/DTOs) — imitate TODO: real reference path
4. Implement the business-logic layer — imitate TODO: real reference path
5. Implement the entry layer (endpoint/controller) — imitate TODO: real reference path
6. Register the new entry — TODO: real registration location
7. Create and run the migration — TODO: real command
8. Add focused tests — TODO: test location convention

<!-- variant: package-module — the generate workflow keeps the matching variant and deletes the rest -->

TODO: steps for adding a new package/module — scaffold location, export wiring, registration, tests — cite a real reference module per step.

<!-- variant: plugin-system — the generate workflow keeps the matching variant and deletes the rest -->

TODO: steps for adding a new plugin/command — plugin scaffold, registration hook, manifest/metadata, tests — cite a real reference plugin per step.

## Design Principles

- Self-contained: a module owns its data, contract, logic, and entry points; shared code goes to the shared infrastructure, never into another module.
- Follow existing patterns: imitate the closest existing module rather than inventing a new structure.
- Update docs in the same change: `../relations/system-map.md` module mapping, `../examples/` when the new module becomes the better example, and `../README.md` routing tables when a new area appears.
