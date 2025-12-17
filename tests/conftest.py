"""Pytest configuration and fixtures"""

import pytest
from typing import Any, Dict, Optional

from src.agents import Agent
from src.models import LLMClient
from src.tools import ToolRegistry

@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing"""
    # Note: This is a placeholder. In real tests, you'd use a mocking library
    # to mock the actual LLM client behavior
    return LLMClient(provider="openai", model="gpt-4")

@pytest.fixture
def tool_registry():
    """Create a tool registry for testing"""
    return ToolRegistry()

@pytest.fixture
def agent(mock_llm_client, tool_registry):
    """Create an agent for testing"""
    return Agent(
        llm_client=mock_llm_client,
        tool_registry=tool_registry
    )

@pytest.fixture
def sample_input():
    """Sample input for testing"""
    return "Hello, how are you?"

@pytest.fixture
def sample_response():
    """Sample response for testing"""
    return "I'm doing well, thank you for asking!"
