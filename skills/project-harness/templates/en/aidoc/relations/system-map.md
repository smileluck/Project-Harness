<!-- last-updated: {{DATE}} -->
# System Map

> System architecture and component relationships. Structure descriptions must match the real tree — never invent directories.

## Root Directory Responsibilities
<!-- scan-fill:rootdirs -->

<!-- init's scan fills this table with component annotations (mixed projects get one row per component); tool directories (.claude/.trae etc.) are not listed here -->

| Directory | Responsibility |
|---|---|
| TODO: | TODO: |

## Backend Layering

<!-- TODO: draw the call chain per the real layering, e.g. Router → Controller → Service → Model; remove this section when there is no backend -->

```
TODO: layered call-chain sketch
```

- Call direction must be one-way; never skip layers or call backwards
- Per-layer constraints: [../modules/architecture-rules.md](../modules/architecture-rules.md)

## Core Infrastructure

<!-- TODO: table of infrastructure directories/modules and their responsibilities (config, logging, auth, exception handling, etc.) -->

| Location | Responsibility |
|---|---|
| TODO: | TODO: |

## Frontend Data Flow

<!-- TODO: if there is a frontend, describe per the real structure: API wrapper → state management → router → view → type declarations; remove this section when there is no frontend -->

```
TODO: frontend data-flow sketch
```

## Module Mapping

<!-- TODO: backend module ↔ frontend page/feature mapping table (if applicable) -->

| Backend module | Frontend page / feature |
|---|---|
| TODO: | TODO: |

## Configuration Files
<!-- scan-fill:config -->

<!-- TODO: key config files and their purpose -->

| File | Purpose |
|---|---|
| TODO: | TODO: |
