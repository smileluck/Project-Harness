<!-- last-updated: {{DATE}} -->
# Development Workflow

Development process and contribution conventions. Commands listed here must be real and runnable.

## Recommended Development Order

TODO: derive from the real layering. Typical shape:

1. Define or adjust the data model and run migrations
2. Define schemas/DTOs (the contract)
3. Implement the service (business logic)
4. Implement the endpoint/controller
5. Register routes
6. Add or update focused tests

## Contract Collaboration

- The producer side defines the contract first; the consumer side develops in parallel against the agreed shape.
- Contract details live in `../contracts/boundary.md`; both sides must match it.
- Verify integration at the real entry path before calling the work done.

## Branch Strategy

TODO: record the real strategy (e.g. `main` / `develop` / `feature/*` / `hotfix/*`).

## Commit Conventions

TODO: record the real convention, e.g. `type(scope): description`, and list the types actually in use.

## Environment & Dependencies
<!-- scan-fill:env -->

TODO: concrete commands, verified to run.

| Task | Command |
|---|---|
| Install dependencies | TODO |
| Run dev server | TODO |
| Run migrations | TODO |
| Run focused tests | TODO |
| Typecheck / lint | TODO |
| Build | TODO |

## API Documentation

TODO: Swagger / ReDoc / other URL if the project exposes one; otherwise state how the contract is inspected (e.g. read `../contracts/boundary.md` plus the entry-point source).
