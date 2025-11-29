# Quick Deployment Guide - Your Configuration

This guide uses YOUR specific Azure AI Foundry configuration.

## 📋 Your Configuration Values

- **API Key:** `YOUR_OPENAI_API_KEY`
- **Project Endpoint (Foundry):** `https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI`
- **Azure OpenAI Endpoint:** `https://ai-healthcare.openai.azure.com/`
- **Deployment Name:** `gpt-5-mini`
- **Subscription ID:** `4188ef75-9e34-4fa8-b24f-1ef2d53a09df`
- **Resource Group:** `DefaultResourceGroup-EUS2`
- **Location:** `eastus2`

## ⚠️ Important Note

You have **Assistant IDs** (asst_*), but our code uses **direct model deployments**. The deployment name `gpt-5-mini` should work for direct API calls. If you need embeddings, you may need a separate embedding deployment.

## 🚀 Step 1: Create Azure Resources

### 1.1 Create Resource Group (if not exists)

```bash
az group create \
  --name DefaultResourceGroup-EUS2 \
  --location eastus2
```

### 1.2 Create Function Apps

```bash
# Create Storage Account for Functions
az storage account create \
  --name healthcarefuncstorage \
  --resource-group DefaultResourceGroup-EUS2 \
  --location eastus2 \
  --sku Standard_LRS

# Create Orchestrator Function App
az functionapp create \
  --resource-group DefaultResourceGroup-EUS2 \
  --consumption-plan-location eastus2 \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name HealthBotOrchestrator \
  --storage-account healthcarefuncstorage

# Create Specialized Tools Function App
az functionapp create \
  --resource-group DefaultResourceGroup-EUS2 \
  --consumption-plan-location eastus2 \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name HealthBotTools \
  --storage-account healthcarefuncstorage
```

### 1.3 Create Web App for Frontend

```bash
# Create App Service Plan
az appservice plan create \
  --name healthcare-web-plan \
  --resource-group DefaultResourceGroup-EUS2 \
  --location eastus2 \
  --sku FREE

# Create Web App
az webapp create \
  --resource-group DefaultResourceGroup-EUS2 \
  --plan healthcare-web-plan \
  --name healthbot-ui-app \
  --runtime "NODE:18-lts"
```

## 🔧 Step 2: Configure Environment Variables

### 2.1 Configure HealthBotOrchestrator

```bash
az functionapp config appsettings set \
  --name HealthBotOrchestrator \
  --resource-group DefaultResourceGroup-EUS2 \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://ai-healthcare.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="YOUR_OPENAI_API_KEY" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-5-mini" \
    AZURE_OPENAI_API_VERSION="2024-02-15-preview" \
    SPECIALIZED_TOOLS_BASE_URL="https://healthbottools.azurewebsites.net/api"
```

### 2.2 Configure HealthBotTools

```bash
az functionapp config appsettings set \
  --name HealthBotTools \
  --resource-group DefaultResourceGroup-EUS2 \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://ai-healthcare.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="YOUR_OPENAI_API_KEY" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-5-mini" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="gpt-5-mini" \
    AZURE_OPENAI_API_VERSION="2024-02-15-preview" \
    COSMOS_DB_ENDPOINT="YOUR_COSMOS_ENDPOINT" \
    COSMOS_DB_KEY="YOUR_COSMOS_KEY" \
    AZURE_COSMOSDB_DATABASE_NAME="HealthcareDB" \
    AZURE_COSMOSDB_KNOWLEDGE_CONTAINER="KnowledgeVectors" \
    AZURE_COSMOSDB_APPOINTMENTS_CONTAINER="Appointments"
```

**Note:** You'll need to create a Cosmos DB account and get the endpoint/key, or we can set up Cosmos DB next.

### 2.3 Configure CORS for Orchestrator

```bash
az functionapp cors add \
  --name HealthBotOrchestrator \
  --resource-group DefaultResourceGroup-EUS2 \
  --allowed-origins "https://healthbot-ui-app.azurewebsites.net" "http://localhost:8000"
```

## 📦 Step 3: Deploy Code

### 3.1 Deploy Orchestrator

```bash
cd src/orchestrator-api
func azure functionapp publish HealthBotOrchestrator --python
```

### 3.2 Deploy Specialized Tools

```bash
cd src/specialized-tools
func azure functionapp publish HealthBotTools --python
```

### 3.3 Deploy Frontend

```bash
cd src/ui-frontend

# Update config.js with orchestrator URL
# Then deploy via Git or ZIP

# Option 1: Git Deploy
git init
git add .
git commit -m "Deploy frontend"
az webapp deployment source config-local-git \
  --name healthbot-ui-app \
  --resource-group DefaultResourceGroup-EUS2
git remote add azure $(az webapp deployment source show \
  --name healthbot-ui-app \
  --resource-group DefaultResourceGroup-EUS2 \
  --query url -o tsv)
git push azure master

# Option 2: ZIP Deploy
zip -r ../webapp.zip .
az webapp deployment source config-zip \
  --resource-group DefaultResourceGroup-EUS2 \
  --name healthbot-ui-app \
  --src ../webapp.zip
```

## 🗄️ Step 4: Set Up Cosmos DB (If Needed)

```bash
# Create Cosmos DB Account
az cosmosdb create \
  --name healthcare-cosmos \
  --resource-group DefaultResourceGroup-EUS2 \
  --locations regionName=eastus2 failoverPriority=0 \
  --default-consistency-level Session

# Get connection strings
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name healthcare-cosmos \
  --resource-group DefaultResourceGroup-EUS2 \
  --query documentEndpoint -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name healthcare-cosmos \
  --resource-group DefaultResourceGroup-EUS2 \
  --query primaryMasterKey -o tsv)

# Update HealthBotTools with Cosmos DB settings
az functionapp config appsettings set \
  --name HealthBotTools \
  --resource-group DefaultResourceGroup-EUS2 \
  --settings \
    COSMOS_DB_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_DB_KEY="$COSMOS_KEY"
```

## ✅ Step 5: Test Deployment

### 5.1 Get Function URLs

```bash
# Get Orchestrator URL
ORCHESTRATOR_URL=$(az functionapp function show \
  --name HealthBotOrchestrator \
  --resource-group DefaultResourceGroup-EUS2 \
  --function-name orchestrate \
  --query invokeUrlTemplate -o tsv)

echo "Orchestrator URL: $ORCHESTRATOR_URL"
```

### 5.2 Test Orchestrator

```bash
curl -X POST "$ORCHESTRATOR_URL" \
  -H "Content-Type: application/json" \
  -d '{"query": "I have a headache"}'
```

### 5.3 Test Frontend

Open: `https://healthbot-ui-app.azurewebsites.net`

## 📝 Quick Reference

**Function Apps:**
- Orchestrator: `https://healthbotorchestrator.azurewebsites.net`
- Specialized Tools: `https://healthbottools.azurewebsites.net`

**Web App:**
- Frontend: `https://healthbot-ui-app.azurewebsites.net`

**Configuration:**
- All settings are configured via Azure CLI commands above
- Local settings files are updated separately for local development

## 🔍 Troubleshooting

1. **Check Function App Logs:**
   ```bash
   az functionapp log tail --name HealthBotOrchestrator --resource-group DefaultResourceGroup-EUS2
   ```

2. **Verify App Settings:**
   ```bash
   az functionapp config appsettings list --name HealthBotOrchestrator --resource-group DefaultResourceGroup-EUS2
   ```

3. **Test Individual Functions:**
   ```bash
   # Get function key first
   FUNC_KEY=$(az functionapp function keys list \
     --name HealthBotOrchestrator \
     --resource-group DefaultResourceGroup-EUS2 \
     --function-name orchestrate \
     --query default -o tsv)
   
   curl -X POST "https://healthbotorchestrator.azurewebsites.net/api/orchestrate?code=$FUNC_KEY" \
     -H "Content-Type: application/json" \
     -d '{"query": "test"}'
   ```

