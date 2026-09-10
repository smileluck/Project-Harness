# Harness model

The harness separates information by how it ages and who must load it. Adapt the model to the target project; the target repository's live state always wins over any template.

## Five layers

1. **Standing instructions** — root `AGENTS.md` holds the minimal rules needed in almost every session. Nested `AGENTS.md` files add only subtree-specific constraints.
2. **Current-state documentation** — `aiDoc/` holds what the project *is*: structure, stack, layering rules, contracts, examples, memory. Each document owns one distinct type of fact.
3. **Decision records** — `aiDoc/notes/<lifecycle>/<class>/` retains motivation, the chosen decision, real rejected alternatives, and consequences.
4. **Workflow skills** — project-local situational procedures under `.agents/skills/`, loaded only when needed.
5. **Executable evidence** — focused tests and `scripts/check_sync.py` prove affected behavior and doc-code consistency locally; CI owns exhaustive matrices.

Team coordination overlays these layers: a lead partitions work, teammates own bounded tasks, a shared task graph records dependencies, and the lead owns final integration. See [collaboration.md](collaboration.md).

## Ownership map

| Information | Maintained home |
|---|---|
| Rules needed in every task | Root `AGENTS.md` |
| Rules for one directory tree | Nested `AGENTS.md` |
| Repo structure, stack, workflow, system map | `aiDoc/relations/` |
| Backend layering rules, module development | `aiDoc/modules/` |
| Frontend/backend contracts and frontend rules | `aiDoc/frontend-backend/` |
| Worked examples of project patterns | `aiDoc/examples/` |
| Stable preferences, business requirements | `aiDoc/memory/` |
| Why a non-trivial decision won | `aiDoc/notes/<lifecycle>/<class>/` |
| Current execution checklist | `aiDoc/plans/active/` |
| Reusable situational procedure | `.agents/skills/<workflow>/SKILL.md` |
| Task → required-docs routing | `aiDoc/README.md` (sole routing table) |
| Tool loading entry | `CLAUDE.md` (`@AGENTS.md`) + thin adapters |
| Proof affected behavior works | Focused tests; `scripts/check_sync.py` for doc drift |

Never duplicate a rule across tiers. Put a short link at the point of use.

## Conflict priority

`AGENTS.md` > `aiDoc/README.md` > aiDoc sub-documents > tool adapter files. Adapters must never carry rule bodies — only entry pointers (see [tool-adapters.md](tool-adapters.md)).

## Operating invariants

- One fact, one maintained home; other documents link to it.
- Non-trivial changes update the documentation and the decision record that owns the rationale. Mechanical, behavior-preserving edits need no ceremonial notes.
- Default initialization never overwrites existing files. `--overwrite` requires explicit approval.
- Mechanically checkable rules should become executable checks (tests, `check_sync.py` coverage) when the project can support them.
- Local work runs the narrowest credible regression evidence; CI owns exhaustive coverage.
- The lead agent owns integration: final diff, overlap reconciliation, relevant checks, and waiting for required delegated work.

## Toolkit boundaries

This toolkit adapts a *system*, not a specific project. It must not copy into the target repo:

- Any source project's package names, directory topology, framework-specific rules, or plugin conventions.
- Any source project's release policy, language-specific gates, fixed commands, or coverage targets.
- Absolute documentation budgets or file quotas without evidence from the target repository.
- Adapter files for tools the target repo does not use.

What is reusable: separation of concerns, durable rationale, scoped instructions, explicit ownership, advisory write scopes, final-lead integration, and evidence proportional to the change. Every generated command, rule, and path must be confirmed against the target project's real manifests and code.
