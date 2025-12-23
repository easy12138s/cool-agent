from typing import Dict, Any
from src.config import env
from .openai_compatible import OpenAICompatibleModel


class XFSparkModel(OpenAICompatibleModel):
    def __init__(self, config: Dict[str, Any]):
        # 设置讯飞星火的默认配置
        if "name" not in config:
            config["name"] = "generalv3.5"
        if "api_key" not in config:
            config["api_key"] = env.get("XF_SPARK_LITE_API_KEY")
        if "base_url" not in config:
            config["base_url"] = env.get("XF_SPARK_OPENAI_API_URL")
        if "model" not in config:
            config["model"] = env.get("XF_SPARK_LITE_MODEL_ID")
        if "provider" not in config:
            config["provider"] = "xf-spark"

        super().__init__(config)

    @property
    def provider(self) -> str:
        return "xf-spark"
