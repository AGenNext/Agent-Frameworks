import json

from adapter import LangGraphAdapter


with open("examples/kimsufi_bootstrap_plan.json", "r") as f:
    plan = json.load(f)

adapter = LangGraphAdapter(plan)
workflow = adapter.build()

result = workflow.invoke(
    {
        "completed": []
    }
)

print(result)
