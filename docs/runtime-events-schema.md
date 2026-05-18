# Runtime Events Schema

Runtime events are stored in the `runtime_events` table.

## Fields

- event_id
- event_type
- task_id
- objective
- scope
- status
- ready_for_human_review
- response_count
- metadata
- created_at

## Example SurrealQL

```sql
SELECT * FROM runtime_events WHERE task_id = $task_id ORDER BY created_at ASC;
```

## Example Event Types

- runtime.started
- runtime.completed
- runtime.failed
- a2a.handoff
- agent.response
- evaluation.completed
- trust.completed

## Final Rule

Runtime events should be append-only and queryable by task_id.
