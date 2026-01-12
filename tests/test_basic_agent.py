import pytest

from src.agents.llm.base import BaseModel
from src.agents.service.react_agent import ReActAgent
from src.agents.tools.registry import ToolRegistry


class FakeModel(BaseModel):
    @property
    def name(self) -> str:
        return "fake-model"

    @property
    def provider(self) -> str:
        return "fake"

    @property
    def function_calling(self) -> bool:
        return False

    async def generate(self, prompt: str, **kwargs) -> str:
        return "Final Answer: ok"


def test_tool_registry_scan_skills() -> None:
    registry = ToolRegistry()
    registry.scan_skills()
    assert registry.list_tools()


@pytest.mark.anyio
async def test_react_agent_can_finish() -> None:
    registry = ToolRegistry()
    registry.scan_skills()

    agent = ReActAgent(model=FakeModel(), tools=registry, max_iterations=1)
    result = await agent.run("hi")
    assert result == "ok"
