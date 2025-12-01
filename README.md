# Healthcare Assistant - Multi-Agent System on Azure

A robust multi-agent healthcare assistant system built on Azure, using Semantic Kernel for orchestration and specialized Azure Functions for domain-specific tasks.

## Architecture Overview

- **Orchestrator (Agent 3)**: Semantic Kernel-based orchestrator that coordinates all agents
- **Specialized Tools**: Three specialized agents (Agents 1, 2, 3) for specific tasks
- **Frontend**: Simple chat interface for user interaction
- **Database**: Azure Cosmos DB for knowledge base and appointments

## Project Structure

```
/Healthcare-Assistant-Project
|-- /deployment                 # Azure Infrastructure as Code
|-- /src
|   |-- /ui-frontend            # Azure Web App (Chat Interface)
|   |-- /orchestrator-api       # Agent 3: Semantic Kernel Orchestrator
|   |-- /specialized-tools      # Agents 1, 2, 3: Azure Functions
|       |-- /agents/            # Logic for specialized tools
|       |-- /shared-db/         # Cosmos DB interaction layer
```

## Setup Instructions

1. **Prerequisites**:
   - Azure subscription
   - Azure OpenAI service
   - Azure Cosmos DB account
   - Python 3.9+

2. **Local Development**:
   ```bash
   # Install orchestrator dependencies
   cd src/orchestrator-api
   pip install -r requirements.txt

   # Install specialized tools dependencies
   cd ../specialized-tools
   pip install -r requirements.txt
   ```

3. **Configuration**:
   - Update `local.settings.json` in `specialized-tools/` with your connection strings
   - Update environment variables in `orchestrator-api/` for Azure OpenAI

4. **Deployment**:
   - Use the Bicep templates in `/deployment` to provision Azure resources
   - Deploy each component to its respective Azure service

## Components

### Orchestrator API (Agent 3)
- Main entry point for all requests
- Uses Semantic Kernel to plan and execute agent calls
- Synthesizes responses from multiple agents

### Specialized Tools
- **Agent 1**: Symptom interpreter and parser
- **Agent 2**: Knowledge retrieval agent (vector search)
- **Agent 3**: Appointment booking and follow-up agent

### Frontend
- Simple HTML/JavaScript chat interface
- Communicates only with the orchestrator API

