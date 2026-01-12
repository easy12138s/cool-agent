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
async def test_skill_batch_file_create_can_run(tmp_path) -> None:
    registry = ToolRegistry()
    registry.scan_skills()
    tool = registry.get_tool("batch-file-create")
    assert tool is not None

    result = await tool.run(
        target_path=str(tmp_path),
        file_template="test_{num}.txt",
        create_count=2,
        file_content="hello",
        overwrite=False,
    )

    assert result.get("error_msg") == ""
    assert result.get("success_count") == 2
    assert (tmp_path / "test_1.txt").exists()
    assert (tmp_path / "test_2.txt").exists()


@pytest.mark.anyio
async def test_skill_batch_file_rename_can_run(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")

    registry = ToolRegistry()
    registry.scan_skills()
    tool = registry.get_tool("batch-file-rename")
    assert tool is not None

    result = await tool.run(
        source_path=str(tmp_path),
        rename_rule="add_prefix",
        rule_params="p_",
        file_filter=".txt",
    )

    assert result.get("error_msg") == ""
    assert result.get("success_count") == 2
    assert (tmp_path / "p_a.txt").exists()
    assert (tmp_path / "p_b.txt").exists()


@pytest.mark.anyio
async def test_skill_batch_file_rename_replace_text_can_run(tmp_path) -> None:
    (tmp_path / "old_name.txt").write_text("x", encoding="utf-8")

    registry = ToolRegistry()
    registry.scan_skills()
    tool = registry.get_tool("batch-file-rename")
    assert tool is not None

    result = await tool.run(
        source_path=str(tmp_path),
        rename_rule="replace_text",
        rule_params="old:new",
        file_filter=".txt",
    )

    assert result.get("error_msg") == ""
    assert result.get("success_count") == 1
    assert (tmp_path / "new_name.txt").exists()


@pytest.mark.anyio
async def test_react_agent_can_finish() -> None:
    registry = ToolRegistry()
    registry.scan_skills()

    agent = ReActAgent(model=FakeModel(), tools=registry, max_iterations=1)
    result = await agent.run("hi")
    assert result == "ok"
