"""LangGraph-oriented runtime adapter for Agent-Team.

Agent-Team owns the agents and orchestration logic.
Agent-Frameworks owns framework-specific execution adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_team.orchestrator import ProjectManagerOrchestrator
from agent_team.registry import build_bootstrapped_team_registry

from agent_frameworks.surreal_backend import RuntimeEvent, SurrealRuntimeBackend


@dataclass
class RuntimeRequest:
    task_id: str
    objective: str
    scope: str
    metadata: dict[str, Any] | None = None


@dataclass
class EvaluationResult:
    status: str
    score: float
    summary: str


@dataclass
class TrustResult:
    status: str
    score: float
    summary: str


@dataclass
class FinOpsResult:
    status: str
    estimated_cost_usd: float
    budget_status: str
    summary: str


@dataclass
class RuntimeResult:
    task_id: str
    ready_for_human_review: bool
    response_count: int
    metadata: dict[str, Any]
    evaluation: EvaluationResult
    trust: TrustResult
    finops: FinOpsResult


class LangGraphRuntime:
    """Minimal runtime adapter.

    This intentionally keeps framework-specific logic in Agent-Frameworks while
    delegating team behavior to Agent-Team.
    """

    def __init__(self) -> None:
        registry = build_bootstrapped_team_registry()
        self.orchestrator = ProjectManagerOrchestrator(registry)
        self.backend = SurrealRuntimeBackend()

    def run(self, request: RuntimeRequest) -> RuntimeResult:
        self.backend.record_event(
            RuntimeEvent(
                event_type="runtime.started",
                task_id=request.task_id,
                objective=request.objective,
                scope=request.scope,
                metadata=request.metadata or {},
            )
        )

        result = self.orchestrator.run_plan(
            task_id=request.task_id,
            objective=request.objective,
            scope=request.scope,
        )

        evaluation = EvaluationResult(
            status="passed" if result.ready_for_human_review else "blocked",
            score=1.0 if result.ready_for_human_review else 0.0,
            summary="Baseline evaluation derived from internal agent consensus.",
        )
        trust = TrustResult(
            status="conditional_trust" if result.ready_for_human_review else "untrusted",
            score=0.75 if result.ready_for_human_review else 0.0,
            summary="Baseline trust derived from traceable runtime events and agent responses.",
        )
        finops = FinOpsResult(
            status="estimated",
            estimated_cost_usd=0.0,
            budget_status="within_budget",
            summary="Baseline FinOps estimate for local/open-source runtime path.",
        )

        runtime_result = RuntimeResult(
            task_id=request.task_id,
            ready_for_human_review=result.ready_for_human_review,
            response_count=len(result.responses),
            metadata=request.metadata or {},
            evaluation=evaluation,
            trust=trust,
            finops=finops,
        )

        self.backend.record_event(
            RuntimeEvent(
                event_type="evaluation.completed",
                task_id=request.task_id,
                objective=request.objective,
                scope=request.scope,
                status=evaluation.status,
                metadata={"score": evaluation.score, "summary": evaluation.summary},
            )
        )
        self.backend.record_event(
            RuntimeEvent(
                event_type="trust.completed",
                task_id=request.task_id,
                objective=request.objective,
                scope=request.scope,
                status=trust.status,
                metadata={"score": trust.score, "summary": trust.summary},
            )
        )
        self.backend.record_event(
            RuntimeEvent(
                event_type="finops.completed",
                task_id=request.task_id,
                objective=request.objective,
                scope=request.scope,
                status=finops.status,
                metadata={
                    "estimated_cost_usd": finops.estimated_cost_usd,
                    "budget_status": finops.budget_status,
                    "summary": finops.summary,
                },
            )
        )
        self.backend.record_event(
            RuntimeEvent(
                event_type="runtime.completed",
                task_id=request.task_id,
                objective=request.objective,
                scope=request.scope,
                status="completed",
                ready_for_human_review=runtime_result.ready_for_human_review,
                response_count=runtime_result.response_count,
                metadata=runtime_result.metadata,
            )
        )

        return runtime_result
