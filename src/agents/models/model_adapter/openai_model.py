from typing import List, Dict, Any
from src.models import BaseModel
import aiohttp

class OpenAIModel(BaseModel):
    def __init__(self, config: Dict[str, Any]):
        self._name = config.get("name", "gpt-3.5-turbo")
        self._api_key = config.get("api_key")
        self._base_url = config.get("base_url", "https://api.openai.com/v1")
        self._model = config.get("model", "gpt-3.5-turbo")
        self._max_tokens = config.get("max_tokens", 4000)
        self._temperature = config.get("temperature", 0.7)
        
        if not self._api_key:
            raise ValueError("API key is required")
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def provider(self) -> str:
        return "openai"
    
    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", self._max_tokens),
                "temperature": kwargs.get("temperature", self._temperature)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                        
        except ImportError:
            raise ImportError("aiohttp is required for OpenAI model. Install it with: pip install aiohttp")
        except Exception as e:
            raise Exception(f"Failed to generate text: {str(e)}")
    
    async def generate_batch(self, prompts: List[str], **kwargs) -> List[str]:
        try:
            
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            }
            
            results = []
            for prompt in prompts:
                data = {
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get("max_tokens", self._max_tokens),
                    "temperature": kwargs.get("temperature", self._temperature)
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self._base_url}/chat/completions",
                        headers=headers,
                        json=data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            results.append(result["choices"][0]["message"]["content"])
                        else:
                            results.append(f"Error: {response.status}")
            
            return results
            
        except ImportError:
            raise ImportError("aiohttp is required for OpenAI model. Install it with: pip install aiohttp")
        except Exception as e:
            raise Exception(f"Failed to generate batch text: {str(e)}")
    
    async def get_embedding(self, text: str, **kwargs) -> List[float]:
        try:            
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "input": text,
                "model": "text-embedding-ada-002"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self._base_url}/embeddings",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["data"][0]["embedding"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                        
        except ImportError:
            raise ImportError("aiohttp is required for OpenAI model. Install it with: pip install aiohttp")
        except Exception as e:
            raise Exception(f"Failed to get embedding: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "model": self._model,
            "max_tokens": self._max_tokens,
            "temperature": self._temperature
        }