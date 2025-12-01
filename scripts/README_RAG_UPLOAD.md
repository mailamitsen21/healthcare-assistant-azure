# RAG Data Upload Guide

This guide explains how to generate and upload 500 RAG (Retrieval Augmented Generation) entries to Cosmos DB for use by Agent 1 and Agent 3.

## Overview

The RAG entries provide healthcare knowledge that can be retrieved by:
- **Agent 1 (Symptom Parser)**: Can reference knowledge entries to better understand symptoms
- **Agent 2 (Knowledge Retrieval)**: Uses vector search to find relevant knowledge entries
- **Agent 3 (Appointment Booking)**: Can reference appointment-related information

## Prerequisites

1. **Python packages installed:**
   ```bash
   pip install azure-cosmos openai numpy
   ```

2. **Azure credentials configured:**
   - Cosmos DB endpoint and key
   - Azure OpenAI endpoint and API key
   - Embedding deployment name

## Steps

### Step 1: Generate RAG Entries

```bash
cd scripts
python3 generate_rag_data.py
```

This creates `rag_entries.json` with 500 healthcare knowledge entries covering:
- Symptoms (20 entries)
- Treatments (10 entries)
- Appointments (10 entries)
- Conditions (10 entries)
- Prevention (10 entries)
- Medications (10 entries)
- General health topics (430 entries)

### Step 2: Upload to Cosmos DB

**Option A: Using the simple script (recommended)**

Update the credentials in `upload_rag_simple.py` if needed, then:

```bash
cd scripts
python3 upload_rag_simple.py
```

**Option B: Using Azure Function App**

You can also create an Azure Function to upload the data, or use Azure Data Factory.

### Step 3: Verify Upload

Check in Azure Portal:
1. Go to Cosmos DB account: `cosmos-health`
2. Navigate to Data Explorer
3. Select database: `HealthcareDB`
4. Select container: `KnowledgeVectors`
5. Verify entries are present

## Data Structure

Each entry in Cosmos DB has the following structure:

```json
{
  "id": "unique-uuid",
  "title": "Entry title",
  "content": "Detailed content",
  "category": "symptoms|treatments|appointments|conditions|prevention|medications|general",
  "embedding": [0.123, 0.456, ...]  // Vector array for semantic search
}
```

## Usage

Once uploaded, the entries are automatically available for:

1. **Agent 2 (Knowledge Retrieval)**: 
   - Queries the `KnowledgeVectors` container using vector search
   - Returns relevant entries based on semantic similarity

2. **Orchestrator**:
   - Can call Agent 2 to retrieve relevant knowledge
   - Synthesizes knowledge into natural language responses

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'azure'"
**Solution:** Install required packages:
```bash
pip install azure-cosmos openai numpy
```

### Error: "Failed to initialize EmbeddingService"
**Solution:** Check your Azure OpenAI credentials:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`

### Error: "Cosmos DB connection failed"
**Solution:** Verify Cosmos DB credentials:
- `COSMOS_DB_ENDPOINT`
- `COSMOS_DB_KEY`
- `AZURE_COSMOSDB_DATABASE_NAME`

## Notes

- The embedding model used is `gpt-5-mini` (as configured)
- Entries are processed in batches of 10 to avoid rate limits
- Upload progress is logged every 50 entries
- Failed entries are logged but don't stop the upload process

## Next Steps

After uploading:
1. Test Agent 2 knowledge retrieval
2. Verify vector search is working
3. Test end-to-end flow through the orchestrator
4. Consider adding more specialized entries based on usage patterns

