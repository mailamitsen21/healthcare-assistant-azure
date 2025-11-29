# Architecture Overview

## System Architecture

The Healthcare Assistant is a multi-agent system built on Azure, using Semantic Kernel for orchestration and specialized Azure Functions for domain-specific tasks.

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Web App)                      │
│              HTML/JavaScript Chat Interface                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Orchestrator API (Agent 3)                       │
│         Semantic Kernel + Azure OpenAI                     │
│  - Plans agent execution                                    │
│  - Synthesizes responses                                    │
└──────┬──────────────┬──────────────┬───────────────────────┘
       │              │              │
       │ HTTP         │ HTTP         │ HTTP
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Agent 1    │ │  Agent 2    │ │  Agent 3    │
│  Parser     │ │  Knowledge  │ │  Booking    │
│             │ │  Retrieval  │ │             │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │              │              │
       │              │              │
       └──────────────┴──────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │   Cosmos DB      │
            │  - Knowledge     │
            │  - Appointments  │
            └──────────────────┘
```

## Component Details

### 1. Frontend (`src/ui-frontend/`)

**Technology:** HTML, CSS, JavaScript  
**Hosting:** Azure Web App or Static Web App

**Responsibilities:**
- User interface for chat interaction
- Sends requests to orchestrator API only
- Displays responses and maintains conversation history

**Files:**
- `index.html` - Main HTML structure
- `app.js` - Frontend logic and API communication
- `style.css` - Styling

### 2. Orchestrator API (`src/orchestrator-api/`)

**Technology:** Python, Semantic Kernel, Azure Functions  
**Hosting:** Azure Function App

**Responsibilities:**
- Single entry point for all user queries
- Uses Semantic Kernel to plan agent execution
- Coordinates calls to specialized agents
- Synthesizes final responses using Azure OpenAI

**Key Components:**
- `function_app.py` - HTTP trigger endpoint
- `sk_core/planner.py` - Semantic Kernel initialization and planning
- `sk_core/tool_connector.py` - HTTP client for calling specialized agents

**Flow:**
1. Receive user query
2. Create execution plan using Semantic Kernel
3. Call specialized agents in sequence
4. Synthesize responses into final answer
5. Return to frontend

### 3. Specialized Tools (`src/specialized-tools/`)

**Technology:** Python, Azure Functions  
**Hosting:** Azure Function App (single app with multiple functions)

#### Agent 1: Symptom Parser (`agents/agent1_parser/`)

**Purpose:** Parse unstructured text into structured symptom data

**Input:** Raw user text  
**Output:** JSON with:
- `primary_intent`: Main intent (symptom_report, question, etc.)
- `symptoms`: List of symptoms
- `severity`: Severity level
- `duration`: Duration of symptoms

**Technology:** Uses Azure OpenAI to extract structured data

#### Agent 2: Knowledge Retrieval (`agents/agent2_knowledge/`)

**Purpose:** Retrieve relevant medical knowledge using vector search

**Input:** Query text  
**Output:** List of relevant knowledge items with similarity scores

**Technology:**
- Uses `EmbeddingService` to convert query to vector
- Performs vector search on Cosmos DB `KnowledgeVectors` container
- Returns top-k most relevant results

#### Agent 3: Appointment Booking (`agents/agent3_booking/`)

**Purpose:** Handle appointment booking and availability checks

**Input:** Appointment query with optional parameters  
**Output:** Booking confirmation or availability information

**Technology:**
- SQL queries on Cosmos DB `Appointments` container
- Supports: book, check availability, cancel, list appointments

### 4. Shared Database Module (`src/specialized-tools/shared-db/`)

**Technology:** Azure Cosmos DB SDK

**Components:**
- `cosmos_client.py` - Centralized Cosmos DB client
  - Manages connections
  - Creates databases/containers if needed
  - Provides container access

- `embedding_service.py` - Text-to-vector conversion
  - Uses Azure OpenAI embeddings API
  - Converts text to vectors for vector search
  - Provides cosine similarity calculation

## Data Flow

### Example: User asks "I have a headache, what should I do?"

1. **Frontend** → Sends POST to `/api/orchestrate` with query
2. **Orchestrator** → Semantic Kernel creates plan:
   - Step 1: Call Agent 1 to parse symptoms
   - Step 2: Call Agent 2 to retrieve knowledge about headaches
   - Step 3: Synthesize response
3. **Agent 1** → Parses text, returns structured data:
   ```json
   {
     "primary_intent": "symptom_report",
     "symptoms": ["headache"]
   }
   ```
4. **Agent 2** → Searches knowledge base, returns relevant articles
5. **Orchestrator** → Synthesizes Agent 1 and Agent 2 results into final response
6. **Frontend** → Displays response to user

## Data Storage

### Cosmos DB Containers

#### KnowledgeVectors Container
- **Partition Key:** `/id`
- **Vector Index:** On `/embedding` field
- **Schema:**
  ```json
  {
    "id": "unique-id",
    "title": "Document title",
    "content": "Medical knowledge content",
    "category": "symptoms|treatments|prevention",
    "embedding": [0.123, 0.456, ...]  // Vector array
  }
  ```

#### Appointments Container
- **Partition Key:** `/user_id`
- **Schema:**
  ```json
  {
    "id": "appt_20240115120000",
    "user_id": "user123",
    "date": "2024-01-15",
    "time": "14:00",
    "doctor": "Dr. Smith",
    "reason": "Headache follow-up",
    "status": "scheduled",
    "created_at": "2024-01-14T10:00:00Z"
  }
  ```

## Security Considerations

1. **Function Keys:** All Azure Functions use function-level authentication
2. **API Keys:** Stored in Azure App Settings (not in code)
3. **CORS:** Configure CORS for frontend domain
4. **Rate Limiting:** Consider adding rate limiting for production
5. **Input Validation:** All inputs are validated before processing

## Scalability

- **Function Apps:** Auto-scale based on demand
- **Cosmos DB:** Can scale throughput and storage independently
- **Frontend:** Static files can be served via CDN
- **Orchestrator:** Can handle multiple concurrent requests

## Monitoring

- **Application Insights:** Integrated for all Function Apps
- **Logging:** Structured logging throughout
- **Metrics:** Track agent call counts, response times, errors

## Future Enhancements

1. **Agent 5:** Could add a diagnosis assistant
2. **Caching:** Add Redis cache for frequent queries
3. **Streaming:** Support streaming responses for better UX
4. **Multi-language:** Add support for multiple languages
5. **Voice Interface:** Add speech-to-text and text-to-speech

