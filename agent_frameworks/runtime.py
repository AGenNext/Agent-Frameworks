"""LangGraph-oriented runtime adapter for Agent-Team.

Agent-Team owns the agents and orchestration logic.
Agent-Frameworks owns framework-specific execution adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_team.orchestrator import ProjectManagerOrchestrator
from agent_team.registry import build_bootstrapped_team_registry


@dataclass
class RuntimeRequest:
    task_id: str
    objective: str
    scope: str
    metadata: dict[str, Any] | None = None


@dataclass
class RuntimeResult:
    task_id: str
    ready_for_human_review: bool
    response_count: int
    metadata: dict[str, Any]


class LangGraphRuntime:
    """Minimal runtime adapter.

    This intentionally keeps framework-specific logic in Agent-Frameworks while
    delegating team behavior to Agent-Team.
    """

    def __init__(self) -> None:
        registry = build_bootstrapped_team_registry()
        self.orchestrator = ProjectManagerOrchestrator(registry)

    def run(self, request: RuntimeRequest) -> RuntimeResult:
        result = self.orchestrator.run_plan(
            task_id=request.task_id,
            objective=request.objective,
            scope=request.scope,
        )

        return RuntimeResult(
            task_id=request.task_id,
            ready_for_human_review=result.ready_for_human_review,
            response_count=len(result.responses),
            metadata=request.metadata or {},
        )
