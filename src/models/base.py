from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseModel(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        pass
    
    @property
    @abstractmethod
    def function_calling(self) -> bool:
        pass

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider
        }