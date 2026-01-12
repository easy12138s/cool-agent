"""MCP配置模型"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TransportType(str, Enum):
    STDIO = "stdio"
    HTTP_SSE = "http_sse"
    HTTP_STREAMABLE = "http_streamable"


class MCPConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        validate_assignment=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )

    transport: TransportType = TransportType.HTTP_SSE
    command: Optional[str] = None
    args: list[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    url: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    timeout: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v, info):
        if info.data.get("transport") in ["http_sse", "http_streamable"] and not v:
            raise ValueError(f"{info.data.get('transport')} 需要URL参数")
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL必须以http://或https://开头")
        return v

    @field_validator("command")
    @classmethod
    def validate_command(cls, v, info):
        if info.data.get("transport") == "stdio" and not v:
            raise ValueError("stdio传输需要command参数")
        return v

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPConfig":
        if "transport" in data and isinstance(data["transport"], str):
            data["transport"] = TransportType(data["transport"])
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transport": (
                self.transport.value
                if isinstance(self.transport, TransportType)
                else self.transport
            ),
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "url": self.url,
            "headers": self.headers,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }
