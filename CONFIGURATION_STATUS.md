# Configuration Status Check

## ✅ Information You Have

1. **API Key:** `YOUR_OPENAI_API_KEY` ✅
2. **Project Endpoint (Foundry):** `https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI` ✅
3. **Azure OpenAI Endpoint (Traditional):** `https://ai-healthcare.openai.azure.com/` ✅
4. **Azure AI Services Endpoint:** `https://ai-healthcare.cognitiveservices.azure.com/` ✅

## ⚠️ Still Need to Find

### 1. Deployment Names (Critical)

You need to find the **exact deployment names** for:

- **GPT-4 Model Deployment:**
  - Navigate to your Azure AI Foundry project
  - Go to **"Deployments"** or **"Models"** section
  - Look for a GPT-4 deployment (could be named: `gpt-4`, `gpt-4-turbo`, `gpt-4o`, `gpt-4-32k`, or a custom name)
  - **This is required for:** `AZURE_OPENAI_DEPLOYMENT_NAME`

- **Embedding Model Deployment:**
  - Same "Deployments" section
  - Look for an embedding model (could be: `text-embedding-ada-002`, `text-embedding-3-small`, `text-embedding-3-large`, or custom name)
  - **This is required for:** `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`

### 2. API Version (Optional - has default)

- Default: `2024-02-15-preview`
- For Foundry, might need: `2024-06-01`
- **This is for:** `AZURE_OPENAI_API_VERSION`

## 🎯 Which Endpoint to Use?

You have **two endpoint options**:

### Option 1: Use Azure AI Foundry (Recommended)
- **Endpoint:** `https://ai-healthcare.services.ai.azure.com/api/projects/healthcare-agenticAI`
- **Pros:** Modern, project-based, unified management
- **Cons:** May need different API version

### Option 2: Use Traditional Azure OpenAI
- **Endpoint:** `https://ai-healthcare.openai.azure.com/`
- **Pros:** Well-established, standard API version
- **Cons:** May not have all Foundry features

**Recommendation:** Start with the **Foundry endpoint** since that's what your project is set up for.

## 📋 Complete Configuration Checklist

### For HealthBotOrchestrator:
- [x] API Key
- [x] Endpoint URL (choose Foundry or Traditional)
- [ ] GPT-4 Deployment Name ⚠️ **NEED THIS**
- [ ] API Version (optional, has default)

### For HealthBotTools:
- [x] API Key
- [x] Endpoint URL (choose Foundry or Traditional)
- [ ] GPT-4 Deployment Name ⚠️ **NEED THIS**
- [ ] Embedding Model Deployment Name ⚠️ **NEED THIS**
- [ ] API Version (optional, has default)

## 🔍 How to Find Deployment Names

1. **In Azure Portal:**
   - Navigate to your Foundry project: `healthcare-agenticAI`
   - Click on **"Deployments"** tab (or **"Models"** → **"Deployments"**)
   - You'll see a list of deployed models
   - Note the exact names (they're case-sensitive)

2. **Alternative - Check Azure OpenAI Resource:**
   - Go to your Azure OpenAI resource: `ai-healthcare`
   - Navigate to **"Deployments"** under "Resource Management"
   - You'll see all your model deployments there

## ✅ Next Steps

1. **Find your deployment names** (most important!)
2. **Choose which endpoint to use** (Foundry vs Traditional)
3. **Configure the Function Apps** with all values
4. **Test the configuration**

## 💡 Quick Test

Once you have deployment names, you can test with:

```bash
# Test if your configuration works
curl https://ai-healthcare.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME/chat/completions?api-version=2024-02-15-preview \
  -H "api-key: YOUR_OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}],"model":"gpt-4"}'
```

Replace `YOUR_DEPLOYMENT_NAME` with your actual deployment name.

