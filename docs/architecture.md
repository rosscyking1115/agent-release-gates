# Architecture

## Goal

Build a public AI-agent safety and reliability lab that can answer synthetic operations questions, extract ticket data, recommend next actions, and produce measurable reliability and safety metrics.

## Phase 0/1 Architecture

```mermaid
flowchart LR
    A["Synthetic domain definitions"] --> B["Data generator"]
    B --> C["Synthetic runbooks"]
    B --> D["Synthetic tickets"]
    B --> E["Golden eval cases"]
    B --> F["Red-team cases"]
    C --> G["Future retrieval index"]
    D --> H["Future extraction and routing"]
    E --> I["Future evaluation runner"]
    F --> I
```

## Future Architecture

```mermaid
flowchart LR
    A["Synthetic docs and tickets"] --> B["Ingestion and chunking"]
    B --> C["Vector store"]
    D["User"] --> E["FastAPI"]
    E --> F["Agent workflow"]
    F --> G["Retriever"]
    G --> C
    F --> H["LLM provider adapter"]
    F --> I["Structured extraction"]
    F --> J["Approval gate"]
    J --> K["Mock operations tools"]
    F --> L["Answer with citations"]
    F --> M["Audit log"]
    F --> O["Trace and monitoring snapshot"]
    M --> N["Evaluation dashboard"]
    O --> N
```

## Key Design Choices

- The environment is synthetic so the project can be public and safe.
- Baseline behavior will be measured before improvements are added.
- Retrieved documents are treated as untrusted input.
- Structured outputs are validated with schemas.
- Side-effecting mock tools require explicit approval before execution.
- Each controlled-agent run returns a trace id, structured audit events, and monitoring fields.
- Evaluation combines deterministic checks with optional model-assisted judging.
