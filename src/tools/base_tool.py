"""Base Tool classes"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, **kwargs: Any):
        """Initialize the tool"""
        self.name: str = kwargs.get("name", self.__class__.__name__)
        self.description: str = kwargs.get("description", "A base tool")
        self.args_schema: Optional[Any] = kwargs.get("args_schema")
    
    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Run the tool with the given arguments"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "name": self.name,
            "description": self.description,
            "args_schema": self.args_schema.__name__ if self.args_schema else None,
        }
    
    def validate_args(self, **kwargs: Any) -> bool:
        """Validate the arguments"""
        if self.args_schema:
            try:
                self.args_schema(**kwargs)
                return True
            except Exception as e:
                return False
        return True
