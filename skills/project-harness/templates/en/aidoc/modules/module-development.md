<!-- last-updated: {{DATE}} -->
# Module Development Guide

> Complete steps for adding a module / feature / command. Steps and reference files must point to real paths.

## Design Principles

- Self-contained modules: every layer of a module lives inside its own directory
- Follow existing patterns: read an existing module first (prefer a feature-complete, recently modified one) before starting
- Do not introduce libraries or patterns the project does not yet use; when genuinely needed, write a decision note first (see [../notes/README.md](../notes/README.md))

<!-- variants: layered-service module / library feature / cli command — the generate workflow keeps the matching variant and deletes the rest -->

## Create a Layered-Service Module

<!-- TODO: keep this variant for layered-service (typical web/backend) projects; complete every step with real commands and paths -->

1. Create the module directory: TODO:
2. Define the model: TODO: (see [architecture-rules.md](architecture-rules.md) Data Layer)
3. Define the schema/DTO: TODO:
4. Implement the business logic: TODO:
5. Implement the entry layer (endpoint/controller): TODO:
6. Register the route: TODO:
7. Database migration: TODO:
8. Add focused tests: TODO:

## Create a Library Feature

<!-- TODO: keep this variant for library/SDK projects; delete it for other project types -->

1. Design the public API surface (function/class signatures): TODO:
2. Implement the internal logic: TODO:
3. Register the export (package entry / public export path): TODO: (export contract: [../contracts/boundary.md](../contracts/boundary.md))
4. Confirm the version-compatibility impact (breaking change or not): TODO:
5. Add focused tests: TODO:

## Create a CLI Command

<!-- TODO: keep this variant for cli projects; delete it for other project types -->

1. Define the command spec (name, arguments, options): TODO:
2. Implement the command handler: TODO:
3. Register the command: TODO:
4. Conventions for output and exit codes: TODO: (exit-code conventions: [../contracts/boundary.md](../contracts/boundary.md))
5. Add focused tests: TODO:

## Create a Frontend Feature

<!-- TODO: delete this section when the project has no frontend -->

1. Define type declarations: TODO:
2. Write the API wrapper function: TODO: (reuse rules: [../frontend/frontend-utils.md](../frontend/frontend-utils.md))
3. Write the page/component: TODO: (rules: [../frontend/frontend-rules.md](../frontend/frontend-rules.md))
4. Register the route: TODO:
5. Internationalization entries (if any): TODO:

## Pre-Completion Checklist

- [ ] Both sides of the contract match [../contracts/boundary.md](../contracts/boundary.md)
- [ ] Focused validation ran, proportional to the affected surface (see the root `AGENTS.md` operating invariants)
- [ ] If the module involves a non-trivial decision, a decision note exists in `aiDoc/notes/`

## Real Reference Files

<!-- TODO: list 1-2 real module paths usable as templates -->

- TODO:
