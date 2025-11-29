"""
Semantic Kernel Planner
Initializes the SK kernel, defines system prompts, and plans agent execution.
"""
import os
import json
import logging
from typing import List, Dict, Any
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureOpenAIChatCompletion
from semantic_kernel.core_plugins.text_plugin import TextPlugin
from semantic_kernel.prompt_template import PromptTemplateConfig
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlanStep(BaseModel):
    """Represents a single step in the execution plan."""
    agent_name: str
    input_data: Dict[str, Any]
    reasoning: str


class ExecutionPlan(BaseModel):
    """Represents the complete execution plan."""
    steps: List[PlanStep]
    reasoning: str


class HealthcarePlanner:
    """
    Healthcare-specific planner using Semantic Kernel.
    Coordinates the execution of specialized agents.
    """
    
    def __init__(self):
        """Initialize the Semantic Kernel with Azure OpenAI."""
        self.kernel = Kernel()
        
        # Get Azure OpenAI configuration from environment
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not endpoint or not api_key:
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set"
            )
        
        # Add Azure OpenAI service
        self.kernel.add_service(
            AzureOpenAIChatCompletion(
                service_id="azure_openai",
                deployment_name=deployment_name,
                endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
        )
        
        # Add text plugin for basic text operations
        self.kernel.add_plugin(TextPlugin(), "text_plugin")
        
        logger.info("HealthcarePlanner initialized successfully")
    
    def _get_system_prompt(self) -> str:
        """Returns the system prompt for the healthcare assistant."""
        return """You are a healthcare assistant orchestrator. Your role is to:
1. Analyze user queries to understand their intent
2. Determine which specialized agents need to be called
3. Plan the sequence of agent calls
4. Synthesize responses from multiple agents

Available Agents:
- agent1_parser: Parses symptoms and extracts structured information (primary_intent, symptoms list)
- agent2_knowledge: Retrieves relevant medical knowledge using vector search
- agent3_booking: Handles appointment booking and availability checks

Your responses should be in JSON format:
{
    "reasoning": "Why you chose these agents",
    "steps": [
        {
            "agent_name": "agent1_parser",
            "input_data": {"text": "user query"},
            "reasoning": "Need to parse symptoms"
        }
    ]
}"""
    
    def create_plan(self, user_query: str, conversation_history: List[Dict] = None) -> ExecutionPlan:
        """
        Creates an execution plan based on the user query.
        
        Args:
            user_query: The user's input query
            conversation_history: Previous conversation messages
            
        Returns:
            ExecutionPlan with ordered steps
        """
        conversation_history = conversation_history or []
        
        # Build context from conversation history
        history_context = ""
        if conversation_history:
            history_context = "\n".join([
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
        
        # Create planning prompt
        planning_prompt = f"""{self._get_system_prompt()}

Conversation History:
{history_context}

User Query: {user_query}

Analyze the query and create an execution plan. Respond with valid JSON only."""

        try:
            # Use Semantic Kernel to generate the plan
            planning_function = self.kernel.create_function_from_prompt(
                function_name="plan_agents",
                plugin_name="orchestrator",
                prompt=planning_prompt,
                description="Plans the execution of specialized agents"
            )
            
            result = self.kernel.invoke(planning_function, user_query=user_query)
            plan_json = str(result)
            
            # Parse the JSON response
            plan_data = json.loads(plan_json)
            
            # Convert to ExecutionPlan
            steps = [
                PlanStep(**step) for step in plan_data.get("steps", [])
            ]
            
            return ExecutionPlan(
                steps=steps,
                reasoning=plan_data.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}", exc_info=True)
            # Fallback: simple plan based on keywords
            return self._create_fallback_plan(user_query)
    
    def _create_fallback_plan(self, user_query: str) -> ExecutionPlan:
        """Creates a simple fallback plan when SK planning fails."""
        query_lower = user_query.lower()
        
        steps = []
        
        # Always start with parser if symptoms are mentioned
        if any(word in query_lower for word in ["symptom", "pain", "ache", "feel", "hurt"]):
            steps.append(PlanStep(
                agent_name="agent1_parser",
                input_data={"text": user_query},
                reasoning="User mentioned symptoms, need to parse them"
            ))
        
        # Add knowledge retrieval if medical questions
        if any(word in query_lower for word in ["what", "how", "why", "explain", "information"]):
            steps.append(PlanStep(
                agent_name="agent2_knowledge",
                input_data={"query": user_query},
                reasoning="User asking for medical information"
            ))
        
        # Add booking if appointment-related
        if any(word in query_lower for word in ["appointment", "book", "schedule", "available"]):
            steps.append(PlanStep(
                agent_name="agent3_booking",
                input_data={"query": user_query},
                reasoning="User wants to book or check appointments"
            ))
        
        # Default: at least parse the query
        if not steps:
            steps.append(PlanStep(
                agent_name="agent1_parser",
                input_data={"text": user_query},
                reasoning="Default: parse user input"
            ))
        
        return ExecutionPlan(
            steps=steps,
            reasoning="Fallback plan based on keyword matching"
        )
    
    def synthesize_response(
        self,
        user_query: str,
        agent_results: List[Dict[str, Any]],
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Synthesizes a final response from multiple agent results.
        
        Args:
            user_query: Original user query
            agent_results: Results from all called agents
            conversation_history: Previous conversation messages
            
        Returns:
            Final synthesized response string
        """
        conversation_history = conversation_history or []
        
        # Build context from agent results
        agent_context = "\n\n".join([
            f"Agent {result.get('agent', 'unknown')}:\n{json.dumps(result.get('data', {}), indent=2)}"
            for result in agent_results
        ])
        
        synthesis_prompt = f"""You are a healthcare assistant. Synthesize a helpful, empathetic response based on the following information.

User Query: {user_query}

Agent Results:
{agent_context}

Provide a clear, professional, and empathetic response. Do not make medical diagnoses, but provide helpful information and guidance."""

        try:
            synthesis_function = self.kernel.create_function_from_prompt(
                function_name="synthesize_response",
                plugin_name="orchestrator",
                prompt=synthesis_prompt,
                description="Synthesizes final response from agent results"
            )
            
            result = self.kernel.invoke(synthesis_function)
            return str(result)
            
        except Exception as e:
            logger.error(f"Error synthesizing response: {str(e)}", exc_info=True)
            # Fallback: simple concatenation
            return "\n\n".join([
                f"From {r.get('agent', 'agent')}: {json.dumps(r.get('data', {}), indent=2)}"
                for r in agent_results
            ])

