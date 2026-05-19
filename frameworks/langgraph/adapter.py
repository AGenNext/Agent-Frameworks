from typing import TypedDict

from langgraph.graph import END, StateGraph


class RuntimeState(TypedDict, total=False):
    current_node: str
    completed: list[str]


class LangGraphAdapter:
    """
    Temporary execution adapter.

    Accepts AgentGraph-compatible plans and
    translates them into LangGraph execution graphs.
    """

    def __init__(self, plan: dict):
        self.plan = plan

    def build(self):
        workflow = StateGraph(RuntimeState)

        nodes = self.plan.get("nodes", [])
        edges = self.plan.get("edges", [])

        for node in nodes:

            def execute(state, node_id=node["id"]):
                completed = state.get("completed", [])
                completed.append(node_id)

                return {
                    "current_node": node_id,
                    "completed": completed,
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
