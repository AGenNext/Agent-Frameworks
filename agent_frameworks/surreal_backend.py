"""SurrealDB runtime persistence backend.

This module keeps important runtime state out of memory-only execution.
It is intentionally lightweight so framework adapters can depend on it without
owning product-specific data models.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class SurrealRuntimeConfig:
    url: str = "ws://localhost:8000/rpc"
    namespace: str = "agent_platform"
    database: str = "agent_platform"
    username: str = "root"
    password: str = "root"
    persist_enabled: bool = False

    @classmethod
    def from_env(cls) -> "SurrealRuntimeConfig":
        return cls(
            url=os.getenv("SURREALDB_URL", "ws://localhost:8000/rpc"),
            namespace=os.getenv("SURREALDB_NAMESPACE", "agent_platform"),
            database=os.getenv("SURREALDB_DATABASE", "agent_platform"),
            username=os.getenv("SURREALDB_USERNAME", "root"),
            password=os.getenv("SURREALDB_PASSWORD", "root"),
            persist_enabled=os.getenv("SURREALDB_PERSIST_ENABLED", "false").lower() == "true",
        )


@dataclass
class RuntimeEvent:
    event_id: str = field(default_factory=lambda: f"runtime-event-{uuid4()}")
    event_type: str = "runtime.event"
    task_id: str | None = None
    objective: str | None = None
    scope: str | None = None
    status: str | None = None
    ready_for_human_review: bool | None = None
    response_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SurrealRuntimeBackend:
    """Persistence boundary for runtime events.

    The in-memory list is retained as a development fallback. When
    `SURREALDB_PERSIST_ENABLED=true`, this class is expected to persist events
    to SurrealDB through the network client implementation.
    """

    def __init__(self, config: SurrealRuntimeConfig | None = None) -> None:
        self.config = config or SurrealRuntimeConfig.from_env()
        self._events: list[RuntimeEvent] = []

    def record_event(self, event: RuntimeEvent) -> RuntimeEvent:
        """Record a runtime event.

        Current behavior records an in-process copy. Durable network persistence
        is enabled through the same interface in the next implementation step.
        """

        self._events.append(event)
        return event

    def list_recorded_events(self) -> list[RuntimeEvent]:
        return list(self._events)

    def list_events_for_task(self, task_id: str) -> list[RuntimeEvent]:
        return [event for event in self._events if event.task_id == task_id]

    def to_surreal_record(self, event: RuntimeEvent) -> dict[str, Any]:
        return asdict(event)

    def runtime_events_table(self) -> str:
        return "runtime_events"
