"""LLM Client implementation"""

import logging
from typing import Any, Dict, List, Optional

from src.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    """LLM Client for interacting with different LLM providers"""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """Initialize the LLM client"""
        self.provider = provider or settings.DEFAULT_LLM
        self.model = model or settings.DEFAULT_MODEL
        self.client = self._initialize_client()
    
    def _initialize_client(self) -> Any:
        """Initialize the appropriate LLM client based on provider"""
        logger.info(f"Initializing LLM client for provider: {self.provider}, model: {self.model}")
        
        if self.provider == "openai":
            try:
                from openai import OpenAI
                return OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                logger.error("OpenAI library not installed")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                raise
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            except ImportError:
                logger.error("Anthropic library not installed")
                raise
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                raise
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_response(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response from the LLM"""
        logger.info(f"Generating response from {self.provider} using model {self.model}")
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                return response.choices[0].message.content or ""
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                return response.content[0].text or ""
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise
    
    def get_provider(self) -> str:
        """Get the current LLM provider"""
        return self.provider
    
    def get_model(self) -> str:
        """Get the current model"""
        return self.model
    
    def set_provider(self, provider: str) -> None:
        """Set the LLM provider"""
        self.provider = provider
        self.client = self._initialize_client()
    
    def set_model(self, model: str) -> None:
        """Set the model"""
        self.model = model
