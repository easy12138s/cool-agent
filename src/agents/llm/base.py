from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import anyio


class BaseModel(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def provider(self) -> str:
        pass

    @property
    @abstractmethod
    def function_calling(self) -> bool:
        pass

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass

    async def stream_generate(self, prompt: str, **kwargs):
        """Default implementation for non-streaming llm (yields once)."""
        response = await self.generate(prompt, **kwargs)
        yield response

    async def generate_with_retry(
        self,
        prompt: str,
        *,
        timeout_s: float = 60.0,
        max_retries: int = 2,
        backoff_s: float = 0.5,
        **kwargs: Any,
    ) -> str:
        if timeout_s <= 0:
            raise ValueError("timeout_s 必须为正数")
        if max_retries < 0:
            raise ValueError("max_retries 不能为负数")
        if backoff_s < 0:
            raise ValueError("backoff_s 不能为负数")

        last_error: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                with anyio.fail_after(timeout_s):
                    return await self.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                if attempt >= max_retries:
                    raise
                await anyio.sleep(backoff_s * (2**attempt))
        raise last_error or RuntimeError("模型调用失败")

    def get_model_info(self) -> Dict[str, Any]:
        return {"name": self.name, "provider": self.provider}
