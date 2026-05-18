# Agent Frameworks

Agent Frameworks contains reusable orchestration framework integrations for AGenNext products.

## Scope

This repository owns framework-level runtime adapters and reusable orchestration patterns, including LangGraph SDK integration.

## Initial Framework

- LangGraph SDK / LangGraph runtime patterns

## Consumers

- Agent Knowledge
- Agent Teams
- Future AGenNext products

## Boundary

```text
Agent-Frameworks
  → LangGraph SDK integration
  → reusable orchestration adapters
  → framework patterns

Agent-Teams
  → reusable agent roles and operating models

Agent-Graph
  → artifact schemas only

Agent-Knowledge
  → enterprise SaaS product using the above
```

Do not put product-specific Agent Knowledge logic in this repository.
