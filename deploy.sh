#!/bin/bash

# Healthcare Assistant Deployment Script
# This script deploys all components to Azure

set -e  # Exit on error

# Configuration
RESOURCE_GROUP="DefaultResourceGroup-EUS2"
LOCATION="eastus2"
STORAGE_ACCOUNT="healthcarefuncstorage"
ORCHESTRATOR_APP="HealthBotOrchestrator"
TOOLS_APP="HealthBotTools"
WEB_APP="healthbot-ui-app"

# Azure OpenAI Configuration
OPENAI_ENDPOINT="https://ai-healthcare.openai.azure.com/"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
DEPLOYMENT_NAME="gpt-5-mini"
API_VERSION="2024-02-15-preview"

echo "🚀 Starting Healthcare Assistant Deployment..."
echo ""

# Step 1: Create Resource Group
echo "📦 Step 1: Creating Resource Group..."
az group create --name $RESOURCE_GROUP --location $LOCATION || echo "Resource group already exists"
echo "✅ Resource group ready"
echo ""

# Step 2: Create Storage Account
echo "📦 Step 2: Creating Storage Account..."
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  || echo "Storage account already exists"
echo "✅ Storage account ready"
echo ""

# Step 3: Create Function Apps
echo "📦 Step 3: Creating Function Apps..."

# Orchestrator Function App
echo "Creating Orchestrator Function App..."
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name $ORCHESTRATOR_APP \
  --storage-account $STORAGE_ACCOUNT \
  || echo "Orchestrator Function App already exists"

# Tools Function App
echo "Creating Specialized Tools Function App..."
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name $TOOLS_APP \
  --storage-account $STORAGE_ACCOUNT \
  || echo "Tools Function App already exists"

echo "✅ Function Apps created"
echo ""

# Step 4: Configure Orchestrator
echo "📦 Step 4: Configuring Orchestrator Function App..."
az functionapp config appsettings set \
  --name $ORCHESTRATOR_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
    AZURE_OPENAI_API_KEY="$OPENAI_API_KEY" \
    AZURE_OPENAI_DEPLOYMENT_NAME="$DEPLOYMENT_NAME" \
    AZURE_OPENAI_API_VERSION="$API_VERSION" \
    SPECIALIZED_TOOLS_BASE_URL="https://${TOOLS_APP,,}.azurewebsites.net/api"

# Configure CORS
az functionapp cors add \
  --name $ORCHESTRATOR_APP \
  --resource-group $RESOURCE_GROUP \
  --allowed-origins "*" \
  || echo "CORS already configured"

echo "✅ Orchestrator configured"
echo ""

# Step 5: Configure Specialized Tools
echo "📦 Step 5: Configuring Specialized Tools Function App..."
az functionapp config appsettings set \
  --name $TOOLS_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
    AZURE_OPENAI_API_KEY="$OPENAI_API_KEY" \
    AZURE_OPENAI_DEPLOYMENT_NAME="$DEPLOYMENT_NAME" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="$DEPLOYMENT_NAME" \
    AZURE_OPENAI_API_VERSION="$API_VERSION" \
    COSMOS_DB_ENDPOINT="YOUR_COSMOS_ENDPOINT" \
    COSMOS_DB_KEY="YOUR_COSMOS_KEY" \
    AZURE_COSMOSDB_DATABASE_NAME="HealthcareDB" \
    AZURE_COSMOSDB_KNOWLEDGE_CONTAINER="KnowledgeVectors" \
    AZURE_COSMOSDB_APPOINTMENTS_CONTAINER="Appointments"

echo "⚠️  Note: Update COSMOS_DB_ENDPOINT and COSMOS_DB_KEY manually after creating Cosmos DB"
echo "✅ Specialized Tools configured"
echo ""

# Step 6: Deploy Function Apps
echo "📦 Step 6: Deploying Function Apps..."

echo "Deploying Orchestrator..."
cd src/orchestrator-api
func azure functionapp publish $ORCHESTRATOR_APP --python
cd ../..

echo "Deploying Specialized Tools..."
cd src/specialized-tools
func azure functionapp publish $TOOLS_APP --python
cd ../..

echo "✅ Function Apps deployed"
echo ""

# Step 7: Create Web App
echo "📦 Step 7: Creating Web App..."
az appservice plan create \
  --name healthcare-web-plan \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku FREE \
  || echo "App Service Plan already exists"

az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan healthcare-web-plan \
  --name $WEB_APP \
  --runtime "NODE:18-lts" \
  || echo "Web App already exists"

# Update frontend config
cd src/ui-frontend
sed -i.bak "s|ORCHESTRATOR_URL.*|ORCHESTRATOR_URL: 'https://${ORCHESTRATOR_APP,,}.azurewebsites.net/api/orchestrate',|" config.js || \
sed -i '' "s|ORCHESTRATOR_URL.*|ORCHESTRATOR_URL: 'https://${ORCHESTRATOR_APP,,}.azurewebsites.net/api/orchestrate',|" config.js

# Deploy frontend
zip -r ../webapp.zip . -x "*.bak"
az webapp deployment source config-zip \
  --resource-group $RESOURCE_GROUP \
  --name $WEB_APP \
  --src ../webapp.zip
rm ../webapp.zip
cd ../..

echo "✅ Web App deployed"
echo ""

# Step 8: Display URLs
echo "🎉 Deployment Complete!"
echo ""
echo "📋 Your Endpoints:"
echo "  Orchestrator: https://${ORCHESTRATOR_APP,,}.azurewebsites.net/api/orchestrate"
echo "  Specialized Tools: https://${TOOLS_APP,,}.azurewebsites.net/api"
echo "  Frontend: https://${WEB_APP}.azurewebsites.net"
echo ""
echo "⚠️  Next Steps:"
echo "  1. Create Cosmos DB account and update COSMOS_DB_ENDPOINT and COSMOS_DB_KEY"
echo "  2. Test the endpoints using the URLs above"
echo "  3. Update CORS settings if needed for your frontend domain"
echo ""

