from typing import Any, Dict

from src.config import env

from .openai_compatible import OpenAICompatibleModel


class DeepSeekModel(OpenAICompatibleModel):
    def __init__(self, config: Dict[str, Any]):
        # 设置 DeepSeek 模型的默认配置
        if "api_key" not in config:
            config["api_key"] = env.get("DEEPSEEK_API_KEY")
        if "base_url" not in config:
            config["base_url"] = env.get("DEEPSEEK_API_URL", "https://api.deepseek.com")
        if "model" not in config:
            config["model"] = env.get("DEEPSEEK_MODEL_ID", "deepseek-chat")
        if "name" not in config:
            config["name"] = env.get("DEEPSEEK_MODEL_ID", "deepseek-chat")
        if "provider" not in config:
            config["provider"] = "deepseek"

        super().__init__(config)
