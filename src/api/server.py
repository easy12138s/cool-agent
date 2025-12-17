"""FastAPI server for the Intelligent Agent Project"""

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from src.config import settings
from src.core import Agent
from src.models import LLMClient

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Intelligent Agent API",
    description="API for interacting with the Intelligent Agent",
    version="0.1.0",
)

# Initialize LLM client and agent
llm_client = LLMClient()
agent = Agent(llm_client=llm_client)

# Pydantic models for request/response
example_input = "Hello, how are you?"
example_output = "I'm doing well, thank you for asking!"

class AgentRequest(BaseModel):
    """Agent request model"""
    input: str
    params: Dict[str, Any] = {}

class AgentResponse(BaseModel):
    """Agent response model"""
    output: str
    metadata: Dict[str, Any] = {}

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str

# API endpoints
@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.AGENT_VERSION
    )

@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    """Run the agent with the given input"""
    try:
        logger.info(f"API received request: {request.input}")
        response = agent.run(request.input, **request.params)
        logger.info(f"API generated response: {response}")
        return AgentResponse(
            output=response,
            metadata={
                "model": llm_client.get_model(),
                "provider": llm_client.get_provider()
            }
        )
    except Exception as e:
        logger.error(f"Error in agent run: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/info")
def get_agent_info():
    """Get agent information"""
    return agent.get_info()

@app.get("/agent/tools")
def list_agent_tools():
    """List all available tools"""
    return {
        "tools": agent.list_tools()
    }

# Run the server if this file is executed directly
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting API server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "src.api.server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG
    )
