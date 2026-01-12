from typing import Any, Dict

from .openai_compatible import OpenAICompatibleModel


class OpenAIModel(OpenAICompatibleModel):
    def __init__(self, config: Dict[str, Any]):
        # 设置 OpenAI 模型相关的默认配置
        if "base_url" not in config:
            config["base_url"] = "https://api.openai.com/v1"
        if "model" not in config:
            config["model"] = "gpt-3.5-turbo"
        if "provider" not in config:
            config["provider"] = "openai"

        super().__init__(config)

    # 保留批量生成接口，方便与旧代码兼容
    async def generate_batch(self, prompts: list[str], **kwargs) -> list[str]:
        # 当前顺序调用，如有需要可改为并发实现
        results = []
        for prompt in prompts:
            try:
                res = await self.generate(prompt, **kwargs)
                results.append(res)
            except Exception as e:
                results.append(f"Error: {str(e)}")
        return results

    async def get_embedding(self, text: str, **kwargs) -> list[float]:
        try:
            response = await self.client.embeddings.create(
                input=text, model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")
