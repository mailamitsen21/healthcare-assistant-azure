"""
Tool Connector
Handles HTTP calls to specialized agents (Agents 1, 2, 3).
"""
import os
import requests
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolConnector:
    """
    Connects to specialized agent Azure Functions.
    Each agent is called via HTTP.
    """
    
    def __init__(self):
        """Initialize with base URLs for specialized agents."""
        # Get base URL from environment (for deployed functions)
        # For local development, use localhost
        self.base_url = os.getenv(
            "SPECIALIZED_TOOLS_BASE_URL",
            "http://localhost:7071/api"
        )
        
        # Function keys for authentication (if required)
        self.function_keys = {
            "agent1_parser": os.getenv("AGENT1_FUNCTION_KEY", ""),
            "agent2_knowledge": os.getenv("AGENT2_FUNCTION_KEY", ""),
            "agent3_booking": os.getenv("AGENT3_FUNCTION_KEY", "")
        }
        
        logger.info(f"ToolConnector initialized with base URL: {self.base_url}")
    
    def call_agent(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Calls a specialized agent via HTTP.
        
        Args:
            agent_name: Name of the agent (agent1_parser, agent2_knowledge, agent3_booking)
            input_data: Input data to send to the agent
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with agent response
        """
        # Map agent names to function endpoints
        endpoint_map = {
            "agent1_parser": "symptom_interpreter_parser",
            "agent2_knowledge": "knowledge_retrieval_agent",
            "agent3_booking": "appointment_followup_agent"
        }
        
        if agent_name not in endpoint_map:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        endpoint = endpoint_map[agent_name]
        url = f"{self.base_url}/{endpoint}"
        
        # Add function key if available
        headers = {"Content-Type": "application/json"}
        if self.function_keys.get(agent_name):
            url += f"?code={self.function_keys[agent_name]}"
        
        try:
            logger.info(f"Calling {agent_name} at {url} with data: {input_data}")
            
            response = requests.post(
                url,
                json=input_data,
                headers=headers,
                timeout=timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "agent": agent_name,
                "data": result,
                "status": "success"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {agent_name}: {str(e)}", exc_info=True)
            return {
                "agent": agent_name,
                "data": {"error": f"Failed to call agent: {str(e)}"},
                "status": "error"
            }
        except Exception as e:
            logger.error(f"Unexpected error calling {agent_name}: {str(e)}", exc_info=True)
            return {
                "agent": agent_name,
                "data": {"error": f"Unexpected error: {str(e)}"},
                "status": "error"
            }

