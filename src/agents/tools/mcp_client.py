"""MCP客户端核心实现"""

import logging
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any, Dict, List, Optional

from .mcp_config import MCPConfig, TransportType
from .mcp_tool import MCPBaseTool

logger = logging.getLogger(__name__)

try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
    from mcp.client.stdio import StdioServerParameters, stdio_client

    HAS_MCP = True
except ImportError:
    logger.warning("未安装 mcp 库，MCP 功能将不可用。请运行 'pip install mcp' 安装。")
    HAS_MCP = False
    ClientSession = Any
    StdioServerParameters = Any


class MCPClient:
    """MCP客户端"""

    def __init__(self, config: MCPConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self._connected: bool = False
        self._exit_stack = AsyncExitStack()

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        """连接到MCP服务器"""
        if not HAS_MCP:
            raise RuntimeError("未安装 mcp 库，无法使用 MCP 功能。请运行 'pip install mcp' 安装。")

        try:
            if self.config.transport == TransportType.STDIO:
                server_params = StdioServerParameters(
                    command=self.config.command or "python",
                    args=self.config.args or [],
                    env=self.config.env,
                )
                read, write = await self._exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
            elif self.config.transport in [
                TransportType.HTTP_SSE,
                TransportType.HTTP_STREAMABLE,
            ]:
                url = self.config.url or ""
                read, write = await self._exit_stack.enter_async_context(
                    sse_client(url)
                )
            else:
                raise ValueError(f"不支持的传输类型: {self.config.transport}")

            session = await self._exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.session = session

            self._connected = True
            logger.info(f"成功连接到MCP服务器: {self.config.transport.value}")

        except Exception as e:
            await self.disconnect()
            logger.error(f"连接MCP服务器失败: {e}")
            raise

    async def disconnect(self) -> None:
        """断开连接"""
        await self._exit_stack.aclose()
        self._exit_stack = AsyncExitStack()
        self.session = None
        self._connected = False
        logger.info("已断开MCP服务器连接")

    async def list_tools(self, prefix: Optional[str] = None) -> List[MCPBaseTool]:
        """获取工具列表"""
        if not self.session:
            raise RuntimeError("未连接到MCP服务器")

        result = await self.session.list_tools()
        tools = []
        for tool in result.tools:
            tool_dict = tool.model_dump()
            tools.append(
                MCPBaseTool(
                    name=tool_dict.get("name", ""),
                    description=tool_dict.get("description", ""),
                    input_schema=tool_dict.get(
                        "inputSchema", {"type": "object", "properties": {}}
                    ),
                    client=self,
                    prefix=prefix,
                )
            )
        return tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.session:
            raise RuntimeError("未连接到MCP服务器")

        result = await self.session.call_tool(name, arguments)
        return {
            "content": [item.model_dump() for item in result.content],
            "is_error": getattr(result, "isError", False),
        }

    async def list_resources(self) -> List[Dict[str, Any]]:
        """获取资源列表"""
        if not self.session:
            raise RuntimeError("未连接到MCP服务器")

        result = await self.session.list_resources()
        return [r.model_dump() for r in result.resources]

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """读取资源"""
        if not self.session:
            raise RuntimeError("未连接到MCP服务器")

        result = await self.session.read_resource(uri)
        return result.model_dump()

    @asynccontextmanager
    async def connection(self):
        """上下文管理器连接"""
        await self.connect()
        try:
            yield self
        finally:
            await self.disconnect()
