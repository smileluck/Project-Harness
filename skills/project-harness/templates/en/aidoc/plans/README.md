<!-- last-updated: {{DATE}} -->
# Change Plans

`aiDoc/plans/` stores execution plans and handoffs for non-trivial work. Durable rationale lives in `../notes/`; execution state lives here — the two age differently.

## When a Plan Is Needed

Create a plan for work that is multi-step, cross-component, risky, or delegated to another agent or person. A single-file, single-concern change needs no plan.

## Directory Structure

| Directory | Contents |
|---|---|
| `active/` | In-progress change plans, named `yyyy-mm-dd-topic.md` |
| `completed/` | Finished and archived plans |

## Lifecycle

1. Before starting, create the plan in `active/` (use [change-plan.TEMPLATE.md](change-plan.TEMPLATE.md)) with objective / non-goals / assumptions / acceptance criteria / work items / validation commands / rollback
2. Update the plan in place as work progresses (current decisions, blockers, completed items)
3. On completion: append a delivery summary and move the file to `completed/`
4. Delete plans with no durable retention value (pure temporary coordination) once finished
5. A completed plan is evidence of execution, not the authority for current behavior — that authority lives in the `aiDoc/` docs and decision notes

## Work Item Format

- Every work item names an owner and its dependencies
- Write scopes are advisory: they name the expected files/directories to reduce parallel conflicts, but they are not locks
- Every work item carries a validation command, with evidence proportional to the affected surface (see the root `AGENTS.md` operating invariants)

## Handoffs

When work is interrupted or handed over, use [handoff.TEMPLATE.md](handoff.TEMPLATE.md). Never describe an interrupted command as completed; a handoff must name the next safe action.
