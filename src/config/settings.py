"""Settings module for the Intelligent Agent Project"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_LLM: str = "openai"
    DEFAULT_MODEL: str = "gpt-4"
    
    # Agent Configuration
    AGENT_NAME: str = "Intelligent Agent"
    AGENT_VERSION: str = "0.1.0"
    AGENT_DESCRIPTION: str = "An intelligent AI agent"
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    
    # Memory Configuration
    MEMORY_TYPE: str = "in_memory"
    MEMORY_MAX_ITEMS: int = 100
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "agent.log"
    
    # Tool Configuration
    TOOL_REGISTRY_PATH: str = "src/tools"
    
    # Workflow Configuration
    WORKFLOW_DEFAULT_TIMEOUT: int = 300
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create a global instance of settings
settings = Settings()
