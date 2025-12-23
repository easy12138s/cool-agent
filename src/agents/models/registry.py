from typing import Dict, List, Optional
from .base import BaseModel


class ModelRegistry:
    def __init__(self):
        self._models: Dict[str, BaseModel] = {}
        self._providers: Dict[str, List[str]] = {}

    def register(self, model: BaseModel) -> None:
        self._models[model.name] = model
        if model.provider not in self._providers:
            self._providers[model.provider] = []
        if model.name not in self._providers[model.provider]:
            self._providers[model.provider].append(model.name)

    def unregister(self, model_name: str) -> bool:
        if model_name not in self._models:
            return False

        model = self._models.pop(model_name)
        self._providers[model.provider].remove(model_name)
        if not self._providers[model.provider]:
            del self._providers[model.provider]

        return True

    def get_model(self, model_name: str) -> Optional[BaseModel]:
        return self._models.get(model_name)

    def list_models(self) -> List[str]:
        return list(self._models.keys())

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())

    def get_models_by_provider(self, provider: str) -> List[BaseModel]:
        model_names = self._providers.get(provider, [])
        return [self._models[name] for name in model_names if name in self._models]
