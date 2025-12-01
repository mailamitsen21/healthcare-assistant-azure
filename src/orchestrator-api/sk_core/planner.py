"""
Semantic Kernel Planner
Initializes the SK kernel, defines system prompts, and plans agent execution.
"""
import os
import json
import logging
from typing import List, Dict, Any
from semantic_kernel import Kernel
from semantic_kernel.core_plugins.text_plugin import TextPlugin
from semantic_kernel.prompt_template import PromptTemplateConfig
from pydantic import BaseModel

# Try different import paths for Azure OpenAI (API changed in different SK versions)
try:
    from semantic_kernel.connectors.ai.azure_open_ai import AzureChatCompletion as AzureOpenAIChatCompletion
except ImportError:
    try:
        from semantic_kernel.connectors.ai.open_ai import AzureOpenAIChatCompletion
    except ImportError:
        try:
            from semantic_kernel.connectors.ai.azure_open_ai import AzureOpenAIChatCompletion
        except ImportError:
            # Fallback: use OpenAI directly if SK doesn't work
            AzureOpenAIChatCompletion = None

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
        self.kernel = None
        self.use_sk = False
        
        # Get Azure OpenAI configuration from environment
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI credentials not set. Using fallback planner.")
            return
        
        # Try to initialize Semantic Kernel
        try:
            if AzureOpenAIChatCompletion is None:
                raise ImportError("AzureOpenAIChatCompletion not available")
            
            self.kernel = Kernel()
            self.kernel.add_service(
                AzureOpenAIChatCompletion(
                    service_id="azure_openai",
                    deployment_name=self.deployment_name,
                    endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version
                )
            )
            self.kernel.add_plugin(TextPlugin(), "text_plugin")
            self.use_sk = True
            logger.info("HealthcarePlanner initialized with Semantic Kernel")
        except Exception as e:
            logger.warning(f"Could not initialize Semantic Kernel: {str(e)}. Using fallback planner.")
            self.use_sk = False
    
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

        # Use Semantic Kernel if available, otherwise use fallback
        if not self.use_sk or self.kernel is None:
            logger.info("Using fallback planner (Semantic Kernel not available)")
            return self._create_fallback_plan(user_query)
        
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
            logger.error(f"Error creating plan with SK: {str(e)}", exc_info=True)
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

        # Use Semantic Kernel if available, otherwise use smart fallback
        if not self.use_sk or self.kernel is None:
            # Smart fallback: format response naturally
            return self._format_response_naturally(user_query, agent_results)
        
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
            # Fallback: format response naturally
            return self._format_response_naturally(user_query, agent_results)
    
    def _format_response_naturally(
        self,
        user_query: str,
        agent_results: List[Dict[str, Any]]
    ) -> str:
        """
        Formats agent results into a natural, conversational response.
        This is used when Semantic Kernel is not available.
        """
        response_parts = []
        
        for result in agent_results:
            agent_name = result.get('agent', 'unknown')
            data = result.get('data', {})
            
            # Format based on agent type
            if agent_name == 'agent1_parser':
                response_parts.append(self._format_parser_response(data))
            elif agent_name == 'agent2_knowledge':
                response_parts.append(self._format_knowledge_response(data))
            elif agent_name == 'agent3_booking':
                response_parts.append(self._format_booking_response(data))
            else:
                # Generic formatting
                if isinstance(data, dict):
                    response_parts.append(json.dumps(data, indent=2))
                else:
                    response_parts.append(str(data))
        
        # Combine all parts into a natural response
        if len(response_parts) == 1:
            return response_parts[0]
        else:
            return "\n\n".join(response_parts)
    
    def _format_parser_response(self, data: Dict[str, Any]) -> str:
        """Formats symptom parser results into natural language."""
        if 'error' in data:
            return f"I'm sorry, I encountered an issue processing your symptoms. Please try rephrasing your question."
        
        primary_intent = data.get('primary_intent', 'unknown')
        symptoms = data.get('symptoms', [])
        severity = data.get('severity')
        duration = data.get('duration')
        additional_context = data.get('additional_context', {})
        
        response = "I understand you're experiencing "
        
        if symptoms:
            if len(symptoms) == 1:
                response += f"a {symptoms[0]}"
            elif len(symptoms) == 2:
                response += f"{symptoms[0]} and {symptoms[1]}"
            else:
                response += ", ".join(symptoms[:-1]) + f", and {symptoms[-1]}"
        else:
            response += "some health concerns"
        
        if severity:
            response += f" that you describe as {severity}"
        
        if duration:
            response += f" for {duration}"
        
        response += "."
        
        # Add helpful next steps based on intent
        if primary_intent == 'symptom_report':
            response += "\n\nI can help you with information about these symptoms. Would you like me to:"
            response += "\n• Provide general information about these symptoms"
            response += "\n• Help you find available appointment times"
            response += "\n• Answer any questions you might have"
        elif primary_intent == 'question':
            response += "\n\nI'm here to help answer your questions. Let me search for relevant information."
        elif primary_intent == 'appointment_request':
            response += "\n\nI can help you schedule an appointment. Let me check available times for you."
        
        return response
    
    def _format_knowledge_response(self, data: Dict[str, Any]) -> str:
        """Formats knowledge retrieval results into natural language."""
        if 'error' in data:
            return "I'm sorry, I couldn't retrieve the information at this time. Please try again."
        
        results = data.get('results', [])
        
        if not results:
            return "I couldn't find specific information about that. Could you provide more details about what you're looking for?"
        
        response = "Based on available medical information:\n\n"
        
        for i, item in enumerate(results[:3], 1):  # Limit to top 3
            title = item.get('title', 'Information')
            content = item.get('content', '')
            
            response += f"{i}. **{title}**\n"
            if content:
                # Truncate long content but keep it informative
                if len(content) > 300:
                    content = content[:300] + "..."
                response += f"   {content}\n\n"
        
        response += "\n*Please note: This is general information and not a substitute for professional medical advice.*"
        
        return response
    
    def _format_booking_response(self, data: Dict[str, Any]) -> str:
        """Formats appointment booking results into natural language."""
        if 'error' in data:
            error_msg = data.get('error', 'Unknown error')
            message = data.get('message', '')
            available_slots = data.get('available_slots', [])
            suggested_date = data.get('suggested_date', '')
            instructions = data.get('instructions', '')
            
            # If it's a helpful error with suggestions
            if message and available_slots:
                response = f"{message}\n\n"
                if suggested_date:
                    response += f"**Suggested date:** {suggested_date}\n\n"
                response += "**Available time slots:**\n"
                for slot in available_slots:
                    response += f"• {slot}\n"
                if instructions:
                    response += f"\n{instructions}"
                return response
            
            # Generic error
            return f"I'm sorry, I encountered an issue with the appointment: {error_msg}. Please try again or provide more details."
        
        if data.get('success'):
            appointment_id = data.get('appointment_id', '')
            message = data.get('message', 'Appointment scheduled successfully')
            return f"✅ {message}\n\nYour appointment ID is: {appointment_id}\n\nYou should receive a confirmation shortly."
        
        if 'available_slots' in data:
            slots = data.get('available_slots', [])
            date = data.get('date', '')
            doctor = data.get('doctor', 'General Practitioner')
            
            if not slots:
                return f"I'm sorry, there are no available slots for {doctor} on {date}. Would you like to check another date?"
            
            response = f"Here are the available appointment times for {doctor} on {date}:\n\n"
            for slot in slots[:10]:  # Limit to 10 slots
                response += f"• {slot}\n"
            
            response += "\nWould you like to book one of these times?"
            return response
        
        if 'appointments' in data:
            appointments = data.get('appointments', [])
            count = data.get('count', 0)
            
            if count == 0:
                return "You don't have any upcoming appointments scheduled."
            
            response = f"You have {count} appointment(s) scheduled:\n\n"
            for apt in appointments:
                date = apt.get('date', 'N/A')
                time = apt.get('time', 'N/A')
                doctor = apt.get('doctor', 'N/A')
                status = apt.get('status', 'scheduled')
                
                response += f"• {date} at {time} with {doctor} ({status})\n"
            
            return response
        
        # Generic response
        return json.dumps(data, indent=2)

