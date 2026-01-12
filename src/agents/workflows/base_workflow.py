from abc import ABC, abstractmethod
from typing import Any


class BaseWorkflow(ABC):
    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        raise NotImplementedError
