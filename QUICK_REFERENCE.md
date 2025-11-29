# Quick Reference Guide

## 🎯 Three Main Components

1. **HealthBotOrchestrator** (Function App) - Agent 3: Orchestrator API
2. **HealthBotTools** (Function App) - Agents 1, 2, 3: Specialized Tools
3. **healthbot-ui-app** (Web App) - Frontend Chat Interface

## 📍 Key Endpoints

### Orchestrator (Main Entry Point)
```
https://healthbotorchestrator.azurewebsites.net/api/orchestrate
```

### Specialized Tools
```
https://healthbottools.azurewebsites.net/api/symptom_interpreter_parser
https://healthbottools.azurewebsites.net/api/knowledge_retrieval_agent
https://healthbottools.azurewebsites.net/api/appointment_followup_agent
```

### Frontend
```
https://healthbot-ui-app.azurewebsites.net
```

## 🔑 Required Environment Variables

### HealthBotOrchestrator
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `SPECIALIZED_TOOLS_BASE_URL`

### HealthBotTools
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `COSMOS_DB_ENDPOINT`
- `COSMOS_DB_KEY`

## 🚀 Quick Deploy Commands

```bash
# Deploy Orchestrator
cd src/orchestrator-api
func azure functionapp publish HealthBotOrchestrator --python

# Deploy Specialized Tools
cd src/specialized-tools
func azure functionapp publish HealthBotTools --python

# Deploy Frontend (via Git)
cd src/ui-frontend
git push azure master
```

## 📚 Documentation Files

- **DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment instructions
- **ENDPOINTS.md** - Detailed API endpoint reference
- **DEPLOYMENT_CHECKLIST.md** - Pre-deployment checklist
- **QUICKSTART.md** - Local development setup
- **ARCHITECTURE.md** - System architecture overview

## 🔧 Common Tasks

### Get Function URL
```bash
az functionapp function show \
  --name HealthBotOrchestrator \
  --resource-group healthcare-assistant-rg \
  --function-name orchestrate \
  --query invokeUrlTemplate
```

### View Logs
```bash
az functionapp log tail \
  --name HealthBotOrchestrator \
  --resource-group healthcare-assistant-rg
```

### Update App Settings
```bash
az functionapp config appsettings set \
  --name HealthBotOrchestrator \
  --resource-group healthcare-assistant-rg \
  --settings KEY="value"
```

## ⚠️ Important Notes

1. **CORS must be configured** on HealthBotOrchestrator for frontend to work
2. **Function keys** are required if using FUNCTION auth level
3. **Cosmos DB containers** must be created before Agents 2 & 3 can work
4. **Vector index** must be configured on KnowledgeVectors container

## 🆘 Troubleshooting

- **CORS errors:** Check CORS settings in Function App
- **Connection errors:** Verify all environment variables are set
- **Import errors:** Ensure requirements.txt is deployed correctly
- **Timeout errors:** Check function timeout settings

