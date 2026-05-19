from collections.abc import Callable
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph


ActionHandler = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


class RuntimeState(TypedDict, total=False):
    current_node: str
    completed: list[str]
    results: dict[str, Any]
    errors: dict[str, str]


class LangGraphAdapter:
    """
    LangGraph-backed execution adapter for AgentGraph-compatible plans.

    This adapter uses the real LangGraph StateGraph API and delegates
    action execution to an injected runtime action handler.
    """

    def __init__(self, plan: dict, action_handler: ActionHandler):
        self.plan = plan
        self.action_handler = action_handler

    def build(self):
        workflow = StateGraph(RuntimeState)

        nodes = self.plan["nodes"]
        edges = self.plan.get("edges", [])
        node_map = {node["id"]: node for node in nodes}

        for node in nodes:

            def execute(state: RuntimeState, node_id=node["id"]) -> RuntimeState:
                completed = list(state.get("completed", []))
                results = dict(state.get("results", {}))
                errors = dict(state.get("errors", {}))
                node_payload = node_map[node_id]

                try:
                    results[node_id] = self.action_handler(node_payload, dict(state))
                    completed.append(node_id)
                except Exception as exc:
                    errors[node_id] = str(exc)
                    return {
                        "current_node": node_id,
                        "completed": completed,
                        "results": results,
                        "errors": errors,
                    }

                return {
                    "current_node": node_id,
                    "completed": completed,
                    "results": results,
                    "errors": errors,
                }

            workflow.add_node(node["id"], execute)

        workflow.add_edge(START, nodes[0]["id"])

        for edge in edges:
            workflow.add_edge(edge["from"], edge["to"])

        source_nodes = {edge["from"] for edge in edges}
        leaf_nodes = {node["id"] for node in nodes if node["id"] not in source_nodes}

        for leaf in leaf_nodes:
            workflow.add_edge(leaf, END)

        return workflow.compile()
