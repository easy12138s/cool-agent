"""Tool Registry for managing tools"""

import logging
from typing import Any, Dict, List, Optional

from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing tools"""
    
    def __init__(self):
        """Initialize the tool registry"""
        self.tools: Dict[str, BaseTool] = {}
        logger.info("ToolRegistry initialized")
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool"""
        if not isinstance(tool, BaseTool):
            raise ValueError(f"Tool must be an instance of BaseTool, got {type(tool)}")
        
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool information by name"""
        tool = self.get_tool(name)
        if tool:
            return tool.get_info()
        return None
    
    def get_all_tools_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information for all tools"""
        return {
            name: tool.get_info()
            for name, tool in self.tools.items()
        }
    
    def run_tool(self, name: str, **kwargs: Any) -> Any:
        """Run a tool by name"""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        logger.info(f"Running tool: {name} with kwargs: {kwargs}")
        return tool.run(**kwargs)
    
    def unregister_tool(self, name: str) -> None:
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Unregistered tool: {name}")
    
    def clear(self) -> None:
        """Clear all tools"""
        self.tools.clear()
        logger.info("Cleared all tools from registry")
