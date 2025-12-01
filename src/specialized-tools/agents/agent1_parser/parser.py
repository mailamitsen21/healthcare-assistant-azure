"""
Agent 1: Symptom Interpreter and Parser
Uses LLM to parse raw text into structured JSON.
"""
import os
import logging
from typing import Dict, Any
from openai import AzureOpenAI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParsedSymptoms(BaseModel):
    """Structured output from symptom parser."""
    primary_intent: str
    symptoms: list[str]
    severity: str | None = None
    duration: str | None = None
    additional_context: Dict[str, Any] | None = None


class SymptomParser:
    """
    Parses user text into structured symptom information.
    Uses Azure OpenAI to extract structured data.
    """
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        
        if not endpoint or not api_key:
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set"
            )
        
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = deployment_name
        
        logger.info("SymptomParser initialized")
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parses user text into structured symptom information.
        
        Args:
            text: Raw user input text
            
        Returns:
            Dictionary with primary_intent, symptoms list, and other fields
        """
        system_prompt = """You are a medical symptom parser. Extract structured information from user text.
Return a JSON object with:
- primary_intent: The main intent (e.g., "symptom_report", "question", "appointment_request")
- symptoms: List of symptoms mentioned (e.g., ["headache", "fever"])
- severity: Severity level if mentioned (e.g., "mild", "moderate", "severe")
- duration: Duration if mentioned (e.g., "2 days", "1 week")
- additional_context: Any other relevant information as key-value pairs

Return ONLY valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
                # Note: temperature parameter removed - model only supports default (1)
            )
            
            result_text = response.choices[0].message.content
            import json
            parsed = json.loads(result_text)
            
            # Validate and structure the response
            result = ParsedSymptoms(**parsed)
            
            logger.info(f"Parsed symptoms: {result.primary_intent}, {len(result.symptoms)} symptoms")
            
            return result.model_dump()
            
        except Exception as e:
            logger.error(f"Error parsing symptoms: {str(e)}", exc_info=True)
            # Fallback response
            return {
                "primary_intent": "unknown",
                "symptoms": [],
                "error": str(e)
            }

