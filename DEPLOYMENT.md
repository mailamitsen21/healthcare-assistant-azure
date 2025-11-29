# Deployment Guide

This guide explains how to deploy the Healthcare Assistant multi-agent system to Azure.

## Prerequisites

1. **Azure Subscription** with appropriate permissions
2. **Azure CLI** installed and configured
3. **Azure Functions Core Tools** (for local development)
4. **Azure OpenAI Service** provisioned with:
   - GPT-4 deployment (or GPT-3.5-turbo)
   - Text embedding model (text-embedding-ada-002)
5. **Bicep CLI** (for infrastructure deployment)

## Step 1: Prepare Azure Resources

### 1.1 Create Resource Group

```bash
az group create --name healthcare-assistant-rg --location eastus
```

### 1.2 Deploy Infrastructure with Bicep

```bash
cd deployment

# Update params.json with your Azure OpenAI details
# Then deploy:
az deployment group create \
  --resource-group healthcare-assistant-rg \
  --template-file main.bicep \
  --parameters @params.json
```

This will create:
- Cosmos DB account and containers
- Storage account
- Function Apps (orchestrator and specialized tools)
- Web App for frontend
- App Service Plans

## Step 2: Configure Environment Variables

### 2.1 Specialized Tools Function App

After deployment, set the function app settings:

```bash
# Get the function app name from deployment output
FUNCTION_APP_NAME="healthcare-assistant-functions-dev"

# Set Cosmos DB connection
az functionapp config appsettings set \
  --name $FUNCTION_APP_NAME \
  --resource-group healthcare-assistant-rg \
  --settings \
    AZURE_COSMOSDB_ENDPOINT="<your-cosmos-endpoint>" \
    AZURE_COSMOSDB_KEY="<your-cosmos-key>"
```

### 2.2 Orchestrator Function App

```bash
ORCHESTRATOR_APP_NAME="healthcare-assistant-orchestrator-dev"

az functionapp config appsettings set \
  --name $ORCHESTRATOR_APP_NAME \
  --resource-group healthcare-assistant-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="<your-openai-endpoint>" \
    AZURE_OPENAI_API_KEY="<your-openai-key>" \
    SPECIALIZED_TOOLS_BASE_URL="https://$FUNCTION_APP_NAME.azurewebsites.net/api"
```

## Step 3: Deploy Function Apps

### 3.1 Deploy Specialized Tools

```bash
cd src/specialized-tools

# Install dependencies locally (for testing)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Deploy to Azure
func azure functionapp publish $FUNCTION_APP_NAME --python
```

### 3.2 Deploy Orchestrator

```bash
cd ../orchestrator-api

# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Deploy to Azure
func azure functionapp publish $ORCHESTRATOR_APP_NAME --python
```

## Step 4: Deploy Frontend

### 4.1 Using Azure Static Web Apps (Recommended)

```bash
cd src/ui-frontend

# Update app.js with your orchestrator URL
# Then deploy:
az staticwebapp create \
  --name healthcare-assistant-web \
  --resource-group healthcare-assistant-rg \
  --source . \
  --location "East US 2" \
  --branch main
```

### 4.2 Using Azure Web App

Alternatively, you can deploy to a traditional Web App:

```bash
WEB_APP_NAME="healthcare-assistant-web-dev"

cd src/ui-frontend
zip -r ../webapp.zip .

az webapp deployment source config-zip \
  --resource-group healthcare-assistant-rg \
  --name $WEB_APP_NAME \
  --src ../webapp.zip
```

## Step 5: Initialize Cosmos DB

### 5.1 Create Sample Knowledge Base Data

You'll need to populate the `KnowledgeVectors` container with medical knowledge documents. Each document should have:
- `id`: Unique identifier
- `title`: Document title
- `content`: Medical knowledge content
- `category`: Category (e.g., "symptoms", "treatments", "prevention")
- `embedding`: Vector embedding of the content (generated using EmbeddingService)

### 5.2 Create Sample Script

Create a script to populate knowledge base:

```python
# scripts/populate_knowledge_base.py
from shared_db.cosmos_client import CosmosClient
from shared_db.embedding_service import EmbeddingService
import os

cosmos_client = CosmosClient()
embedding_service = EmbeddingService()

container = cosmos_client.get_container(
    database_name=cosmos_client.database_name,
    container_name="KnowledgeVectors"
)

# Sample knowledge items
knowledge_items = [
    {
        "title": "Headache Management",
        "content": "Headaches can be caused by various factors...",
        "category": "symptoms"
    },
    # Add more items
]

for item in knowledge_items:
    embedding = embedding_service.get_embedding(item["content"])
    item["embedding"] = embedding
    item["id"] = f"kb_{item['title'].lower().replace(' ', '_')}"
    container.create_item(body=item)
```

## Step 6: Test the Deployment

### 6.1 Test Orchestrator Endpoint

```bash
ORCHESTRATOR_URL="https://$ORCHESTRATOR_APP_NAME.azurewebsites.net/api/orchestrate"

curl -X POST $ORCHESTRATOR_URL \
  -H "Content-Type: application/json" \
  -d '{"query": "I have a headache"}'
```

### 6.2 Test Specialized Tools

```bash
SPECIALIZED_URL="https://$FUNCTION_APP_NAME.azurewebsites.net/api"

# Test Agent 1
curl -X POST "$SPECIALIZED_URL/symptom_interpreter_parser" \
  -H "Content-Type: application/json" \
  -d '{"text": "I have been experiencing headaches for 2 days"}'
```

### 6.3 Access Frontend

Navigate to your web app URL and test the chat interface.

## Troubleshooting

### Function App Not Starting

- Check Application Insights for errors
- Verify all environment variables are set correctly
- Check function app logs: `func logs`

### Cosmos DB Connection Issues

- Verify connection strings in app settings
- Check firewall rules if using private endpoints
- Ensure containers are created

### Vector Search Not Working

- Verify vector index is created on the `embedding` field
- Check that embeddings are generated correctly
- Ensure Cosmos DB account supports vector search

## Next Steps

1. Set up CI/CD pipelines for automated deployments
2. Configure Application Insights for monitoring
3. Set up authentication/authorization
4. Add rate limiting and security measures
5. Scale resources based on usage

