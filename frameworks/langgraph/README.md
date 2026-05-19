# LangGraph framework adapter

LangGraph is the current execution framework adapter for AGenNext graph-based agent workflows.

## Decision

LangGraph-specific code belongs in `AGenNext/Agent-Frameworks`, not directly inside `Agent-Runtime`.

Agent-Runtime remains framework-neutral and calls framework adapters through stable contracts.

## Boundary

| Component | Responsibility |
|---|---|
| Agent-Frameworks | Framework adapters such as LangGraph |
| Agent-Runtime | Runtime lifecycle, profiles, adapter invocation |
| Agent-Graph | AGenNext graph contracts and future-native execution model |
| Agent-Blueprint | Planning/blueprint contracts |
| SurrealDB | Durable state, memory, graph, events, audit |

## Current flow

```txt
Agent-Blueprint emits AgentGraph-compatible plan
  ↓
Agent-Runtime receives plan
  ↓
Agent-Runtime calls Agent-Frameworks/LangGraph adapter
  ↓
LangGraph executes workflow
  ↓
Runtime persists state/events to SurrealDB
```

## Rule

Do not couple blueprints, cloud agents, or runtime profiles directly to LangGraph.

Only the framework adapter should import LangGraph packages.

## Future

When AgentGraph-native execution is ready, Agent-Runtime can switch from the LangGraph adapter to the native AgentGraph executor without rewriting blueprints or domain agents.
