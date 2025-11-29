# Deployment Checklist

Use this checklist to ensure all components are properly deployed and configured.

## ✅ Pre-Deployment

- [ ] Azure subscription active and accessible
- [ ] Azure OpenAI service provisioned with:
  - [ ] GPT-4 deployment (or GPT-3.5-turbo)
  - [ ] Text embedding model (text-embedding-ada-002)
- [ ] Azure Cosmos DB account created
- [ ] Azure CLI installed and logged in (`az login`)
- [ ] VS Code with Azure extensions installed
- [ ] Azure Functions Core Tools v4 installed
- [ ] All code reviewed and tested locally

## 🏗️ Infrastructure Setup

### Resource Group
- [ ] Resource group created: `healthcare-assistant-rg`
- [ ] Location selected: `eastus` (or preferred region)

### Function App: HealthBotOrchestrator
- [ ] Function App created: `HealthBotOrchestrator`
- [ ] Runtime: Python 3.11
- [ ] Plan: Consumption (Serverless)
- [ ] Storage account linked

### Function App: HealthBotTools
- [ ] Function App created: `HealthBotTools`
- [ ] Runtime: Python 3.11
- [ ] Plan: Consumption (Serverless)
- [ ] Storage account linked

### Web App: healthbot-ui-app
- [ ] Web App created: `healthbot-ui-app`
- [ ] Runtime: Node.js 18 LTS (or Static Web App)
- [ ] Plan: Free (F1) or Basic

## ⚙️ Configuration

### HealthBotOrchestrator Settings
- [ ] `AZURE_OPENAI_ENDPOINT` set
- [ ] `AZURE_OPENAI_API_KEY` set
- [ ] `AZURE_OPENAI_DEPLOYMENT_NAME` set (default: "gpt-4")
- [ ] `AZURE_OPENAI_API_VERSION` set (default: "2024-02-15-preview")
- [ ] `SPECIALIZED_TOOLS_BASE_URL` set to `https://healthbottools.azurewebsites.net/api`
- [ ] CORS configured with frontend URL

### HealthBotTools Settings
- [ ] `AZURE_OPENAI_ENDPOINT` set
- [ ] `AZURE_OPENAI_API_KEY` set
- [ ] `AZURE_OPENAI_DEPLOYMENT_NAME` set (default: "gpt-4")
- [ ] `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` set (default: "text-embedding-ada-002")
- [ ] `AZURE_OPENAI_API_VERSION` set (default: "2024-02-15-preview")
- [ ] `COSMOS_DB_ENDPOINT` set
- [ ] `COSMOS_DB_KEY` set
- [ ] `AZURE_COSMOSDB_DATABASE_NAME` set (default: "HealthcareDB")
- [ ] `AZURE_COSMOSDB_KNOWLEDGE_CONTAINER` set (default: "KnowledgeVectors")
- [ ] `AZURE_COSMOSDB_APPOINTMENTS_CONTAINER` set (default: "Appointments")

## 📦 Code Deployment

### Orchestrator API
- [ ] Navigate to `src/orchestrator-api`
- [ ] Verify `requirements.txt` is up to date
- [ ] Deploy to `HealthBotOrchestrator`
- [ ] Verify deployment succeeded
- [ ] Check function appears in Azure Portal

### Specialized Tools
- [ ] Navigate to `src/specialized-tools`
- [ ] Verify `requirements.txt` is up to date
- [ ] Deploy to `HealthBotTools`
- [ ] Verify deployment succeeded
- [ ] Check all three functions appear:
  - [ ] `symptom_interpreter_parser`
  - [ ] `knowledge_retrieval_agent`
  - [ ] `appointment_followup_agent`

### Frontend
- [ ] Update `src/ui-frontend/config.js` with orchestrator URL
- [ ] Deploy frontend to `healthbot-ui-app`
- [ ] Verify files are accessible

## 🔗 Endpoint Configuration

### Get Function URLs
- [ ] Orchestrator endpoint URL copied
- [ ] Specialized tools endpoint URLs copied
- [ ] Function keys retrieved (if using)

### Update Frontend Config
- [ ] `config.js` updated with orchestrator URL
- [ ] Function key added (optional)
- [ ] Config file deployed with frontend

## 🧪 Testing

### Test Orchestrator
- [ ] Test endpoint with cURL or Postman
- [ ] Verify response format is correct
- [ ] Check logs for errors

### Test Agent 1 (Symptom Parser)
- [ ] Test with sample symptom text
- [ ] Verify structured output
- [ ] Check logs for errors

### Test Agent 2 (Knowledge Retrieval)
- [ ] Test with sample query
- [ ] Verify vector search works
- [ ] Check Cosmos DB connection
- [ ] Verify results are returned

### Test Agent 3 (Appointment Booking)
- [ ] Test booking an appointment
- [ ] Test checking availability
- [ ] Test listing appointments
- [ ] Verify Cosmos DB writes/reads

### Test Frontend
- [ ] Open frontend URL in browser
- [ ] Send test query: "I have a headache"
- [ ] Verify response appears
- [ ] Check browser console for errors
- [ ] Verify CORS is working (no CORS errors)

### End-to-End Test
- [ ] Complete flow: Frontend → Orchestrator → Agents → Response
- [ ] Verify all agents are called correctly
- [ ] Check response synthesis works
- [ ] Verify conversation history is maintained

## 🔒 Security

- [ ] Function keys stored securely (not in code)
- [ ] API keys stored in Azure App Settings
- [ ] CORS configured correctly
- [ ] HTTPS enforced for all endpoints
- [ ] No sensitive data in logs

## 📊 Monitoring

- [ ] Application Insights enabled
- [ ] Logs accessible in Azure Portal
- [ ] Metrics dashboard set up (optional)
- [ ] Alerts configured (optional)

## 🗄️ Database Setup

### Cosmos DB
- [ ] Database `HealthcareDB` created
- [ ] Container `KnowledgeVectors` created
- [ ] Container `Appointments` created
- [ ] Vector index configured on `KnowledgeVectors.embedding`
- [ ] Sample knowledge data populated (optional)
- [ ] Connection strings verified

## 📝 Documentation

- [ ] Endpoint URLs documented
- [ ] Function keys documented (securely)
- [ ] Configuration values documented
- [ ] Deployment process documented
- [ ] Troubleshooting guide available

## 🚀 Post-Deployment

- [ ] All endpoints responding correctly
- [ ] No errors in Application Insights
- [ ] Performance is acceptable
- [ ] Frontend accessible and functional
- [ ] Team notified of deployment
- [ ] Monitoring alerts set up

## 🔄 Rollback Plan

- [ ] Previous deployment version identified
- [ ] Rollback procedure documented
- [ ] Backup of configuration settings

## 📞 Support Information

- [ ] Azure subscription ID noted
- [ ] Resource group name documented
- [ ] Function App names documented
- [ ] Web App name documented
- [ ] Contact information for issues

---

## Quick Test Commands

```bash
# Test Orchestrator
curl -X POST "https://healthbotorchestrator.azurewebsites.net/api/orchestrate?code=KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "I have a headache"}'

# Test Agent 1
curl -X POST "https://healthbottools.azurewebsites.net/api/symptom_interpreter_parser?code=KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "I have headaches"}'

# Test Frontend
open https://healthbot-ui-app.azurewebsites.net
```

---

**Last Updated:** [Date]
**Deployed By:** [Name]
**Version:** [Version Number]

