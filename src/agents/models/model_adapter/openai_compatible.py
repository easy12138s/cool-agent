from typing import Dict, Any, AsyncGenerator, List, Optional
from ..base import BaseModel
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAICompatibleModel(BaseModel):
    """
    Base class for OpenAI-compatible models (OpenAI, DeepSeek, Moonshot, etc.).
    Uses the official AsyncOpenAI client for better performance and standard compliance.
    """

    def __init__(self, config: Dict[str, Any]):
        self._name = config.get("name", "openai-compatible")
        self._provider = config.get("provider", "openai")
        self._api_key = config.get("api_key")
        self._base_url = config.get("base_url")
        self._model = config.get("model")
        self._max_tokens = config.get("max_tokens", 4096)
        self._temperature = config.get("temperature", 0.7)
        self._function_calling = config.get("function_calling", False)

        if not self._api_key:
            raise ValueError(f"API key is required for {self._name}")

        self.client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)

    @property
    def name(self) -> str:
        return self._name

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def function_calling(self) -> bool:
        return self._function_calling

    async def generate(self, prompt: str, **kwargs) -> str:
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
        # 如果提供了 system_prompt 且当前消息中没有 system 角色，则自动插入
        if "system_prompt" in kwargs and not any(
            m["role"] == "system" for m in messages
        ):
            messages.insert(0, {"role": "system", "content": kwargs["system_prompt"]})

        try:
            completion = await self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self._max_tokens),
                temperature=kwargs.get("temperature", self._temperature),
                stream=False,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from {self._name}: {e}")
            raise

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        messages = kwargs.get("messages", [{"role": "user", "content": prompt}])
        if "system_prompt" in kwargs and not any(
            m["role"] == "system" for m in messages
        ):
            messages.insert(0, {"role": "system", "content": kwargs["system_prompt"]})

        try:
            stream = await self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self._max_tokens),
                temperature=kwargs.get("temperature", self._temperature),
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming response from {self._name}: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "model": self._model,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature,
            "function_calling": self._function_calling,
            "base_url": self._base_url,
        }
