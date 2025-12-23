from typing import Optional
from .registry import ModelRegistry
from .base import BaseModel


class ModelManager:
    def __init__(self, registry: Optional[ModelRegistry] = None):
        self._registry = registry or ModelRegistry()
        self._default_model: Optional[str] = None

    def set_default_model(self, model_name: str) -> None:
        if model_name not in self._registry.list_models():
            raise ValueError(f"Model '{model_name}' not found")
        self._default_model = model_name

    def get_default_model(self) -> Optional[BaseModel]:
        if not self._default_model:
            return None
        return self._registry.get_model(self._default_model)

    async def generate(
        self, prompt: str, model_name: Optional[str] = None, **kwargs
    ) -> str:
        model = self._get_model(model_name)
        return await model.generate(prompt, **kwargs)

    def _get_model(self, model_name: Optional[str]) -> BaseModel:
        if model_name:
            model = self._registry.get_model(model_name)
            if not model:
                raise ValueError(f"Model '{model_name}' not found")
            return model

        default_model = self.get_default_model()
        if not default_model:
            raise ValueError("No model specified and no default model set")

        return default_model
