from src.agents.llm.base import BaseModel
from src.agents.service.file_agents import FileCleanupAgent, FileOrganizerAgent, FileRenamerAgent
from src.agents.tools.registry import ToolRegistry


class FakeModel(BaseModel):
    @property
    def name(self) -> str:
        return "fake"

    @property
    def provider(self) -> str:
        return "fake"

    @property
    def function_calling(self) -> bool:
        return False

    async def generate(self, prompt: str, **kwargs) -> str:
        return "Final Answer: ok"


def test_file_agents_agent_card_only_lists_allowed_tools() -> None:
    registry = ToolRegistry()
    registry.scan_skills()

    organizer = FileOrganizerAgent(model=FakeModel(), tools=registry, max_iterations=1)
    renamer = FileRenamerAgent(model=FakeModel(), tools=registry, max_iterations=1)
    cleanup = FileCleanupAgent(model=FakeModel(), tools=registry, max_iterations=1)

    organizer_tools = {s["tool"] for s in organizer.agent_card["skill_list"]}
    assert "batch-file-move" in organizer_tools
    assert "batch-file-delete" not in organizer_tools

    renamer_tools = {s["tool"] for s in renamer.agent_card["skill_list"]}
    assert renamer_tools == {"batch-file-search", "batch-file-rename"}

    cleanup_tools = {s["tool"] for s in cleanup.agent_card["skill_list"]}
    assert cleanup_tools == {"batch-file-search", "batch-file-delete"}

