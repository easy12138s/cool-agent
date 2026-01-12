import asyncio
import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml  # type: ignore[import]

from .base_tool import BaseTool
from .mcp_client import MCPClient
from .mcp_config import MCPConfig

logger = logging.getLogger(__name__)


class SkillTool(BaseTool):
    """基于 SKILL.md 定义的本地技能工具"""

    def __init__(self, skill_dir: Path, script_path: Optional[Path] = None):
        self.skill_dir = skill_dir
        self.skill_md_path = skill_dir / "SKILL.md"
        self._name = ""
        self._description = ""
        self._parameters = {"type": "object", "properties": {}, "required": []}
        self.script_path = script_path

        self._load_skill_md()

    def _load_skill_md(self) -> None:
        """解析 SKILL.md 中的 YAML 元数据和参数"""
        if not self.skill_md_path.exists():
            return

        with open(self.skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 YAML Front Matter
        if content.startswith("---"):
            try:
                _, front_matter, body = content.split("---", 2)
                metadata = yaml.safe_load(front_matter)
                self._name = metadata.get("name", self.skill_dir.name)
                self._description = metadata.get("description", "")

                # 从正文中解析参数
                if "parameters" in metadata:
                    self._parameters = metadata["parameters"]
                else:
                    pass
            except Exception as e:
                logger.error(f"解析 {self.skill_md_path} 失败: {e}")

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters

    async def run(self, **kwargs) -> Any:
        """运行脚本执行技能"""
        if not self.script_path or not self.script_path.exists():
            raise FileNotFoundError(f"找不到执行脚本: {self.script_path}")

        # 动态加载并运行脚本中的 run 函数
        try:
            spec = importlib.util.spec_from_file_location(
                "skill_script", self.script_path
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"无法加载脚本模块: {self.script_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "run"):
                if asyncio.iscoroutinefunction(module.run):
                    return await module.run(**kwargs)
                else:
                    return module.run(**kwargs)
            else:
                raise AttributeError(f"脚本 {self.script_path} 中未定义 run 函数")
        except Exception as e:
            logger.error(f"执行技能 {self.name} 失败: {e}")
            return {"error": str(e)}


class ToolRegistry:
    """工具注册表 - 负责自动发现和管理所有工具"""

    def __init__(
        self,
        skills_dir: Optional[str] = None,
        scripts_dir: Optional[str] = None,
    ) -> None:
        # 默认路径
        root_dir = Path(__file__).parent.parent.parent.parent
        self.skills_dir = (
            Path(skills_dir) if skills_dir else root_dir / "src" / "agents" / "skills"
        )
        self.scripts_dir = (
            Path(scripts_dir)
            if scripts_dir
            else root_dir / "src" / "agents" / "tools" / "scripts"
        )

        self._tools: Dict[str, BaseTool] = {}
        self._mcp_clients: Dict[str, MCPClient] = {}

    def scan_skills(self) -> None:
        """扫描 skills 目录并自动注册工具"""
        if not self.skills_dir.exists():
            logger.warning(f"技能目录不存在: {self.skills_dir}")
            return

        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                # 寻找匹配的脚本
                script_name = self._map_skill_to_script(skill_path.name)
                script_path = self.scripts_dir / f"{script_name}.py"

                try:
                    tool = SkillTool(
                        skill_path, script_path if script_path.exists() else None
                    )
                    if tool.name:
                        self.register(tool)
                        logger.info(f"已自动注册技能工具: {tool.name}")
                except Exception as e:
                    logger.error(f"注册技能 {skill_path.name} 失败: {e}")

    def _map_skill_to_script(self, skill_name: str) -> str:
        """将技能文件夹名映射为脚本文件名"""
        # 规则：batch-file-search -> batch_search
        # 规则：batch-text-replace -> batch_replace
        name = (
            skill_name.replace("-file-", "_").replace("-text-", "_").replace("-", "_")
        )
        return name

    def register(self, tool: BaseTool):
        """手动注册工具"""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取指定名称的工具"""
        return self._tools.get(name)

    def list_tools(self) -> List[BaseTool]:
        """列出所有已注册工具"""
        return list(self._tools.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具的 OpenAI 格式描述"""
        return [tool.to_openai_tool() for tool in self._tools.values()]

    # --- MCP 服务器管理 ---

    async def register_mcp_server(self, server_id: str, config: MCPConfig):
        """注册并连接一个 MCP 服务器"""
        if server_id in self._mcp_clients:
            logger.warning(f"MCP 服务器 {server_id} 已存在，正在重新连接...")
            await self.unregister_mcp_server(server_id)

        client = MCPClient(config)
        try:
            await client.connect()
            tools = await client.list_tools(prefix=server_id)
            for tool in tools:
                self._tools[tool.name] = tool

            self._mcp_clients[server_id] = client
            logger.info(f"已成功注册 MCP 服务器 {server_id}，新增 {len(tools)} 个工具")
        except Exception as e:
            logger.error(f"注册 MCP 服务器 {server_id} 失败: {e}")
            raise

    async def unregister_mcp_server(self, server_id: str):
        """断开并注销一个 MCP 服务器"""
        if server_id in self._mcp_clients:
            client = self._mcp_clients.pop(server_id)
            await client.disconnect()

            # 移除该服务器关联的所有工具
            prefix = f"{server_id}_"
            keys_to_remove = [k for k in self._tools if k.startswith(prefix)]
            for k in keys_to_remove:
                self._tools.pop(k)
            logger.info(f"已注销 MCP 服务器 {server_id}")


# 全局默认注册表
default_registry = ToolRegistry()
