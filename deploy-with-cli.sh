#!/bin/bash

###############################################################################
# Healthcare Assistant - Complete Azure CLI Deployment Script
# 
# This script deploys the entire Healthcare Assistant system to Azure
# 
# Usage:
#   1. Edit the variables below (YOUR_INITIALS, LOCATION, etc.)
#   2. Run: bash deploy-with-cli.sh
#   3. Follow prompts and save output values
###############################################################################

set -e  # Exit on error

# ============================================================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================================================

RESOURCE_GROUP="HealthcareAssistant-RG"
LOCATION="eastus2"  # Change if needed
YOUR_INITIALS="jdoe"  # CHANGE THIS to your initials (must be unique)

# Resource names (will be prefixed/suffixed with YOUR_INITIALS)
COSMOS_ACCOUNT="healthcare-cosmos-${YOUR_INITIALS}"
OPENAI_ACCOUNT="healthcare-openai-${YOUR_INITIALS}"
FUNC_STORAGE="healthcarefunc${YOUR_INITIALS}"
UI_STORAGE="healthcareui${YOUR_INITIALS}"
ORCHESTRATOR_FUNC="healthcare-orchestrator-${YOUR_INITIALS}"
TOOLS_FUNC="healthcare-tools-${YOUR_INITIALS}"

# Database and container names
DATABASE_NAME="HealthcareDB"
KNOWLEDGE_CONTAINER="KnowledgeVectors"
APPOINTMENTS_CONTAINER="Appointments"

# OpenAI deployment
OPENAI_DEPLOYMENT="gpt-4o-mini"  # or gpt-35-turbo

# ============================================================================
# FUNCTIONS
# ============================================================================

print_step() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

print_info() {
    echo "ℹ️  $1"
}

print_success() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

wait_for_resource() {
    local resource_type=$1
    local resource_name=$2
    local max_wait=300  # 5 minutes
    local elapsed=0
    
    print_info "Waiting for $resource_type to be ready..."
    while [ $elapsed -lt $max_wait ]; do
        # Check resource status (simplified - adjust based on resource type)
        sleep 10
        elapsed=$((elapsed + 10))
        echo -n "."
    done
    echo ""
}

# ============================================================================
# STEP 1: VERIFY PREREQUISITES
# ============================================================================

print_step "Step 1: Verifying Prerequisites"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    print_error "Azure CLI not found. Please install it first."
    exit 1
fi
print_success "Azure CLI found: $(az --version | head -n 1)"

# Check if logged in
if ! az account show &> /dev/null; then
    print_info "Not logged in. Please login..."
    az login
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_success "Logged in to subscription: $SUBSCRIPTION_ID"

# Check Function Core Tools
if ! command -v func &> /dev/null; then
    print_error "Azure Functions Core Tools not found."
    print_info "Install with: npm install -g azure-functions-core-tools@4"
    exit 1
fi
print_success "Azure Functions Core Tools found: $(func --version)"

# ============================================================================
# STEP 2: CREATE RESOURCE GROUP
# ============================================================================

print_step "Step 2: Creating Resource Group"

if az group show --name $RESOURCE_GROUP &> /dev/null; then
    print_info "Resource group already exists. Using existing one."
else
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION
    print_success "Resource group created: $RESOURCE_GROUP"
fi

# ============================================================================
# STEP 3: CREATE COSMOS DB
# ============================================================================

print_step "Step 3: Creating Cosmos DB Account"

if az cosmosdb show --name $COSMOS_ACCOUNT --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_info "Cosmos DB account already exists. Using existing one."
    COSMOS_ENDPOINT=$(az cosmosdb show \
        --name $COSMOS_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --query documentEndpoint -o tsv)
    COSMOS_KEY=$(az cosmosdb keys list \
        --name $COSMOS_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --type keys \
        --query primaryMasterKey -o tsv)
else
    az cosmosdb create \
        --name $COSMOS_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --locations regionName=$LOCATION failoverPriority=0 \
        --default-consistency-level Session \
        --enable-free-tier true
    
    wait_for_resource "Cosmos DB" "$COSMOS_ACCOUNT"
    
    COSMOS_ENDPOINT=$(az cosmosdb show \
        --name $COSMOS_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --query documentEndpoint -o tsv)
    COSMOS_KEY=$(az cosmosdb keys list \
        --name $COSMOS_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --type keys \
        --query primaryMasterKey -o tsv)
    
    print_success "Cosmos DB created: $COSMOS_ENDPOINT"
fi

# Create database
print_info "Creating database: $DATABASE_NAME"
az cosmosdb sql database create \
    --account-name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --name $DATABASE_NAME \
    --throughput 400 &> /dev/null || print_info "Database may already exist"

# Create containers
print_info "Creating container: $KNOWLEDGE_CONTAINER"
az cosmosdb sql container create \
    --account-name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --database-name $DATABASE_NAME \
    --name $KNOWLEDGE_CONTAINER \
    --partition-key-path "/id" \
    --throughput 400 &> /dev/null || print_info "Container may already exist"

print_info "Creating container: $APPOINTMENTS_CONTAINER"
az cosmosdb sql container create \
    --account-name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --database-name $DATABASE_NAME \
    --name $APPOINTMENTS_CONTAINER \
    --partition-key-path "/user_id" \
    --throughput 400 &> /dev/null || print_info "Container may already exist"

print_success "Cosmos DB setup complete"

# ============================================================================
# STEP 4: CREATE AZURE OPENAI
# ============================================================================

print_step "Step 4: Creating Azure OpenAI Resource"

if az cognitiveservices account show --name $OPENAI_ACCOUNT --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_info "OpenAI account already exists. Using existing one."
    OPENAI_ENDPOINT=$(az cognitiveservices account show \
        --name $OPENAI_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --query properties.endpoint -o tsv)
    OPENAI_KEY=$(az cognitiveservices account keys list \
        --name $OPENAI_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --query key1 -o tsv)
else
    az cognitiveservices account create \
        --name $OPENAI_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --kind OpenAI \
        --sku S0 \
        --location $LOCATION
    
    sleep 10
    
    OPENAI_ENDPOINT=$(az cognitiveservices account show \
        --name $OPENAI_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --query properties.endpoint -o tsv)
    OPENAI_KEY=$(az cognitiveservices account keys list \
        --name $OPENAI_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --query key1 -o tsv)
    
    print_success "OpenAI resource created: $OPENAI_ENDPOINT"
fi

# Deploy model
print_info "Deploying model: $OPENAI_DEPLOYMENT"
az cognitiveservices account deployment create \
    --name $OPENAI_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --deployment-name $OPENAI_DEPLOYMENT \
    --model-name $OPENAI_DEPLOYMENT \
    --model-version "1" \
    --model-format OpenAI \
    --sku-capacity 1 \
    --sku-name "Standard" &> /dev/null || print_info "Deployment may already exist"

sleep 30
print_success "OpenAI setup complete"

# ============================================================================
# STEP 5: CREATE STORAGE ACCOUNTS
# ============================================================================

print_step "Step 5: Creating Storage Accounts"

# Functions storage
if az storage account show --name $FUNC_STORAGE --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_info "Functions storage already exists."
else
    az storage account create \
        --name $FUNC_STORAGE \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2
    print_success "Functions storage created"
fi

FUNC_STORAGE_CONN=$(az storage account show-connection-string \
    --name $FUNC_STORAGE \
    --resource-group $RESOURCE_GROUP \
    --query connectionString -o tsv)

# Frontend storage
if az storage account show --name $UI_STORAGE --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_info "Frontend storage already exists."
else
    az storage account create \
        --name $UI_STORAGE \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2
    
    az storage blob service-properties update \
        --account-name $UI_STORAGE \
        --static-website \
        --404-document "index.html" \
        --index-document "index.html"
    
    print_success "Frontend storage created"
fi

UI_STORAGE_URL=$(az storage account show \
    --name $UI_STORAGE \
    --resource-group $RESOURCE_GROUP \
    --query "primaryEndpoints.web" -o tsv)

# ============================================================================
# STEP 6: CREATE FUNCTION APPS
# ============================================================================

print_step "Step 6: Creating Function Apps"

# Orchestrator
if az functionapp show --name $ORCHESTRATOR_FUNC --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_info "Orchestrator function app already exists."
else
    az functionapp create \
        --name $ORCHESTRATOR_FUNC \
        --resource-group $RESOURCE_GROUP \
        --storage-account $FUNC_STORAGE \
        --consumption-plan-location $LOCATION \
        --runtime python \
        --runtime-version 3.11 \
        --functions-version 4 \
        --os-type Linux
    
    print_success "Orchestrator function app created"
fi

ORCHESTRATOR_URL="https://${ORCHESTRATOR_FUNC}.azurewebsites.net"

# Specialized Tools
if az functionapp show --name $TOOLS_FUNC --resource-group $RESOURCE_GROUP &> /dev/null; then
    print_info "Tools function app already exists."
else
    az functionapp create \
        --name $TOOLS_FUNC \
        --resource-group $RESOURCE_GROUP \
        --storage-account $FUNC_STORAGE \
        --consumption-plan-location $LOCATION \
        --runtime python \
        --runtime-version 3.11 \
        --functions-version 4 \
        --os-type Linux
    
    print_success "Tools function app created"
fi

TOOLS_URL="https://${TOOLS_FUNC}.azurewebsites.net"

# ============================================================================
# STEP 7: CONFIGURE FUNCTION APP SETTINGS
# ============================================================================

print_step "Step 7: Configuring Function App Settings"

# Orchestrator settings
print_info "Configuring orchestrator settings..."
az functionapp config appsettings set \
    --name $ORCHESTRATOR_FUNC \
    --resource-group $RESOURCE_GROUP \
    --settings \
        "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT" \
        "AZURE_OPENAI_API_KEY=$OPENAI_KEY" \
        "AZURE_OPENAI_DEPLOYMENT_NAME=$OPENAI_DEPLOYMENT" \
        "AZURE_OPENAI_API_VERSION=2024-02-15-preview" \
        "SPECIALIZED_TOOLS_BASE_URL=${TOOLS_URL}/api" \
        "FUNCTIONS_WORKER_RUNTIME=python" \
        "AzureWebJobsStorage=$FUNC_STORAGE_CONN" \
    --output none

# Tools settings
print_info "Configuring tools settings..."
az functionapp config appsettings set \
    --name $TOOLS_FUNC \
    --resource-group $RESOURCE_GROUP \
    --settings \
        "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT" \
        "AZURE_OPENAI_API_KEY=$OPENAI_KEY" \
        "AZURE_OPENAI_DEPLOYMENT_NAME=$OPENAI_DEPLOYMENT" \
        "AZURE_OPENAI_API_VERSION=2024-02-15-preview" \
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=$OPENAI_DEPLOYMENT" \
        "COSMOS_DB_ENDPOINT=$COSMOS_ENDPOINT" \
        "COSMOS_DB_KEY=$COSMOS_KEY" \
        "AZURE_COSMOSDB_ENDPOINT=$COSMOS_ENDPOINT" \
        "AZURE_COSMOSDB_KEY=$COSMOS_KEY" \
        "AZURE_COSMOSDB_DATABASE_NAME=$DATABASE_NAME" \
        "AZURE_COSMOSDB_KNOWLEDGE_CONTAINER=$KNOWLEDGE_CONTAINER" \
        "AZURE_COSMOSDB_APPOINTMENTS_CONTAINER=$APPOINTMENTS_CONTAINER" \
        "FUNCTIONS_WORKER_RUNTIME=python" \
        "AzureWebJobsStorage=$FUNC_STORAGE_CONN" \
    --output none

print_success "Function app settings configured"

# ============================================================================
# STEP 8: DEPLOY FUNCTION CODE
# ============================================================================

print_step "Step 8: Deploying Function Code"

# Deploy orchestrator
if [ -d "src/orchestrator-api" ]; then
    print_info "Deploying orchestrator..."
    cd src/orchestrator-api
    func azure functionapp publish $ORCHESTRATOR_FUNC --python --no-build
    cd ../..
    print_success "Orchestrator deployed"
else
    print_error "Orchestrator code not found. Skipping deployment."
fi

# Deploy specialized tools
if [ -d "src/specialized-tools" ]; then
    print_info "Deploying specialized tools..."
    cd src/specialized-tools
    func azure functionapp publish $TOOLS_FUNC --python --no-build
    cd ../..
    print_success "Specialized tools deployed"
else
    print_error "Specialized tools code not found. Skipping deployment."
fi

# ============================================================================
# STEP 9: UPLOAD FRONTEND
# ============================================================================

print_step "Step 9: Uploading Frontend Files"

if [ -d "src/ui-frontend" ]; then
    print_info "Uploading frontend files..."
    
    # Create $web container
    az storage container create \
        --name "\$web" \
        --account-name $UI_STORAGE \
        --public-access blob \
        --output none 2>/dev/null || true
    
    # Upload files
    cd src/ui-frontend
    for file in index.html app.js style.css config.js; do
        if [ -f "$file" ]; then
            az storage blob upload \
                --account-name $UI_STORAGE \
                --container-name "\$web" \
                --name "$file" \
                --file "$file" \
                --overwrite \
                --output none
            print_info "Uploaded: $file"
        fi
    done
    cd ../..
    
    print_success "Frontend files uploaded"
else
    print_error "Frontend code not found. Skipping upload."
fi

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================

print_step "Deployment Complete!"

echo ""
echo "📋 DEPLOYMENT SUMMARY"
echo "===================="
echo ""
echo "Resource Group:     $RESOURCE_GROUP"
echo "Location:          $LOCATION"
echo ""
echo "🌐 URLs:"
echo "  Orchestrator:    $ORCHESTRATOR_URL/api/orchestrate"
echo "  Tools:           $TOOLS_URL/api"
echo "  Frontend:        $UI_STORAGE_URL"
echo ""
echo "💾 Storage:"
echo "  Cosmos DB:       $COSMOS_ENDPOINT"
echo "  OpenAI:          $OPENAI_ENDPOINT"
echo ""
echo "🔑 Save these values (they're sensitive):"
echo "  Cosmos Key:      $COSMOS_KEY"
echo "  OpenAI Key:      $OPENAI_KEY"
echo ""
echo "✅ Next Steps:"
echo "  1. Test orchestrator: curl -X POST \"$ORCHESTRATOR_URL/api/orchestrate\" -H \"Content-Type: application/json\" -d '{\"query\": \"test\"}'"
echo "  2. Open frontend: $UI_STORAGE_URL"
echo "  3. Upload RAG data: cd scripts && python3 upload_rag_no_embeddings.py"
echo ""
echo "🎉 Deployment successful!"
echo ""

