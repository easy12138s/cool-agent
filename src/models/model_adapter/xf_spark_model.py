from typing import Dict, Any
from src.config import env
from src.models import BaseModel
from openai import OpenAI


class XFSparkModel(BaseModel):
    def __init__(self, config: Dict[str, Any]):
        self._name = config.get("name", "generalv3.5")
        self._api_key = config.get("api_key", env.get("XF_SPARK_LITE_API_KEY"))
        self._base_url = config.get("base_url", env.get("XF_SPARK_OPENAI_API_URL"))
        self._model = config.get("model", env.get("XF_SPARK_LITE_MODEL_ID"))
        self._max_tokens = config.get("max_tokens", 4000)
        self._temperature = config.get("temperature", 0.7)
        self._function_calling = config.get("function_calling", False)

        if not self._api_key:
            raise ValueError("API key is required")

    @property
    def name(self) -> str:
        return self._name·
    
    @property
    def provider(self) -> str:
        return "xf-spark"

    @property
    def function_calling(self) -> bool:
        return self._function_calling

    async def generate(self, prompt: str, **kwargs) -> str:
        client = OpenAI(
            api_key=f"Bearer {self._api_key}", 
            base_url = self._base_url
        )

        completion = client.chat.completions.create(
            model=self._model, # 指定请求的版本
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content
    
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "model": self._model,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
            "function_calling": self._function_calling
        }