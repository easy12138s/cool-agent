"""Intelligent Agent Project - Main package"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .config import settings
from .core import Agent
from .models import LLMClient
from .tools import ToolRegistry
from .memory import BaseMemory
from .workflows import BaseWorkflow

__all__ = [
    "settings",
    "Agent",
    "LLMClient",
    "ToolRegistry",
    "BaseMemory",
    "BaseWorkflow",
]
