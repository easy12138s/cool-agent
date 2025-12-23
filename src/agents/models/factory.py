from typing import Dict, Any, Type
from .base import BaseModel
from .model_adapter import OpenAIModel, XFSparkModel, DeepSeekModel, OpenAICompatibleModel

class ModelFactory:
    model_map = {
        "openai": OpenAIModel,
        "xf-spark": XFSparkModel,
        "deepseek": DeepSeekModel,
        # 兼容 OpenAI 协议的通用模型适配器
        "openai-compatible": OpenAICompatibleModel
    }

    def create_model(self, config: Dict[str, Any]) -> BaseModel:
        provider = config.get("provider", "").lower()
        
        model_class = ModelFactory.model_map.get(provider)
        if not model_class:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return model_class(config)


model_factory = ModelFactory()
