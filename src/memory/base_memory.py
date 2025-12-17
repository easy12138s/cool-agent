"""Base Memory classes"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseMemory(ABC):
    """Base class for all memory implementations"""
    
    def __init__(self, **kwargs: Any):
        """Initialize the memory"""
        self.max_items: int = kwargs.get("max_items", 100)
        self.memory_type: str = kwargs.get("memory_type", "base")
    
    @abstractmethod
    def add(self, key: str, value: Any, **kwargs: Any) -> None:
        """Add an item to memory"""
        pass
    
    @abstractmethod
    def get(self, key: str, **kwargs: Any) -> Optional[Any]:
        """Get an item from memory"""
        pass
    
    @abstractmethod
    def remove(self, key: str, **kwargs: Any) -> None:
        """Remove an item from memory"""
        pass
    
    @abstractmethod
    def clear(self, **kwargs: Any) -> None:
        """Clear all memory"""
        pass
    
    @abstractmethod
    def get_all(self, **kwargs: Any) -> Dict[str, Any]:
        """Get all items from memory"""
        pass
    
    def reset(self) -> None:
        """Reset memory to initial state"""
        self.clear()
    
    def get_info(self) -> Dict[str, Any]:
        """Get memory information"""
        return {
            "memory_type": self.memory_type,
            "max_items": self.max_items,
            "current_items": len(self.get_all()),
        }
