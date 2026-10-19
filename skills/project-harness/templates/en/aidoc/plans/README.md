<!-- last-updated: {{DATE}} -->
# Change Plans

`aiDoc/plans/` stores in-progress change plans and handoff documents. Execution state and decision rationale age at different speeds, so plans (here) and decision records ([../notes/](../notes/)) are maintained separately.

## Directory Structure

- `active/` — in-progress change plans, named `yyyy-mm-dd-topic.md`
- `completed/` — finished and archived plans

## When a Plan Is Needed

Multi-step / cross-component changes, risky changes (data migration, contract breakage, dependency upgrades), and work that must be split across multiple executors or handed over require a plan in `active/` using [change-plan.TEMPLATE.md](change-plan.TEMPLATE.md). A single-file, single-interface change needs no plan — execute it directly against the root `AGENTS.md` Definition of Done.

## Lifecycle

1. Before starting, create the plan in `active/` with objective / scope and assumptions / acceptance criteria / work items / rollback
2. Update the plan in place as work progresses (current decisions, blockers, completed items)
3. On completion, add the delivery summary and move the file to `completed/`; plans with no durable retention value (pure temporary coordination) may be deleted outright
4. A completed plan is evidence of execution, not the authority for current behavior — current behavior is defined by the code and the aiDoc child documents

## Work Item Format

- Every work item names an owner and its dependencies; advisory write scopes reduce parallel conflicts but are not locks
- Every work item carries a validation command, with evidence proportional to the affected surface (see the root `AGENTS.md` operating invariants)

## Handoffs

When work is interrupted or handed over, use [handoff.TEMPLATE.md](handoff.TEMPLATE.md); never describe an interrupted command as completed, and a handoff must name the next safe action.
