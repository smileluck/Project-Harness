<!-- last-updated: {{DATE}} -->
# Development Workflow

> Development order, collaboration mode, branch and commit conventions, environment commands. Commands must come from real config files — never invent.

## Recommended Development Order

<!-- TODO: design the steps from the real layering, e.g. model → Schema → Service → Endpoint → router registration → migration -->

1. TODO:
2. TODO:

## Contract Collaboration

<!-- TODO: add the integration-verification method per the real structure; remove this section when there is no producer/consumer two-sided structure -->

- The producer side defines the interface contract first (see [../contracts/boundary.md](../contracts/boundary.md)); the consumer side develops in parallel
- Before integration, confirm both sides of the contract match field-for-field

## Branch Strategy

<!-- TODO: fill per the real convention, e.g. main/develop/feature/hotfix -->

| Branch | Purpose |
|---|---|
| TODO: | TODO: |

## Commit Conventions

<!-- TODO: format and allowed type list, e.g. type(scope): description -->

TODO:

## Environment & Dependencies
<!-- scan-fill:env -->

<!-- TODO: install, start, migrate, test, build commands — must run in the real environment; delete inapplicable rows -->

| Task | Command |
|---|---|
| Install dependencies | `TODO:` |
| Start dev server | `TODO:` |
| Database migration | `TODO:` |
| Run tests | `TODO:` |
| Build | `TODO:` |

## API Documentation

<!-- TODO: Swagger/ReDoc URL if any; otherwise remove this section -->

TODO:
