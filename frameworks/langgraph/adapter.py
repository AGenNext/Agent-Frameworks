from collections.abc import Callable
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph


ActionHandler = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


class RuntimeState(TypedDict, total=False):
    current_node: str
    completed: list[str]
    results: dict[str, Any]
    errors: dict[str, str]


class LangGraphAdapter:
    """
    Temporary execution adapter.

    Accepts AgentGraph-compatible plans and translates them into
    LangGraph execution graphs.

    This adapter does not own runtime execution. It delegates node actions
    to an injected action handler supplied by Agent-Runtime.
    """

    def __init__(self, plan: dict, action_handler: ActionHandler | None = None):
        self.plan = plan
        self.action_handler = action_handler or self.default_action_handler

    def default_action_handler(self, node: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "completed",
            "action": node.get("action"),
            "input": node.get("input", {}),
            "note": "No action handler supplied; dry-run completion only.",
        }

    def build(self):
        workflow = StateGraph(RuntimeState)

        nodes = self.plan.get("nodes", [])
        edges = self.plan.get("edges", [])
        node_map = {node["id"]: node for node in nodes}

        for node in nodes:

            def execute(state, node_id=node["id"]):
                completed = list(state.get("completed", []))
                results = dict(state.get("results", {}))
                errors = dict(state.get("errors", {}))
                node_payload = node_map[node_id]

                try:
                    result = self.action_handler(node_payload, state)
                    results[node_id] = result
                    completed.append(node_id)
                except Exception as exc:
                    errors[node_id] = str(exc)
                    raise

                return {
                    "current_node": node_id,
                    "completed": completed,
                    "results": results,
                    "errors": errors,
                }

            workflow.add_node(node["id"], execute)

        for edge in edges:
            workflow.add_edge(edge["from"], edge["to"])

        if nodes:
            workflow.set_entry_point(nodes[0]["id"])

        leaf_nodes = {
            node["id"]
            for node in nodes
            if node["id"] not in {edge["from"] for edge in edges}
        }

        for leaf in leaf_nodes:
            workflow.add_edge(leaf, END)

        return workflow.compile()
