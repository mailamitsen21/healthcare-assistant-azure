# Quick Start Guide

Get the Healthcare Assistant running locally in minutes.

## Prerequisites

- Python 3.9 or higher
- Azure Functions Core Tools v4
- Azure account with:
  - Azure OpenAI service
  - Cosmos DB account (optional for local testing)

## Local Development Setup

### 1. Clone and Navigate

```bash
cd Agentic_Healthcare
```

### 2. Set Up Orchestrator API

```bash
cd src/orchestrator-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Update local.settings.json with your Azure OpenAI credentials
# Then run:
func start
```

The orchestrator will be available at `http://localhost:7071/api/orchestrate`

### 3. Set Up Specialized Tools

Open a new terminal:

```bash
cd src/specialized-tools

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Update local.settings.json with your credentials
# Then run:
func start
```

The specialized tools will be available at:
- `http://localhost:7071/api/symptom_interpreter_parser`
- `http://localhost:7071/api/knowledge_retrieval_agent`
- `http://localhost:7071/api/appointment_followup_agent`

### 4. Set Up Frontend

Open a new terminal:

```bash
cd src/ui-frontend

# For simple testing, use Python's HTTP server:
python -m http.server 8000

# Or use any static file server
```

Update `app.js` to point to your local orchestrator:
```javascript
const CONFIG = {
    ORCHESTRATOR_URL: 'http://localhost:7071/api/orchestrate'
};
```

Open `http://localhost:8000` in your browser.

## Testing Individual Components

### Test Agent 1 (Symptom Parser)

```bash
curl -X POST http://localhost:7071/api/symptom_interpreter_parser \
  -H "Content-Type: application/json" \
  -d '{"text": "I have been experiencing headaches and fever for 3 days"}'
```

Expected response:
```json
{
  "primary_intent": "symptom_report",
  "symptoms": ["headache", "fever"],
  "duration": "3 days"
}
```

### Test Agent 2 (Knowledge Retrieval)

```bash
curl -X POST http://localhost:7071/api/knowledge_retrieval_agent \
  -H "Content-Type: application/json" \
  -d '{"query": "What causes headaches?", "top_k": 3}'
```

### Test Agent 3 (Appointment Booking)

```bash
curl -X POST http://localhost:7071/api/appointment_followup_agent \
  -H "Content-Type: application/json" \
  -d '{"query": "Check availability for tomorrow", "date": "2024-01-15"}'
```

### Test Orchestrator

```bash
curl -X POST http://localhost:7071/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "I have a headache, can you help?"}'
```

## Configuration

### Required Environment Variables

**Orchestrator API:**
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME` (default: "gpt-4")
- `SPECIALIZED_TOOLS_BASE_URL` (default: "http://localhost:7071/api")

**Specialized Tools:**
- `AZURE_COSMOSDB_ENDPOINT`
- `AZURE_COSMOSDB_KEY`
- `AZURE_COSMOSDB_DATABASE_NAME` (default: "HealthcareDB")
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` (default: "text-embedding-ada-002")

## Common Issues

### Functions Not Starting

- Ensure Azure Functions Core Tools is installed: `npm install -g azure-functions-core-tools@4`
- Check Python version: `python --version` (should be 3.9+)
- Verify all dependencies are installed

### Import Errors

- Ensure virtual environments are activated
- Check that all `requirements.txt` files have been installed
- Verify Python path includes the project directories

### Cosmos DB Connection Errors

- For local testing, you can mock Cosmos DB responses
- Or set up a local Cosmos DB emulator
- Or use a development Cosmos DB account

## Next Steps

- See [DEPLOYMENT.md](./DEPLOYMENT.md) for Azure deployment
- Review [README.md](./README.md) for architecture details
- Customize system prompts in `orchestrator-api/sk_core/planner.py`

