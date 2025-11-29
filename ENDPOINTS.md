# API Endpoints Reference

Quick reference for all API endpoints in the Healthcare Assistant system.

## 🌐 Frontend

- **URL:** `https://healthbot-ui-app.azurewebsites.net`
- **Type:** Static Web App / Web App
- **Files:** `index.html`, `app.js`, `config.js`, `style.css`

## 🎯 Orchestrator API (Agent 3)

**Function App:** `HealthBotOrchestrator`

### Main Endpoint

```
POST https://healthbotorchestrator.azurewebsites.net/api/orchestrate
```

**Authentication:** Function key (optional, via `?code=` query parameter)

**Request:**
```json
{
  "query": "I have a headache, what should I do?",
  "history": [
    {"role": "user", "content": "previous message"},
    {"role": "assistant", "content": "previous response"}
  ]
}
```

**Response:**
```json
{
  "response": "Based on your symptoms, I recommend...",
  "agent_calls": ["agent1_parser", "agent2_knowledge"]
}
```

**Local Development:**
```
POST http://localhost:7071/api/orchestrate
```

## 🔧 Specialized Tools (Agents 1, 2, 3)

**Function App:** `HealthBotTools`

### Agent 1: Symptom Parser

```
POST https://healthbottools.azurewebsites.net/api/symptom_interpreter_parser
```

**Request:**
```json
{
  "text": "I have been experiencing headaches and fever for 3 days"
}
```

**Response:**
```json
{
  "primary_intent": "symptom_report",
  "symptoms": ["headache", "fever"],
  "severity": "moderate",
  "duration": "3 days",
  "additional_context": {}
}
```

**Local Development:**
```
POST http://localhost:7071/api/symptom_interpreter_parser
```

---

### Agent 2: Knowledge Retrieval

```
POST https://healthbottools.azurewebsites.net/api/knowledge_retrieval_agent
```

**Request:**
```json
{
  "query": "What causes headaches?",
  "top_k": 3
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "kb_headache_management",
      "title": "Headache Management",
      "content": "Headaches can be caused by...",
      "category": "symptoms",
      "similarity_score": 0.95
    }
  ]
}
```

**Local Development:**
```
POST http://localhost:7071/api/knowledge_retrieval_agent
```

---

### Agent 3: Appointment Booking

```
POST https://healthbottools.azurewebsites.net/api/appointment_followup_agent
```

**Request (Book Appointment):**
```json
{
  "query": "Book an appointment",
  "date": "2024-01-15",
  "time": "14:00",
  "user_id": "user123",
  "doctor": "Dr. Smith",
  "reason": "Headache follow-up"
}
```

**Response:**
```json
{
  "success": true,
  "appointment_id": "appt_20240115120000",
  "message": "Appointment scheduled for 2024-01-15 at 14:00 with Dr. Smith"
}
```

**Request (Check Availability):**
```json
{
  "query": "Check availability",
  "date": "2024-01-15",
  "doctor": "Dr. Smith"
}
```

**Response:**
```json
{
  "date": "2024-01-15",
  "doctor": "Dr. Smith",
  "available_slots": ["09:00", "09:30", "10:00", "14:00"]
}
```

**Request (List Appointments):**
```json
{
  "query": "List my appointments",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "user_id": "user123",
  "appointments": [
    {
      "id": "appt_20240115120000",
      "date": "2024-01-15",
      "time": "14:00",
      "doctor": "Dr. Smith",
      "status": "scheduled"
    }
  ],
  "count": 1
}
```

**Local Development:**
```
POST http://localhost:7071/api/appointment_followup_agent
```

## 🔑 Getting Function Keys

### Via Azure Portal

1. Navigate to Function App
2. Go to **Functions** > Select function name
3. Click **Get function URL**
4. Copy the `code` parameter value

### Via Azure CLI

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

## 🧪 Testing Endpoints

### Using cURL

```bash
# Test Orchestrator
curl -X POST "https://healthbotorchestrator.azurewebsites.net/api/orchestrate?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "I have a headache"}'

# Test Agent 1
curl -X POST "https://healthbottools.azurewebsites.net/api/symptom_interpreter_parser?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "I have been experiencing headaches for 2 days"}'

# Test Agent 2
curl -X POST "https://healthbottools.azurewebsites.net/api/knowledge_retrieval_agent?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What causes headaches?", "top_k": 3}'

# Test Agent 3
curl -X POST "https://healthbottools.azurewebsites.net/api/appointment_followup_agent?code=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "Check availability", "date": "2024-01-15"}'
```

### Using Postman

1. Create a new POST request
2. Set URL to endpoint
3. Add `code` as query parameter (if using function key auth)
4. Set Headers: `Content-Type: application/json`
5. Set Body (raw JSON) with request payload
6. Send request

### Using JavaScript (Frontend)

```javascript
const response = await fetch('https://healthbotorchestrator.azurewebsites.net/api/orchestrate?code=YOUR_KEY', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'I have a headache',
    history: []
  })
});

const data = await response.json();
console.log(data);
```

## ⚠️ Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (missing or invalid parameters)
- `500` - Internal Server Error

## 🔒 Security Notes

1. **Function Keys:** Keep function keys secret. Don't commit them to version control.
2. **CORS:** Ensure CORS is configured for your frontend domain.
3. **HTTPS:** All endpoints use HTTPS in production.
4. **Rate Limiting:** Consider implementing rate limiting for production use.

## 📝 Environment Variables

### HealthBotOrchestrator
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_API_VERSION`
- `SPECIALIZED_TOOLS_BASE_URL`

### HealthBotTools
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`
- `AZURE_OPENAI_API_VERSION`
- `COSMOS_DB_ENDPOINT`
- `COSMOS_DB_KEY`
- `AZURE_COSMOSDB_DATABASE_NAME`
- `AZURE_COSMOSDB_KNOWLEDGE_CONTAINER`
- `AZURE_COSMOSDB_APPOINTMENTS_CONTAINER`

