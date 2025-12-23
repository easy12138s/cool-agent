from typing import Dict, Any
from src.config import env
from src.agents.models import BaseModel
from openai import OpenAI


class DeepSeekModel(BaseModel):
    def __init__(self, config: Dict[str, Any]):
        self._name = config.get("name", env.get("DEEPSEEK_MODEL_ID", "deepseek-chat"))
        self._api_key = config.get("api_key", env.get("DEEPSEEK_API_KEY"))
        self._base_url = config.get("base_url", env.get("DEEPSEEK_API_URL", "https://api.deepseek.com"))
        self._model = config.get("model", env.get("DEEPSEEK_MODEL_ID", "deepseek-chat"))
        self._max_tokens = config.get("max_tokens", 4096)
        self._temperature = config.get("temperature", 0.7)
        self._function_calling = config.get("function_calling", False)

        if not self._api_key:
            raise ValueError("API key is required")

    @property
    def name(self) -> str:
        return self._name

    @property
    def provider(self) -> str:
        return "deepseek"

    @property
    def function_calling(self) -> bool:
        return self._function_calling

    async def generate(self, prompt: str, **kwargs) -> str:
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])

        client = OpenAI(
            api_key=self._api_key,
            base_url=self._base_url
        )

        completion = client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=False
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
