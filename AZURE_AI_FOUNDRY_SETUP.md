# Azure AI Foundry Configuration Guide

This guide explains how to configure the Healthcare Assistant to use Azure AI Foundry (Microsoft Foundry) instead of traditional Azure OpenAI.

## 📋 Information Needed from Azure AI Foundry Portal

From the project page you're viewing, you need the following information:

### 1. **API Key** ✅ (Visible in your image)
- **Location:** "Endpoints and keys" section → "API Key" field
- **Value from your image:** `AVliAvqlKzIY0h3tjejWZs4zoRnX9OiJfcUAn30ZYgZKZS5Lbv6dJQQJ99BKACHYHv6XJ3w`
- **Usage:** Set as `AZURE_OPENAI_API_KEY` environment variable

### 2. **Project Endpoint** ✅ (Partially visible in your image)
- **Location:** "Endpoints and keys" section → "Microsoft Foundry project endpoint"
- **Value from your image:** `https://ai-healthcare.services.ai.azure.com/api/projects/healt` (appears truncated)
- **Action needed:** Click "View all endpoints" to see the complete endpoint URL
- **Usage:** This is your `AZURE_OPENAI_ENDPOINT`

### 3. **Deployment Names** ⚠️ (Need to find)
- **Location:** You need to navigate to the "Deployments" section in your Foundry project
- **Required deployments:**
  - **GPT-4 deployment** (for orchestrator and Agent 1)
    - Look for a deployment name like: `gpt-4`, `gpt-4-turbo`, `gpt-4o`, etc.
  - **Embedding model deployment** (for Agent 2)
    - Look for a deployment name like: `text-embedding-ada-002`, `text-embedding-3-small`, etc.
- **Usage:** Set as `AZURE_OPENAI_DEPLOYMENT_NAME` and `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`

### 4. **API Version** (Usually auto-detected)
- **Default:** `2024-02-15-preview` (for traditional Azure OpenAI)
- **For Foundry:** May need to use `2024-06-01` or check API documentation
- **Usage:** Set as `AZURE_OPENAI_API_VERSION`

## 🔧 Configuration Steps

### Step 1: Get Complete Endpoint URL

1. Click **"View all endpoints"** link in the "Endpoints and keys" section
2. Find the **complete Microsoft Foundry project endpoint**
3. It should look like: `https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI` (full project name)

### Step 2: Find Deployment Names

1. Navigate to **"Deployments"** or **"Models"** section in your Foundry project
2. Note the deployment names for:
   - Your GPT-4 model (e.g., `gpt-4`, `gpt-4-turbo`)
   - Your embedding model (e.g., `text-embedding-ada-002`)

### Step 3: Configure Environment Variables

#### For HealthBotOrchestrator Function App:

```bash
az functionapp config appsettings set \
  --name HealthBotOrchestrator \
  --resource-group healthcare-assistant-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI" \
    AZURE_OPENAI_API_KEY="AVliAvqlKzIY0h3tjejWZs4zoRnX9OiJfcUAn30ZYgZKZS5Lbv6dJQQJ99BKACHYHv6XJ3w" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4" \
    AZURE_OPENAI_API_VERSION="2024-06-01"
```

#### For HealthBotTools Function App:

```bash
az functionapp config appsettings set \
  --name HealthBotTools \
  --resource-group healthcare-assistant-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI" \
    AZURE_OPENAI_API_KEY="AVliAvqlKzIY0h3tjejWZs4zoRnX9OiJfcUAn30ZYgZKZS5Lbv6dJQQJ99BKACHYHv6XJ3w" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4" \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME="text-embedding-ada-002" \
    AZURE_OPENAI_API_VERSION="2024-06-01"
```

### Step 4: Update Local Settings (for local development)

#### `src/orchestrator-api/local.settings.json`:
```json
{
  "Values": {
    "AZURE_OPENAI_ENDPOINT": "https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI",
    "AZURE_OPENAI_API_KEY": "AVliAvqlKzIY0h3tjejWZs4zoRnX9OiJfcUAn30ZYgZKZS5Lbv6dJQQJ99BKACHYHv6XJ3w",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
    "AZURE_OPENAI_API_VERSION": "2024-06-01"
  }
}
```

#### `src/specialized-tools/local.settings.json`:
```json
{
  "Values": {
    "AZURE_OPENAI_ENDPOINT": "https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI",
    "AZURE_OPENAI_API_KEY": "AVliAvqlKzIY0h3tjejWZs4zoRnX9OiJfcUAn30ZYgZKZS5Lbv6dJQQJ99BKACHYHv6XJ3w",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME": "text-embedding-ada-002",
    "AZURE_OPENAI_API_VERSION": "2024-06-01"
  }
}
```

## ⚠️ Important Notes

### Azure AI Foundry vs Traditional Azure OpenAI

1. **Endpoint Format:**
   - **Traditional:** `https://[resource-name].openai.azure.com/`
   - **Foundry:** `https://[region].services.ai.azure.com/api/projects/[project-name]`

2. **API Version:**
   - Foundry may use different API versions
   - Check the API documentation link in your Foundry portal
   - Common versions: `2024-06-01`, `2024-02-15-preview`

3. **Deployment Names:**
   - In Foundry, deployment names are what you named your model deployments
   - They may differ from traditional Azure OpenAI naming

4. **Authentication:**
   - Foundry uses project-level API keys (what you see in the portal)
   - These are different from resource-level keys in traditional Azure OpenAI

## 🔍 How to Find Missing Information

### Finding the Complete Endpoint:
1. Click **"View all endpoints"** in the portal
2. Look for the full project endpoint URL
3. It should include the complete project name: `healthcare-agenticAI`

### Finding Deployment Names:
1. Navigate to **"Deployments"** or **"Models"** tab
2. Look for your deployed models
3. Note the exact deployment names (case-sensitive)

### Finding API Version:
1. Click the **"API documentation"** link in the portal
2. Check the API reference for the correct version
3. Or try common versions: `2024-06-01`, `2024-02-15-preview`

## ✅ Quick Checklist

- [ ] API Key copied (✅ You have this)
- [ ] Complete endpoint URL obtained (Click "View all endpoints")
- [ ] GPT-4 deployment name found (Check Deployments section)
- [ ] Embedding model deployment name found (Check Deployments section)
- [ ] API version confirmed (Check API documentation)
- [ ] Environment variables configured in both Function Apps
- [ ] Local settings updated for development

## 🧪 Testing

After configuration, test with:

```bash
# Test Orchestrator
curl -X POST "https://healthbotorchestrator.azurewebsites.net/api/orchestrate?code=KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "I have a headache"}'
```

If you get authentication errors, verify:
- Endpoint URL is complete and correct
- API key is correct
- Deployment names match exactly
- API version is supported

