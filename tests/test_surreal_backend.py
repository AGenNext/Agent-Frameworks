from agent_frameworks.surreal_backend import RuntimeEvent, SurrealRuntimeBackend, SurrealRuntimeConfig


def test_runtime_backend_records_and_filters_events() -> None:
    backend = SurrealRuntimeBackend(
        SurrealRuntimeConfig(persist_enabled=False)
    )

    backend.record_event(RuntimeEvent(event_type="runtime.started", task_id="task-1"))
    backend.record_event(RuntimeEvent(event_type="runtime.completed", task_id="task-1"))
    backend.record_event(RuntimeEvent(event_type="runtime.started", task_id="task-2"))

    events = backend.list_events_for_task("task-1")

    assert len(events) == 2
    assert [event.event_type for event in events] == ["runtime.started", "runtime.completed"]


def test_runtime_event_serializes_to_surreal_record() -> None:
    backend = SurrealRuntimeBackend(
        SurrealRuntimeConfig(persist_enabled=False)
    )
    event = RuntimeEvent(event_type="runtime.started", task_id="task-1")

    record = backend.to_surreal_record(event)

    assert record["event_type"] == "runtime.started"
    assert record["task_id"] == "task-1"
    assert "event_id" in record
    assert "created_at" in record


def test_runtime_events_table_name_is_stable() -> None:
    backend = SurrealRuntimeBackend(
        SurrealRuntimeConfig(persist_enabled=False)
    )

    assert backend.runtime_events_table() == "runtime_events"
