"""
Orchestrator API - Agent 3
Main entry point for the healthcare assistant system.
Uses Semantic Kernel to coordinate specialized agents.
"""
import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.route(route="orchestrate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def orchestrator_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main orchestrator endpoint that receives user queries
    and coordinates the specialized agents.
    """
    logging.info('Orchestrator function processed a request.')

    try:
        # Lazy imports to avoid blocking function registration
        from sk_core.planner import HealthcarePlanner
        from sk_core.tool_connector import ToolConnector
        
        # Parse request body
        req_body = req.get_json()
        if not req_body or 'query' not in req_body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'query' in request body"}),
                status_code=400,
                mimetype="application/json"
            )

        user_query = req_body['query']
        conversation_history = req_body.get('history', [])

        # Initialize planner and tool connector
        planner = HealthcarePlanner()
        tool_connector = ToolConnector()

        # Get the plan from Semantic Kernel
        plan = planner.create_plan(user_query, conversation_history)

        # Execute the plan by calling specialized agents
        results = []
        for step in plan.steps:
            agent_result = tool_connector.call_agent(
                agent_name=step.agent_name,
                input_data=step.input_data
            )
            results.append(agent_result)

        # Synthesize final response
        final_response = planner.synthesize_response(
            user_query=user_query,
            agent_results=results,
            conversation_history=conversation_history
        )

        return func.HttpResponse(
            json.dumps({
                "response": final_response,
                "agent_calls": [r.get("agent", "unknown") for r in results]
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error in orchestrator: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

