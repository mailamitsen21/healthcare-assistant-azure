# Quick Deploy - Your Configuration

## 🚀 Fastest Way to Deploy

### Option 1: Automated Script (Recommended)

```bash
# Make script executable and run
chmod +x deploy.sh
./deploy.sh
```

This script will:
- ✅ Create all Azure resources
- ✅ Configure all environment variables
- ✅ Deploy all code
- ✅ Set up CORS

### Option 2: Manual Step-by-Step

Follow the detailed steps in `DEPLOY_NOW.md`

## 📋 Your Configuration (Already Set)

All configuration files have been updated with your values:

- ✅ **API Key:** Configured
- ✅ **Endpoint:** `https://ai-healthcare.openai.azure.com/`
- ✅ **Deployment:** `gpt-5-mini`
- ✅ **Local settings:** Updated in both Function Apps

## ⚠️ Before Running

1. **Azure CLI Login:**
   ```bash
   az login
   ```

2. **Azure Functions Core Tools:**
   ```bash
   npm install -g azure-functions-core-tools@4
   ```

3. **Cosmos DB (Optional for now):**
   - You can deploy without Cosmos DB initially
   - Agents 1 and 3 will work
   - Agent 2 (Knowledge Retrieval) needs Cosmos DB
   - Agent 3 (Appointment Booking) needs Cosmos DB

## 🎯 What Gets Deployed

1. **HealthBotOrchestrator** - Main orchestrator API
2. **HealthBotTools** - Specialized agents (1, 2, 3)
3. **healthbot-ui-app** - Frontend chat interface

## 🔧 After Deployment

### Update Frontend Config

The frontend config.js will be auto-updated, but verify:

```javascript
// src/ui-frontend/config.js
ORCHESTRATOR_URL: 'https://healthbotorchestrator.azurewebsites.net/api/orchestrate'
```

### Set Up Cosmos DB (If Needed)

```bash
# Create Cosmos DB
az cosmosdb create \
  --name healthcare-cosmos \
  --resource-group DefaultResourceGroup-EUS2 \
  --locations regionName=eastus2 failoverPriority=0

# Get connection info
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name healthcare-cosmos \
  --resource-group DefaultResourceGroup-EUS2 \
  --query documentEndpoint -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name healthcare-cosmos \
  --resource-group DefaultResourceGroup-EUS2 \
  --query primaryMasterKey -o tsv)

# Update Function App
az functionapp config appsettings set \
  --name HealthBotTools \
  --resource-group DefaultResourceGroup-EUS2 \
  --settings \
    COSMOS_DB_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_DB_KEY="$COSMOS_KEY"
```

## ✅ Test Your Deployment

```bash
# Get orchestrator URL
ORCHESTRATOR_URL="https://healthbotorchestrator.azurewebsites.net/api/orchestrate"

# Get function key
FUNC_KEY=$(az functionapp function keys list \
  --name HealthBotOrchestrator \
  --resource-group DefaultResourceGroup-EUS2 \
  --function-name orchestrate \
  --query default -o tsv)

# Test
curl -X POST "${ORCHESTRATOR_URL}?code=${FUNC_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"query": "I have a headache"}'
```

## 🌐 Access Your App

- **Frontend:** https://healthbot-ui-app.azurewebsites.net
- **Orchestrator API:** https://healthbotorchestrator.azurewebsites.net/api/orchestrate
- **Specialized Tools:** https://healthbottools.azurewebsites.net/api

## 🆘 Troubleshooting

1. **Check logs:**
   ```bash
   az functionapp log tail --name HealthBotOrchestrator --resource-group DefaultResourceGroup-EUS2
   ```

2. **Verify settings:**
   ```bash
   az functionapp config appsettings list --name HealthBotOrchestrator --resource-group DefaultResourceGroup-EUS2
   ```

3. **Redeploy if needed:**
   ```bash
   cd src/orchestrator-api && func azure functionapp publish HealthBotOrchestrator --python
   ```

