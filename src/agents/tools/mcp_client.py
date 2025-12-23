"""MCP客户端核心实现"""
import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
from datetime import datetime

from mcp import ClientSession
from mcp.client import stdio
from mcp.client.http import SSEClient, StreamableHTTPClient, HTTPClientConfig
from mcp.client.stdio import StdioServerParameters

from .mcp_config import MCPConfig, TransportType
from .mcp_tool import MCPTool

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP客户端"""

    def __init__(self, config: MCPConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self._connected: bool = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        """连接到MCP服务器"""
        try:
            if self.config.transport == TransportType.STDIO:
                await self._connect_stdio()
            elif self.config.transport in [TransportType.HTTP_SSE, TransportType.HTTP_STREAMABLE]:
                await self._connect_http()
            else:
                raise ValueError(f"不支持的传输类型: {self.config.transport}")

            self._connected = True
            logger.info(f"成功连接到MCP服务器: {self.config.transport.value}")

        except Exception as e:
            logger.error(f"连接MCP服务器失败: {e}")
            raise

    async def _connect_stdio(self) -> None:
        """STDIO连接"""
        server_params = StdioServerParameters(
            command=self.config.command or "python",
            args=self.config.args,
            env=self.config.env
        )
        stdio_transport = await stdio.create_stdio_transport(server_params)
        read_stream, write_stream = stdio_transport
        self.session = ClientSession(read_stream, write_stream)
        await self.session.initialize()

    async def _connect_http(self) -> None:
        """HTTP连接 (SSE/Streamable)"""
        http_config = HTTPClientConfig(
            server_url=self.config.url or "",
            headers=self.config.headers,
            timeout=self.config.timeout
        )

        if self.config.transport == TransportType.HTTP_SSE:
            client = SSEClient(http_config)
        else:
            client = StreamableHTTPClient(http_config)

        self.session = await client.connect()

    async def list_tools(self) -> List[MCPTool]:
        """获取工具列表"""
        if not self.session:
            raise RuntimeError("未连接到MCP服务器")

        result = await self.session.list_tools()
        return [MCPTool.from_mcp_tool(tool) for tool in result.tools]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.session:
            raise RuntimeError("未连接到MCP服务器")

        result = await self.session.call_tool(name, arguments)
        return {
            "content": [item.model_dump() for item in result.content],
            "is_error": getattr(result, "isError", False)
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

    async def disconnect(self) -> None:
        """断开连接"""
        if self.session:
            await self.session.close()
            self.session = None
        self._connected = False
        logger.info("已断开MCP服务器连接")

    @asynccontextmanager
    async def connection(self):
        """上下文管理器连接"""
        await self.connect()
        try:
            yield self
        finally:
            await self.disconnect()


class MCPToolRegistry:
    """MCP工具注册表 - 管理和缓存MCP工具"""

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._clients: Dict[str, MCPClient] = {}

    async def register_server(
        self,
        server_id: str,
        config: MCPConfig
    ) -> List[MCPTool]:
        """注册MCP服务器并获取工具"""
        client = MCPClient(config)
        await client.connect()

        tools = await client.list_tools()
        for tool in tools:
            self._tools[f"{server_id}.{tool.name}"] = tool

        self._clients[server_id] = client
        logger.info(f"已注册MCP服务器 {server_id}, 工具数量: {len(tools)}")
        return tools

    async def unregister_server(self, server_id: str) -> None:
        """注销MCP服务器"""
        if server_id in self._clients:
            await self._clients[server_id].disconnect()
            del self._clients[server_id]

        keys_to_remove = [k for k in self._tools if k.startswith(f"{server_id}.")]
        for key in keys_to_remove:
            del self._tools[key]

    def get_tool(self, full_name: str) -> Optional[MCPTool]:
        """获取工具"""
        return self._tools.get(full_name)

    def list_tools(self) -> List[MCPTool]:
        """列出所有工具"""
        return list(self._tools.values())

    async def call_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用工具"""
        client = self._clients.get(server_id)
        if not client:
            raise ValueError(f"MCP服务器 {server_id} 未注册")

        full_name = f"{server_id}.{tool_name}"
        tool = self._tools.get(full_name)
        if not tool:
            raise ValueError(f"工具 {full_name} 不存在")

        return await client.call_tool(tool_name, arguments)


default_registry = MCPToolRegistry()
