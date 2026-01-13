from typing import Any, Dict, Optional

from ..llm.base import BaseModel
from ..memory.short_term_memory import ShortTermMemory
from ..prompt.file_cleanup import FILE_CLEANUP_PROMPT
from ..prompt.file_organizer import FILE_ORGANIZER_PROMPT
from ..prompt.file_renamer import FILE_RENAMER_PROMPT
from ..tools.registry import ToolRegistry
from .react_agent import ReActAgent


class FileOrganizerAgent(ReActAgent):
    def __init__(
        self,
        model: BaseModel,
        tools: ToolRegistry,
        memory: Optional[ShortTermMemory] = None,
        max_iterations: int = 10,
    ):
        super().__init__(
            model=model,
            tools=tools,
            memory=memory,
            max_iterations=max_iterations,
            allowed_tools={
                "batch-file-search",
                "batch-file-move",
                "batch-file-copy",
                "batch-file-rename",
                "batch-file-create",
            },
        )

    @property
    def agent_card(self) -> Dict[str, Any]:
        return {
            "name": "文件整理助手",
            "description": "面向文件归档、分类、搬运与批量整理的助手",
            "skill_list": [
                {"tool": t.name, "tool_description": t.description}
                for t in self.tools.list_tools()
                if self.allowed_tools is None or t.name in self.allowed_tools
            ],
            "permission": "local",
        }

    @property
    def sys_prompt(self) -> str:
        return FILE_ORGANIZER_PROMPT


class FileRenamerAgent(ReActAgent):
    def __init__(
        self,
        model: BaseModel,
        tools: ToolRegistry,
        memory: Optional[ShortTermMemory] = None,
        max_iterations: int = 10,
    ):
        super().__init__(
            model=model,
            tools=tools,
            memory=memory,
            max_iterations=max_iterations,
            allowed_tools={"batch-file-search", "batch-file-rename"},
        )

    @property
    def agent_card(self) -> Dict[str, Any]:
        return {
            "name": "文件命名助手",
            "description": "面向批量重命名与命名规范统一的助手",
            "skill_list": [
                {"tool": t.name, "tool_description": t.description}
                for t in self.tools.list_tools()
                if self.allowed_tools is None or t.name in self.allowed_tools
            ],
            "permission": "local",
        }

    @property
    def sys_prompt(self) -> str:
        return FILE_RENAMER_PROMPT


class FileCleanupAgent(ReActAgent):
    def __init__(
        self,
        model: BaseModel,
        tools: ToolRegistry,
        memory: Optional[ShortTermMemory] = None,
        max_iterations: int = 10,
    ):
        super().__init__(
            model=model,
            tools=tools,
            memory=memory,
            max_iterations=max_iterations,
            allowed_tools={"batch-file-search", "batch-file-delete"},
        )

    @property
    def agent_card(self) -> Dict[str, Any]:
        return {
            "name": "文件清理助手",
            "description": "面向清理无用文件与按规则批量删除的助手",
            "skill_list": [
                {"tool": t.name, "tool_description": t.description}
                for t in self.tools.list_tools()
                if self.allowed_tools is None or t.name in self.allowed_tools
            ],
            "permission": "local",
        }

    @property
    def sys_prompt(self) -> str:
        return FILE_CLEANUP_PROMPT

