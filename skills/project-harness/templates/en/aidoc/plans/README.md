<!-- last-updated: {{DATE}} -->
# Change Plans

`aiDoc/plans/` stores execution plans and handoffs for non-trivial work. Durable rationale lives in `../notes/`; execution state lives here — the two age differently.

## When a Plan Is Needed

Create a plan for work that is multi-step, cross-component, risky, or delegated to another agent or person. A single-file, single-concern change needs no plan.

## Lifecycle

- Active plans live in `active/yyyy-mm-dd-topic.md` and are updated as work changes.
- On completion, summarize the delivered outcome in the plan and move it to `completed/`. Delete it instead when it has no durable value.
- A completed plan is evidence of execution, not the authority for current behavior — current behavior is documented in the `aiDoc/` docs and `../notes/`.

## Templates

- `change-plan.TEMPLATE.md` — objective, non-goals, assumptions, acceptance criteria, work items with owners / dependencies / advisory write scopes, validation commands, rollback.
- `handoff.TEMPLATE.md` — exact state for the next agent or person continuing unfinished work.

## Discipline

- Every work item names an owner and its dependencies.
- Validation commands must be concrete and runnable, with evidence proportional to the affected surface.
- Never describe an interrupted command as completed — in plans or in handoffs.
