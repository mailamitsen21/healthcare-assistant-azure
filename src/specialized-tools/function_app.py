"""
Specialized Tools - Azure Functions
Contains HTTP triggers for Agents 1, 2, and 3.
"""
import azure.functions as func
import logging
import json
import sys
import os

# Add agents and shared-db to path
current_dir = os.path.dirname(os.path.abspath(__file__))
agents_dir = os.path.join(current_dir, 'agents')
shared_db_dir = os.path.join(current_dir, 'shared-db')
sys.path.insert(0, agents_dir)
sys.path.insert(0, shared_db_dir)

# Lazy imports to avoid blocking function registration
def get_parser():
    from agent1_parser.parser import SymptomParser
    return SymptomParser

def get_retriever():
    from agent2_knowledge.retriever import KnowledgeRetriever
    return KnowledgeRetriever

def get_booking():
    from agent3_booking.booking import AppointmentBooking
    return AppointmentBooking

app = func.FunctionApp()

@app.route(route="symptom_interpreter_parser", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
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
        ParserClass = get_parser()
        parser = ParserClass()
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


@app.route(route="knowledge_retrieval_agent", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
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
        
        RetrieverClass = get_retriever()
        retriever = RetrieverClass()
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


@app.route(route="appointment_followup_agent", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
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
        
        query = req_body.get('query', '')
        if not query:
            # If no query, try to extract from input_data
            query = req_body.get('text', 'appointment request')
        
        BookingClass = get_booking()
        booking = BookingClass()
        # Pass the full request body as input_data
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

