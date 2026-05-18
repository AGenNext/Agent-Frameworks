"""SurrealDB runtime persistence backend.

This module keeps important runtime state out of memory-only execution.
It is intentionally lightweight so framework adapters can depend on it without
owning product-specific data models.
"""

from __future__ import annotations

import asyncio
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
    agent_id: str | None = None
    loop_id: str | None = None
    iteration: int | None = None
    exchange_id: str | None = None
    parent_event_id: str | None = None
    handoff_id: str | None = None
    source_agent: str | None = None
    target_agent: str | None = None
    status: str | None = None
    ready_for_human_review: bool | None = None
    response_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SurrealRuntimeBackend:
    """Persistence boundary for runtime events.

    The in-memory list is retained as a development fallback. When
    `SURREALDB_PERSIST_ENABLED=true`, this class writes to SurrealDB.
    """

    def __init__(self, config: SurrealRuntimeConfig | None = None) -> None:
        self.config = config or SurrealRuntimeConfig.from_env()
        self._events: list[RuntimeEvent] = []

    def record_event(self, event: RuntimeEvent) -> RuntimeEvent:
        self._events.append(event)
        if self.config.persist_enabled:
            asyncio.run(self._record_event_async(event))
        return event

    def list_recorded_events(self) -> list[RuntimeEvent]:
        return list(self._events)

    def list_events_for_task(self, task_id: str) -> list[RuntimeEvent]:
        if self.config.persist_enabled:
            return asyncio.run(self._list_events_for_task_async(task_id))
        return [event for event in self._events if event.task_id == task_id]

    def list_events_for_loop(self, task_id: str, loop_id: str) -> list[RuntimeEvent]:
        return [
            event
            for event in self.list_events_for_task(task_id)
            if event.loop_id == loop_id
        ]

    def to_surreal_record(self, event: RuntimeEvent) -> dict[str, Any]:
        return asdict(event)

    def runtime_events_table(self) -> str:
        return "runtime_events"

    async def _connect(self):
        from surrealdb import Surreal

        db = Surreal(self.config.url)
        await db.connect()
        await db.signin({"username": self.config.username, "password": self.config.password})
        await db.use(self.config.namespace, self.config.database)
        return db

    async def _record_event_async(self, event: RuntimeEvent) -> None:
        db = await self._connect()
        try:
            await db.create(self.runtime_events_table(), self.to_surreal_record(event))
        finally:
            await db.close()

    async def _list_events_for_task_async(self, task_id: str) -> list[RuntimeEvent]:
        db = await self._connect()
        try:
            rows = await db.query(
                "SELECT * FROM runtime_events WHERE task_id = $task_id ORDER BY created_at ASC;",
                {"task_id": task_id},
            )
        finally:
            await db.close()

        result = rows[0].get("result", []) if rows else []
        return [RuntimeEvent(**self._clean_surreal_row(row)) for row in result]

    def _clean_surreal_row(self, row: dict[str, Any]) -> dict[str, Any]:
        row = dict(row)
        row.pop("id", None)
        return row
