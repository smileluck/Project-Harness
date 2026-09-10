<!-- last-updated: {{DATE}} -->
# Module Development Guide

## Create a New Backend Module

TODO: adjust the steps to the real layering; each step cites a real reference file to imitate.

1. Create the module directory — TODO: location convention
2. Define the model — imitate TODO: real reference path
3. Define schemas/DTOs — imitate TODO: real reference path
4. Implement the service — imitate TODO: real reference path
5. Implement the endpoint/controller — imitate TODO: real reference path
6. Register the router — TODO: real registration location
7. Create and run the migration — TODO: real command
8. Add focused tests — TODO: test location convention

## Create a New Frontend Feature

TODO: if the project has a frontend — typical shape: define types → API functions → i18n entries → page component → register route. Cite real reference files per step. Remove this section when there is no frontend.

## Design Principles

- Self-contained: a module owns its model, contract, logic, and routes; shared code goes to the shared infrastructure, never into another module.
- Follow existing patterns: imitate the closest existing module rather than inventing a new structure.
- Update docs in the same change: `../relations/system-map.md` module mapping, `../examples/` when the new module becomes the better example, and `../README.md` routing tables when a new area appears.
