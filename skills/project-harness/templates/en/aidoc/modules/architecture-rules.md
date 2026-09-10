<!-- last-updated: {{DATE}} -->
# Architecture / Module Organization Rules

## General Principle

- Strict layering: never skip layers or call across layers in the wrong direction.
- Every rule below cites real class names and file paths; when the code changes, update this file in the same change.

<!-- variant: layered-service — the generate workflow keeps the matching variant and deletes the rest -->

TODO: state the actual layer order and data-flow direction (e.g. `Router → Endpoint → Service → Model`).

<!-- variant: package-module — the generate workflow keeps the matching variant and deletes the rest -->

TODO: state the actual package/module structure and the dependency direction between packages.

<!-- variant: plugin-system — the generate workflow keeps the matching variant and deletes the rest -->

TODO: state the actual plugin architecture: core vs plugins, registration mechanism, allowed interaction paths.

<!-- additional paradigms the generate workflow may substitute for the variants above:
- qt-app: UI/logic separation, signals & slots connecting the two sides; the UI layer never touches core data structures directly
- cpp-app: public headers/interfaces → implementation modules → build targets (CMake/Makefile)
- java-app: package layering (e.g. controller/service/repository or api/impl) with one-way dependencies
-->

## Data Layer

TODO: storage/persistence conventions — base classes, declaration style, naming rules, storage location — cite real paths and symbols (e.g. `app/models/common/base.py:BaseModel`).

## Contract Layer

TODO: interface/data-shape conventions — request/response or schema/DTO base classes, serialization rules, validation approach — cite real paths and symbols.

## Business-Logic Layer

TODO: pure business logic rules, method/function signature pattern, exception handling, query optimization expectations — cite real paths and symbols.

## Entry Layer

TODO: how external calls enter the system — parameter extraction, response formatting, registration of new entries — cite real paths and symbols (e.g. the route/command registration file).

The layer titles above are neutral placeholders; the generate workflow adapts them to the actual paradigm and names them after the real layers in the code.

## Error Code Allocation

TODO: list used error-code ranges per module if the project has an error-code system; otherwise remove this section.

| Range | Module / purpose |
|---|---|
| TODO | TODO |
