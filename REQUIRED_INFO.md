# Required Information from Azure AI Foundry Portal

Based on the portal page you're viewing, here's exactly what you need:

## ✅ Information You Already Have

### 1. API Key
- **Value:** `AVliAvqlKzIY0h3tjejWZs4zoRnX9OiJfcUAn30ZYgZKZS5Lbv6dJQQJ99BKACHYHv6XJ3w`
- **Where:** "Endpoints and keys" → "API Key" field
- **Used for:** `AZURE_OPENAI_API_KEY` environment variable

### 2. Project Endpoint (Partially Visible)
- **Visible:** `https://ai-healthcare.services.ai.azure.com/api/projects/healt`
- **Action Needed:** Click **"View all endpoints"** to get the complete URL
- **Should be:** `https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI` (full project name)
- **Used for:** `AZURE_OPENAI_ENDPOINT` environment variable

## ⚠️ Information You Need to Find

### 3. GPT-4 Deployment Name
- **Where to find:** Click on **"Deployments"** or **"Models"** tab in your Foundry project
- **What to look for:** A deployment name like:
  - `gpt-4`
  - `gpt-4-turbo`
  - `gpt-4o`
  - Or whatever you named your GPT-4 deployment
- **Used for:** `AZURE_OPENAI_DEPLOYMENT_NAME` environment variable

### 4. Embedding Model Deployment Name
- **Where to find:** Same "Deployments" or "Models" section
- **What to look for:** A deployment name like:
  - `text-embedding-ada-002`
  - `text-embedding-3-small`
  - `text-embedding-3-large`
  - Or whatever you named your embedding model deployment
- **Used for:** `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` environment variable

### 5. API Version (Optional - has default)
- **Where to find:** Click **"API documentation"** link in the portal
- **Default value:** `2024-02-15-preview` (may need `2024-06-01` for Foundry)
- **Used for:** `AZURE_OPENAI_API_VERSION` environment variable

## 📝 Quick Action Items

1. **Click "View all endpoints"** → Copy the complete endpoint URL
2. **Navigate to "Deployments" tab** → Note your GPT-4 deployment name
3. **Navigate to "Deployments" tab** → Note your embedding model deployment name
4. **Click "API documentation"** → Check the API version (optional)

## 🔧 Where This Information Goes

Once you have all the information, you'll configure it in:

1. **Azure Function Apps** (via Azure Portal or CLI):
   - `HealthBotOrchestrator` Function App → Configuration → Application settings
   - `HealthBotTools` Function App → Configuration → Application settings

2. **Local Development** (for testing):
   - `src/orchestrator-api/local.settings.json`
   - `src/specialized-tools/local.settings.json`

## 📋 Summary Table

| Information | Status | Location in Portal | Environment Variable |
|------------|--------|-------------------|---------------------|
| API Key | ✅ Have it | Endpoints and keys → API Key | `AZURE_OPENAI_API_KEY` |
| Endpoint URL | ⚠️ Need complete | Click "View all endpoints" | `AZURE_OPENAI_ENDPOINT` |
| GPT-4 Deployment | ❌ Need to find | Deployments tab | `AZURE_OPENAI_DEPLOYMENT_NAME` |
| Embedding Deployment | ❌ Need to find | Deployments tab | `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` |
| API Version | ⚠️ Optional | API documentation | `AZURE_OPENAI_API_VERSION` |

## 🎯 Next Steps

1. Get the complete endpoint URL from "View all endpoints"
2. Find your deployment names in the "Deployments" section
3. Update the configuration files (see `AZURE_AI_FOUNDRY_SETUP.md` for detailed steps)

