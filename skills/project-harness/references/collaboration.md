# Team collaboration

Coordinating multiple agents or people against one shared checkout.

## Lead responsibilities

The lead owns decomposition, authority boundaries, dependency order, final integration, and the user-facing result. Delegation does not transfer responsibility for the final diff or the checks.

Create parallel tasks only when they have independently useful outcomes and bounded write scopes. Give each teammate: the objective, relevant context, non-goals, permitted mutations, acceptance evidence, and the expected handoff format.

## Task DAG

Represent work as a DAG when dependencies matter. Each task records:

| Field | Content |
|---|---|
| id | Stable identifier |
| outcome | The independently useful result |
| owner | Current responsible agent/person |
| status | ready / claimed / done / blocked |
| dependencies | Task ids that must finish first |
| write scope | Advisory file/directory scope |
| acceptance evidence | Commands or checks that prove completion |

An owner claims one ready task at a time when practical. Update task state with compare-and-set discipline: re-read the shared record before overwriting one that may have changed.

## Advisory write scopes

Write scopes are coordination hints, **not locks**. They reduce collisions; they neither authorize writes nor prevent them. Overlapping work must be handled by ordering or by a designated integrator, never by assuming exclusion.

## Shared checkout discipline

- All writes are visible to every member immediately — there is no private staging.
- Avoid overlapping source edits. If overlap is unavoidable, serialize the work or designate one integrator.
- Formatters, code generators, dependency installers, and broad scripts can touch files far outside the apparent scope. **Announce and coordinate them before running.**
- On stale-file or patch rejection: re-read the current file, rebase the intended edit onto it, and retry. Never erase another member's changes to make a patch apply.
- Never run destructive git operations (`reset --hard`, `checkout --`, force-push) against shared state without explicit coordination.

## Communication discipline

- Use quiet status messages for information; use waking follow-ups only for new work that must be acted on.
- Treat an accepted or queued message as delivered work; do not blindly resend.
- After any wait or timeout, re-read authoritative task and repository state before acting — the world may have moved.

## Final integration

The lead waits for all required tasks, inspects the combined diff, resolves ownership gaps and overlaps, and runs integration evidence (see [quality-workflow.md](quality-workflow.md)) before delivering the user-facing result. The final answer must stand alone: outcome, material files, validation run, remaining risks.
