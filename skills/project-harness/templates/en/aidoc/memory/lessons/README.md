<!-- last-updated: {{DATE}} -->
# Lesson Memory

Stores pitfalls hit during development and patterns observed recurring. This directory is a **staging area for experience**: lessons are captured here at low cost, and once the promotion condition is met the rule is written into the constraint body's home document (`/AGENTS.md`, `modules/architecture-rules.md`, `contracts/boundary.md`, etc.) — this directory keeps only the record and the outbound link.

## Rules

- When work hits a pitfall, review flags the same class of problem repeatedly, or a reusable pattern emerges, one lesson must be recorded in the same change.
- When an equivalent lesson already exists, **increment its occurrence count in place** — never file a duplicate.
- Use [TEMPLATE.md](TEMPLATE.md) for new records (keep it light — five lines); the header `lesson-meta` marker must stay in sync with the human-readable sections.
- After recording or incrementing, update the index in [../project-memory.md](../project-memory.md).
- Naming: `yyyy-mm-dd-topic.md`.

## Promotion Discipline

- Trigger: the same lesson occurs a 2nd time, or the user confirms explicitly — **once is an incident, twice is a pattern**.
- Action: in the same change, write the rule into the constraint body's home document; set this record's status to `promoted`, fill in the promotion target link, and sync `status`/`target` in the header `lesson-meta` marker.
- Deferral: when an entry is `pending` with count ≥ 2 but promotion is deliberately postponed, set the marker to `deferred` and record the defer reason under "Promotion Target"; the sync workflow re-examines whether the reason still holds.
- If the promotion alters behavior, architecture, or contracts, a decision note per `aiDoc/notes/README.md` is still required.
- Entries confirmed to have no general value are marked `dropped`, with the reason recorded.
- Never stockpile lessons without promoting; `check_sync.py` check 5 fails on unhandled `pending` entries with count ≥ 2.

## Recurrence After Promotion

- If the same problem recurs after promotion, the promoted rule was ineffective (wrong home document, non-binding wording, wrong granularity): increment `post` in `lesson-meta`, **revise the promoted rule body** in the same change (do not file a new lesson), and record per `aiDoc/notes/README.md` why the first rule failed to prevent it.
- `check_sync.py` check 6 lists entries with `post ≥ 1` as hints.

## Mechanical Scan

`check_sync.py` judges solely from the header `lesson-meta` marker (never heading-text matching):

- `pending` with `count ≥ 2`, neither promoted nor explicitly `deferred` → ❌ fail
- `promoted` with empty `target` → ❌ fail
- Missing `lesson-meta` marker, or `post ≥ 1` → ⚠️ listed as hints, non-blocking

## Lesson Index

None yet.
