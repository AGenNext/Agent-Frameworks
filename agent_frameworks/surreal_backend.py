"""SurrealDB runtime persistence backend.

This module keeps important runtime state out of memory-only execution.
It is intentionally lightweight so framework adapters can depend on it without
owning product-specific data models.
"""

from __future__ import annotations

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

    The actual network client is kept lazy so tests and local smoke runs can use
    this class without requiring SurrealDB to be available.
    """

    def __init__(self, config: SurrealRuntimeConfig | None = None) -> None:
        self.config = config or SurrealRuntimeConfig()
        self._events: list[RuntimeEvent] = []

    def record_event(self, event: RuntimeEvent) -> RuntimeEvent:
        """Record a runtime event.

        Current implementation stores an in-process copy and provides the stable
        interface that will be backed by SurrealDB network writes next.
        """

        self._events.append(event)
        return event

    def list_recorded_events(self) -> list[RuntimeEvent]:
        return list(self._events)

    def to_surreal_record(self, event: RuntimeEvent) -> dict[str, Any]:
        return asdict(event)
