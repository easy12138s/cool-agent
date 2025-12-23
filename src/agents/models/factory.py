from typing import Dict, Any, Type
from .base import BaseModel
from .model_adapter import OpenAIModel, XFSparkModel, DeepSeekModel

class ModelFactory:
    model_map = {
        "openai": OpenAIModel,
        "xf-spark": XFSparkModel,
        "deepseek": DeepSeekModel
    }

    def create_model(self, config: Dict[str, Any]) -> BaseModel:
        provider = config.get("provider", "").lower()
        
        model_class = ModelFactory.model_map.get(provider)
        if not model_class:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return model_class(config)


model_factory = ModelFactory()
