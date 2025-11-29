# Complete Deployment Guide

This guide walks you through deploying the Healthcare Assistant to Azure with all three components: two Function Apps and one Web App.

## 📋 Prerequisites

1. **Azure Subscription** with appropriate permissions
2. **Visual Studio Code** with Azure extensions installed
3. **Azure Functions Core Tools** v4
4. **Azure CLI** (optional, for command-line deployment)
5. **Azure Resources:**
   - Azure OpenAI service with GPT-4 deployment
   - Azure Cosmos DB account
   - Azure Storage Account (created automatically with Function Apps)

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│   Azure Web App (Frontend)             │
│   healthbot-ui-app                     │
└──────────────┬──────────────────────────┘
               │ HTTP POST
               ▼
┌─────────────────────────────────────────┐
│   Function App: HealthBotOrchestrator   │
│   Agent 3: Orchestrator API            │
│   Endpoint: /api/orchestrate            │
└──────────────┬──────────────────────────┘
               │ HTTP POST
               ▼
┌─────────────────────────────────────────┐
│   Function App: HealthBotTools          │
│   Agents 1, 2, 3: Specialized Tools    │
│   Endpoints:                            │
│   - /api/symptom_interpreter_parser     │
│   - /api/knowledge_retrieval_agent      │
│   - /api/appointment_followup_agent     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Azure Cosmos DB                       │
│   - KnowledgeVectors container          │
│   - Appointments container               │
└─────────────────────────────────────────┘
```

## 🚀 Step-by-Step Deployment

### Step 1: Create Azure Resources

#### 1.1 Create Resource Group

```bash
az group create --name healthcare-assistant-rg --location eastus
```

#### 1.2 Create Function App: HealthBotOrchestrator

**Via Azure Portal:**
1. Go to Azure Portal > Create a resource > Function App
2. Settings:
   - **Name:** `HealthBotOrchestrator` (must be globally unique)
   - **Runtime stack:** Python
   - **Version:** 3.11
   - **Region:** East US (or your preferred region)
   - **Plan:** Consumption (Serverless)
3. Click **Review + Create** > **Create**

**Via Azure CLI:**
```bash
az functionapp create \
  --resource-group healthcare-assistant-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name HealthBotOrchestrator \
  --storage-account <storage-account-name>
```

#### 1.3 Create Function App: HealthBotTools

Repeat the same process for the specialized tools:

**Via Azure Portal:**
1. Create another Function App
2. **Name:** `HealthBotTools`
3. Same settings as above

**Via Azure CLI:**
```bash
az functionapp create \
  --resource-group healthcare-assistant-rg \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name HealthBotTools \
  --storage-account <storage-account-name>
```

#### 1.4 Create Web App: healthbot-ui-app

**Via Azure Portal:**
1. Go to Azure Portal > Create a resource > Web App
2. Settings:
   - **Name:** `healthbot-ui-app` (must be globally unique)
   - **Runtime stack:** Node.js 18 LTS (or Static Web App)
   - **Region:** Same as Function Apps
   - **Plan:** Free (F1) or Basic
3. Click **Review + Create** > **Create**

**Via Azure CLI:**
```bash
az webapp create \
  --resource-group healthcare-assistant-rg \
  --plan <app-service-plan-name> \
  --name healthbot-ui-app \
  --runtime "NODE:18-lts"
```

### Step 2: Configure Environment Variables

#### 2.1 Configure HealthBotOrchestrator Function App

**Via Azure Portal:**
1. Navigate to `HealthBotOrchestrator` Function App
2. Go to **Configuration** > **Application settings**
3. Click **+ New application setting** and add:

| Setting Name | Value | Description |
|-------------|-------|-------------|
| `AZURE_OPENAI_ENDPOINT` | `https://your-resource.openai.azure.com/` | Your Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | `your-api-key` | Your Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | `gpt-4` | Your GPT-4 deployment name |
| `AZURE_OPENAI_API_VERSION` | `2024-02-15-preview` | API version |
| `SPECIALIZED_TOOLS_BASE_URL` | `https://healthbottools.azurewebsites.net/api` | Base URL for specialized tools |

4. Click **Save**

**Via Azure CLI:**
```bash
az functionapp config appsettings set \
  --name HealthBotOrchestrator \
  --resource-group healthcare-assistant-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-api-key" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4" \
    AZURE_OPENAI_API_VERSION="2024-02-15-preview" \
    SPECIALIZED_TOOLS_BASE_URL="https://healthbottools.azurewebsites.net/api"
```

#### 2.2 Configure HealthBotTools Function App

**Via Azure Portal:**
1. Navigate to `HealthBotTools` Function App
2. Go to **Configuration** > **Application settings**
3. Add the following settings:

| Setting Name | Value | Description |
|-------------|-------|-------------|
| `AZURE_OPENAI_ENDPOINT` | `https://your-resource.openai.azure.com/` | Your Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | `your-api-key` | Your Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | `gpt-4` | Your GPT-4 deployment name |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` | `text-embedding-ada-002` | Embedding model deployment |
| `AZURE_OPENAI_API_VERSION` | `2024-02-15-preview` | API version |
| `COSMOS_DB_ENDPOINT` | `https://your-cosmos-account.documents.azure.com:443/` | Cosmos DB endpoint |
| `COSMOS_DB_KEY` | `your-cosmos-key` | Cosmos DB primary key |
| `AZURE_COSMOSDB_DATABASE_NAME` | `HealthcareDB` | Database name |
| `AZURE_COSMOSDB_KNOWLEDGE_CONTAINER` | `KnowledgeVectors` | Knowledge container name |
| `AZURE_COSMOSDB_APPOINTMENTS_CONTAINER` | `Appointments` | Appointments container name |

**Via Azure CLI:**
```bash
az functionapp config appsettings set \
  --name HealthBotTools \
  --resource-group healthcare-assistant-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
    AZURE_OPENAI_API_KEY="your-api-key" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="text-embedding-ada-002" \
    AZURE_OPENAI_API_VERSION="2024-02-15-preview" \
    COSMOS_DB_ENDPOINT="https://your-cosmos-account.documents.azure.com:443/" \
    COSMOS_DB_KEY="your-cosmos-key" \
    AZURE_COSMOSDB_DATABASE_NAME="HealthcareDB" \
    AZURE_COSMOSDB_KNOWLEDGE_CONTAINER="KnowledgeVectors" \
    AZURE_COSMOSDB_APPOINTMENTS_CONTAINER="Appointments"
```

### Step 3: Configure CORS

**Critical:** You must configure CORS to allow your frontend to call the orchestrator.

#### 3.1 Configure CORS for HealthBotOrchestrator

**Via Azure Portal:**
1. Navigate to `HealthBotOrchestrator` Function App
2. Go to **CORS** (under API)
3. Add your frontend URL:
   - `https://healthbot-ui-app.azurewebsites.net`
   - For local testing: `http://localhost:8000`
4. Click **Save**

**Via Azure CLI:**
```bash
az functionapp cors add \
  --name HealthBotOrchestrator \
  --resource-group healthcare-assistant-rg \
  --allowed-origins "https://healthbot-ui-app.azurewebsites.net"
```

### Step 4: Deploy Function Apps

#### 4.1 Deploy via VS Code (Recommended)

1. **Install Extensions:**
   - Azure Account
   - Azure Functions
   - Python

2. **Sign In:**
   - Click Azure icon in VS Code sidebar
   - Sign in to your Azure account

3. **Deploy Orchestrator:**
   - Open `src/orchestrator-api` folder in VS Code
   - Press `F1` or `Cmd+Shift+P`
   - Type: `Azure Functions: Deploy to Function App`
   - Select `HealthBotOrchestrator`
   - Wait for deployment to complete

4. **Deploy Specialized Tools:**
   - Open `src/specialized-tools` folder in VS Code
   - Repeat the deployment process
   - Select `HealthBotTools`

#### 4.2 Deploy via Azure CLI

**Deploy Orchestrator:**
```bash
cd src/orchestrator-api
func azure functionapp publish HealthBotOrchestrator --python
```

**Deploy Specialized Tools:**
```bash
cd src/specialized-tools
func azure functionapp publish HealthBotTools --python
```

### Step 5: Get Function Endpoints and Keys

#### 5.1 Get Orchestrator Endpoint

**Via Azure Portal:**
1. Navigate to `HealthBotOrchestrator` Function App
2. Go to **Functions** > `orchestrate`
3. Click **Get function URL**
4. Copy the URL (format: `https://healthbotorchestrator.azurewebsites.net/api/orchestrate?code=...`)

**Via Azure CLI:**
```bash
az functionapp function show \
  --name HealthBotOrchestrator \
  --resource-group healthcare-assistant-rg \
  --function-name orchestrate \
  --query invokeUrlTemplate
```

#### 5.2 Get Function Keys (Optional)

If you want to use function keys for authentication:

```bash
# Get orchestrator function key
az functionapp function keys list \
  --name HealthBotOrchestrator \
  --resource-group healthcare-assistant-rg \
  --function-name orchestrate

# Get specialized tools function keys
az functionapp function keys list \
  --name HealthBotTools \
  --resource-group healthcare-assistant-rg \
  --function-name symptom_interpreter_parser
```

### Step 6: Deploy Frontend

#### 6.1 Update Frontend Configuration

Edit `src/ui-frontend/config.js`:

```javascript
return {
    ORCHESTRATOR_URL: 'https://healthbotorchestrator.azurewebsites.net/api/orchestrate',
    FUNCTION_KEY: 'your-function-key-here', // Optional
    TIMEOUT: 30000
};
```

#### 6.2 Deploy via Local Git (Recommended)

1. **Enable Local Git in Azure Portal:**
   - Navigate to `healthbot-ui-app` Web App
   - Go to **Deployment Center**
   - Select **Local Git** as source
   - Copy the Git URL

2. **Deploy from Local Machine:**
```bash
cd src/ui-frontend

# Initialize git if not already done
git init
git add .
git commit -m "Initial deployment"

# Add Azure remote
git remote add azure <Your_Azure_Git_URL>

# Push to Azure
git push azure master
```

#### 6.3 Deploy via VS Code

1. Install **Azure Static Web Apps** extension
2. Right-click `src/ui-frontend` folder
3. Select **Deploy to Static Web App**
4. Follow the prompts

#### 6.4 Deploy via Azure CLI (ZIP Deploy)

```bash
cd src/ui-frontend
zip -r ../webapp.zip .

az webapp deployment source config-zip \
  --resource-group healthcare-assistant-rg \
  --name healthbot-ui-app \
  --src ../webapp.zip
```

### Step 7: Test the Deployment

#### 7.1 Test Orchestrator Endpoint

```bash
curl -X POST "https://healthbotorchestrator.azurewebsites.net/api/orchestrate?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "I have a headache"}'
```

#### 7.2 Test Specialized Tools

```bash
# Test Agent 1
curl -X POST "https://healthbottools.azurewebsites.net/api/symptom_interpreter_parser?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "I have been experiencing headaches for 2 days"}'

# Test Agent 2
curl -X POST "https://healthbottools.azurewebsites.net/api/knowledge_retrieval_agent?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What causes headaches?", "top_k": 3}'
```

#### 7.3 Test Frontend

1. Open `https://healthbot-ui-app.azurewebsites.net` in your browser
2. Try a query like: "I have a fever, and I need a doctor"
3. Verify the entire flow works end-to-end

## 📍 Endpoint Reference

### Orchestrator API (HealthBotOrchestrator)

- **Base URL:** `https://healthbotorchestrator.azurewebsites.net`
- **Endpoint:** `/api/orchestrate`
- **Method:** POST
- **Auth:** Function key (optional, can use FUNCTION auth level)
- **Request Body:**
  ```json
  {
    "query": "User query text",
    "history": [
      {"role": "user", "content": "previous message"},
      {"role": "assistant", "content": "previous response"}
    ]
  }
  ```
- **Response:**
  ```json
  {
    "response": "Synthesized response text",
    "agent_calls": ["agent1_parser", "agent2_knowledge"]
  }
  ```

### Specialized Tools (HealthBotTools)

#### Agent 1: Symptom Parser
- **Endpoint:** `/api/symptom_interpreter_parser`
- **Method:** POST
- **Request Body:**
  ```json
  {
    "text": "I have been experiencing headaches and fever"
  }
  ```
- **Response:**
  ```json
  {
    "primary_intent": "symptom_report",
    "symptoms": ["headache", "fever"],
    "severity": "moderate",
    "duration": "2 days"
  }
  ```

#### Agent 2: Knowledge Retrieval
- **Endpoint:** `/api/knowledge_retrieval_agent`
- **Method:** POST
- **Request Body:**
  ```json
  {
    "query": "What causes headaches?",
    "top_k": 3
  }
  ```
- **Response:**
  ```json
  {
    "results": [
      {
        "id": "kb_1",
        "title": "Headache Management",
        "content": "...",
        "category": "symptoms",
        "similarity_score": 0.95
      }
    ]
  }
  ```

#### Agent 3: Appointment Booking
- **Endpoint:** `/api/appointment_followup_agent`
- **Method:** POST
- **Request Body:**
  ```json
  {
    "query": "Book an appointment",
    "date": "2024-01-15",
    "time": "14:00",
    "user_id": "user123",
    "doctor": "Dr. Smith"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "appointment_id": "appt_20240115120000",
    "message": "Appointment scheduled for 2024-01-15 at 14:00"
  }
  ```

## 🔧 Troubleshooting

### Function App Not Starting

1. Check **Application Insights** for errors
2. Verify all environment variables are set
3. Check function logs: `az functionapp log tail --name HealthBotOrchestrator --resource-group healthcare-assistant-rg`

### CORS Errors

1. Verify CORS is configured in Function App settings
2. Check that frontend URL is in allowed origins
3. Ensure no trailing slashes in URLs

### Connection Errors

1. Verify all connection strings and keys are correct
2. Check Cosmos DB firewall rules
3. Verify Azure OpenAI endpoint and key

### Import Errors

1. Ensure `requirements.txt` is deployed correctly
2. Check Python version matches (3.11)
3. Review deployment logs for package installation errors

## 🔐 Security Best Practices

1. **Use Managed Identity** instead of keys where possible
2. **Enable HTTPS only** for all Function Apps
3. **Use Key Vault** for sensitive configuration
4. **Enable Application Insights** for monitoring
5. **Set up rate limiting** for production
6. **Regularly rotate** API keys and function keys

## 📊 Monitoring

1. **Application Insights:** Automatically enabled for Function Apps
2. **Metrics:** Monitor function execution count, duration, errors
3. **Logs:** View real-time logs in Azure Portal
4. **Alerts:** Set up alerts for errors and performance issues

## 🚀 Next Steps

1. Set up **CI/CD pipelines** for automated deployments
2. Configure **custom domains** for production
3. Set up **authentication/authorization**
4. Add **rate limiting** and **throttling**
5. Implement **caching** for frequently accessed data
6. Set up **backup and disaster recovery**

