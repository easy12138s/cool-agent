from typing import Dict, Any, List, Optional
import logging
from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class MCPBaseTool(BaseTool):
    """MCP 工具的 BaseTool 适配器"""
    
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any], client: Any, prefix: Optional[str] = None):
        self._name = f"{prefix}_{name}" if prefix else name
        self._raw_name = name # 保留原始名称用于调用
        self._description = description
        self._input_schema = input_schema
        self.client = client # 引用所属的 MCPClient 以便执行

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> Dict[str, Any]:
        return self._input_schema

    async def run(self, **kwargs) -> Any:
        """通过 MCP Client 调用远程工具"""
        # 调用时使用原始名称
        return await self.client.call_tool(self._raw_name, kwargs)
