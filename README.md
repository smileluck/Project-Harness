# Project-Harness

**English** | [中文](README.zh-CN.md)

Turn any repository into an **agent-ready project**: layered `AGENTS.md` instructions, a structured `aiDoc/` documentation system, durable decision records, change plans, handoffs, project-local review skills, and drift detection — all installable into the agent tools you already use.

## Why

An `AGENTS.md` file helps, but it is not a complete collaboration system. Agent-heavy projects also need:

- a maintained home for current-state facts (architecture, contracts, module rules),
- durable rationale for decisions (including the alternatives that were rejected),
- execution state for work in flight (plans, handoffs),
- situational workflows (review, pre-push checks) loaded only when relevant,
- and a way to detect when the docs have drifted away from the code.

Project-Harness packages all of this as a single installable skill with deterministic scripts, working with Kimi Code, Claude Code, Codex, and any tool that scans `.agents/skills/`.

## The harness model

Five cooperating layers, one maintained home per fact:

| Layer | Home in the target repo |
|---|---|
| Standing instructions | Root `AGENTS.md` (+ nested `AGENTS.md` only where subtree rules genuinely differ) |
| Current-state documentation | `aiDoc/` (relations, modules, frontend-backend, examples, memory) |
| Decision records | `aiDoc/notes/<proposed\|implemented\|rejected>/<class>/` |
| Execution state | `aiDoc/plans/active/` → `completed/`, handoffs |
| Workflow skills & executable evidence | `.agents/skills/`, focused checks (`check_sync.py`), CI owns exhaustive matrices |

Conflict priority: `AGENTS.md` > `aiDoc/README.md` > aiDoc child docs > tool adapter files. Tool-private directories hold only thin pointers, never rule copies.

## Install

Requirements: Python 3.9+ (standard library only).

```bash
git clone <this-repo-url>
cd Project-Harness

# Install the skill into your agent tools (user level)
python3 install.py --tool agents    # ~/.agents/skills/ (Kimi Code and other .agents-aware tools)
python3 install.py --tool kimi      # ~/.kimi-code/skills/
python3 install.py --tool claude    # ~/.claude/skills/
python3 install.py --tool codex     # ~/.codex/skills/
python3 install.py --tool all       # all of the above

# Options: --scope project (into the current repo), --link (symlink for live updates), --dry-run
```

## The four workflows

Invoke the skill in your agent (e.g. Kimi Code: `/skill:project-harness <args>`):

| Command | What it does |
|---|---|
| `init` | Non-destructive scaffold: probes project type/stack, copies the `AGENTS.md` + `aiDoc/` skeleton, never overwrites by default (`--dry-run`, `--overwrite` with backups, idempotent). For mature repos, run a gap audit and only fill the missing pieces. |
| `generate [--incremental\|--scope <area>\|--dry-run] [--lang zh\|en]` | Agent-driven: probes the codebase and writes the real content of `AGENTS.md` + `aiDoc/` from actual code — layering rules, API contracts, examples, routing tables. Supports incremental and scoped regeneration. |
| `sync` | Drift detection: `check_sync.py` verifies index integrity, referenced paths, `last-updated` headers, and area consistency; the agent then resolves semantic drift. |
| `record [note\|plan\|handoff]` | Create decision notes, change plans, or handoffs following the lifecycle discipline (no invented alternatives; implemented notes updated in place; reversals get new cross-linked notes). |

## What a target repo gets

```
<target-repo>/
├── AGENTS.md                # L0 single source of truth: rules, invariants, DoD, routing
├── CLAUDE.md                # one line: @AGENTS.md
├── aiDoc/
│   ├── README.md            # L1 routing: index, task→must-read table, ownership map
│   ├── relations/           # repo profile, dev workflow, system map
│   ├── modules/             # backend layering rules, module dev guide
│   ├── frontend-backend/    # API contract, frontend rules, utils reuse
│   ├── examples/            # explanatory examples per layer
│   ├── memory/              # long-term preferences + business requirement records
│   ├── notes/               # decision records: <lifecycle>/<class>/yyyy-mm-dd-topic.md
│   └── plans/               # change plans (active/completed) + handoffs
├── .agents/skills/
│   ├── project-code-review/       # semantic review checklist + evidence selection
│   └── project-pre-push-checks/   # smallest credible outgoing checks
└── thin tool adapters       # only for tool dirs that already exist (.trae, .cursor, copilot, ...)
```

## Safety model

- Default initialization **never overwrites** existing files; existing destinations are reported as `SKIP`.
- `--overwrite` backs up every replaced file to `aiDoc/.harness-backups/<timestamp>/` first.
- The initializer refuses to run in a subdirectory of an existing Git repository.
- Unverifiable facts become visible `TODO` markers — the toolkit never invents commands or stack details.
- Rule bodies live only in `AGENTS.md` + `aiDoc/`; tool directories get thin adapter pointers only.

## Repository layout

```
Project-Harness/
├── install.py                    # multi-tool installer (copy or symlink)
└── skills/project-harness/       # the whole skill; installing = copying this directory
    ├── SKILL.md                  # entry routing: init / generate / sync / record
    ├── references/               # workflow details (harness model, aiDoc contract, quality, collaboration, ...)
    ├── templates/zh/  templates/en/   # bilingual skeletons injected into target repos
    └── scripts/
        ├── init_project.py       # non-destructive scaffolding
        └── check_sync.py         # mechanical drift checks
```

## Acknowledgements

Designs adapted and generalized from:

- [generate-aidoc](https://github.com/smileluck/SmileX-Fastapi-Cloud/blob/main/.claude/commands/generate-aidoc.md) — the aiDoc layered documentation generation workflow
- [dsh-project-harness](https://github.com/Pytorchlover/dsh-project-harness) — five-layer harness model, decision records, change plans, team coordination, proportionate evidence
- [Harness_Handbook](https://github.com/Ruhan-Wang/Harness_Handbook) — codebase handbooks for agent navigation (inspiration; the heavy LLM pipeline is intentionally not included)

## License

[MIT](LICENSE)
