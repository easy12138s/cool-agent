"""MCP工具封装"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    original_tool: Any = None

    @property
    def parameters(self) -> Dict[str, Any]:
        return self.input_schema.get("properties", {})

    @property
    def required_params(self) -> List[str]:
        return self.input_schema.get("required", [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }

    @classmethod
    def from_mcp_tool(cls, mcp_tool: Any) -> "MCPTool":
        tool_dict = mcp_tool.model_dump()
        return cls(
            name=tool_dict.get("name", ""),
            description=tool_dict.get("description", ""),
            input_schema=tool_dict.get("inputSchema", {"type": "object", "properties": {}}),
            original_tool=mcp_tool
        )
