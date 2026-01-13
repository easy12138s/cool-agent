import pytest

from src.agents.llm.base import BaseModel


class FlakyModel(BaseModel):
    def __init__(self) -> None:
        self.calls = 0

    @property
    def name(self) -> str:
        return "flaky"

    @property
    def provider(self) -> str:
        return "test"

    @property
    def function_calling(self) -> bool:
        return False

    async def generate(self, prompt: str, **kwargs) -> str:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("boom")
        return "ok"


@pytest.mark.anyio
async def test_generate_with_retry_can_retry_once() -> None:
    model = FlakyModel()
    out = await model.generate_with_retry("hi", max_retries=1, timeout_s=5)
    assert out == "ok"
    assert model.calls == 2


@pytest.mark.anyio
async def test_generate_with_retry_validates_timeout() -> None:
    model = FlakyModel()
    with pytest.raises(ValueError):
        await model.generate_with_retry("hi", timeout_s=0)
