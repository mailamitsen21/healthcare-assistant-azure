"""
Specialized Tools - Azure Functions
Contains HTTP triggers for Agents 1, 2, and 3.
"""
import azure.functions as func
import logging
import json
import sys
import os

# Add shared-db to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared-db'))

from agent1_parser.parser import SymptomParser
from agent2_knowledge.retriever import KnowledgeRetriever
from agent3_booking.booking import AppointmentBooking

app = func.FunctionApp()

@app.route(route="symptom_interpreter_parser", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def symptom_interpreter_parser(req: func.HttpRequest) -> func.HttpResponse:
    """
    Agent 1: Symptom Interpreter and Parser
    Parses raw text into structured JSON (primary_intent, symptoms).
    """
    logging.info('Agent 1: Symptom interpreter parser processed a request.')
    
    try:
        req_body = req.get_json()
        if not req_body or 'text' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'text' in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        text = req_body['text']
        parser = SymptomParser()
        result = parser.parse(text)
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in Agent 1: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="knowledge_retrieval_agent", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def knowledge_retrieval_agent(req: func.HttpRequest) -> func.HttpResponse:
    """
    Agent 2: Knowledge Retrieval Agent
    Executes vector search on KnowledgeVectors container.
    """
    logging.info('Agent 2: Knowledge retrieval agent processed a request.')
    
    try:
        req_body = req.get_json()
        if not req_body or 'query' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'query' in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        query = req_body['query']
        top_k = req_body.get('top_k', 3)
        
        retriever = KnowledgeRetriever()
        results = retriever.search(query, top_k=top_k)
        
        return func.HttpResponse(
            json.dumps({"results": results}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in Agent 2: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )


@app.route(route="appointment_followup_agent", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def appointment_followup_agent(req: func.HttpRequest) -> func.HttpResponse:
    """
    Agent 3: Appointment Booking and Follow-up Agent
    Executes SQL queries for booking and checking availability.
    """
    logging.info('Agent 3: Appointment followup agent processed a request.')
    
    try:
        req_body = req.get_json()
        if not req_body or 'query' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'query' in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        query = req_body['query']
        booking = AppointmentBooking()
        result = booking.process_query(query, req_body)
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in Agent 3: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

