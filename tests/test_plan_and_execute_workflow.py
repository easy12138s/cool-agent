import json

import pytest

from src.agents.llm.base import BaseModel
from src.agents.tools.registry import ToolRegistry
from src.agents.workflows import PlanAndExecuteWorkflow


class FakePlannerModel(BaseModel):
    @property
    def name(self) -> str:
        return "fake-planner"

    @property
    def provider(self) -> str:
        return "fake"

    @property
    def function_calling(self) -> bool:
        return False

    async def generate(self, prompt: str, **kwargs) -> str:
        start = prompt.find("WORKSPACE_DIR=")
        if start == -1:
            raise ValueError("prompt missing WORKSPACE_DIR")
        workspace_dir = prompt[start:].split("\n", 1)[0].split("=", 1)[1].strip()

        plan = {
            "steps": [
                {
                    "name": "创建两个测试文件",
                    "tool": "batch-file-create",
                    "args": {
                        "target_path": workspace_dir,
                        "file_template": "week_{num}.md",
                        "create_count": 2,
                        "file_content": "hello",
                        "overwrite": False,
                    },
                }
            ]
        }
        return json.dumps(plan, ensure_ascii=False)


@pytest.mark.anyio
async def test_plan_and_execute_workflow_can_run_batch_create(tmp_path) -> None:
    registry = ToolRegistry()
    registry.scan_skills()

    workflow = PlanAndExecuteWorkflow(model=FakePlannerModel(), tools=registry)
    report = await workflow.run(user_input=f"WORKSPACE_DIR={tmp_path}")

    assert report["user_input"].startswith("WORKSPACE_DIR=")
    assert report["steps"][0]["ok"] is True
    assert (tmp_path / "week_1.md").exists()
    assert (tmp_path / "week_2.md").exists()

