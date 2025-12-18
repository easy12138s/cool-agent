#!/usr/bin/env python3
"""Main entry point for the Intelligent Agent Project"""

import logging
from dotenv import load_dotenv

from src.config import settings
from src.core import Agent
from src.models import LLMClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run the agent"""
    logger.info("Starting Intelligent Agent...")
    logger.info(f"Agent Name: {settings.AGENT_NAME}")
    logger.info(f"Agent Version: {settings.AGENT_VERSION}")
    
    # Initialize LLM client
    llm_client = LLMClient()
    
    # Initialize agent
    agent = Agent(llm_client=llm_client)
    
    # Example usage
    logger.info("Agent initialized successfully")
    
    # Run the agent loop
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                logger.info("Exiting agent...")
                break
            
            response = agent.run(user_input)
            print(f"Agent: {response}")
    except KeyboardInterrupt:
        logger.info("Agent interrupted by user")
    finally:
        logger.info("Agent shutdown complete")

if __name__ == "__main__":
    main()
