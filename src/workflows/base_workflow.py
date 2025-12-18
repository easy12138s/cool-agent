"""Base Workflow classes"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseWorkflow(ABC):
    """Base class for all workflows"""
    
    def __init__(self, **kwargs: Any):
        """Initialize the workflow"""
        self.name: str = kwargs.get("name", self.__class__.__name__)
        self.description: str = kwargs.get("description", "A base workflow")
        self.timeout: int = kwargs.get("timeout", 300)
    
    @abstractmethod
    def run(self, **kwargs: Any) -> Any:
        """Run the workflow with the given arguments"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get workflow information"""
        return {
            "name": self.name,
            "description": self.description,
            "timeout": self.timeout,
        }
    
    def validate_inputs(self, **kwargs: Any) -> bool:
        """Validate the inputs"""
        # Default implementation - override in subclasses
        return True
    
    def on_start(self, **kwargs: Any) -> None:
        """Hook called when workflow starts"""
        pass
    
    def on_completion(self, result: Any, **kwargs: Any) -> None:
        """Hook called when workflow completes"""
        pass
    
    def on_failure(self, error: Exception, **kwargs: Any) -> None:
        """Hook called when workflow fails"""
        pass
