# SurrealDB Runtime Backend

Agent-Frameworks should persist runtime state in SurrealDB from the beginning.

## Why SurrealDB

SurrealDB can store:

- objectives
- tasks
- A2A handoffs
- LangGraph checkpoints
- events
- evaluations
- trust records
- analytics events
- artifacts

This makes it a strong default backend for the agent runtime.

## Runtime Persistence Requirements

The runtime should persist:

- runtime requests
- execution state
- intermediate checkpoints
- agent responses
- errors
- retry attempts
- readiness decisions

## Core Principle

```text
No important runtime state should exist only in memory.
```

## Integration Boundary

```text
Agent-Frameworks
  → writes runtime state to SurrealDB

Agent-Graph
  → defines data schemas

Agent-Analytics
  → consumes events

Agent-Trust
  → consumes provenance records
```
