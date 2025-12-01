"""
Simple script to upload RAG entries to Cosmos DB
Run this after generating rag_entries.json
"""
import os
import sys
import json
import logging
import uuid

# Add shared-db to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'specialized-tools', 'shared-db'))

from cosmos_client import CosmosClient
from embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables (update these with your actual values)
# You can also set these in your shell before running
os.environ.setdefault('COSMOS_DB_ENDPOINT', 'https://cosmos-health.documents.azure.com:443/')
os.environ.setdefault('COSMOS_DB_KEY', 'YOUR_COSMOS_DB_KEY==')
os.environ.setdefault('AZURE_COSMOSDB_DATABASE_NAME', 'HealthcareDB')
os.environ.setdefault('AZURE_OPENAI_ENDPOINT', 'https://ai-healthcare.openai.azure.com/')
os.environ.setdefault('AZURE_OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
os.environ.setdefault('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-ada-002')
os.environ.setdefault('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')

def load_rag_entries(file_path: str = None) -> list:
    """Load RAG entries from JSON file"""
    if file_path is None:
        # Try multiple locations
        possible_paths = [
            "rag_entries.json",
            "../rag_entries.json",
            os.path.join(os.path.dirname(__file__), "..", "rag_entries.json")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if file_path is None:
            logger.error("RAG entries file not found. Tried: " + ", ".join(possible_paths))
            logger.info("Please run generate_rag_data.py first")
            return []
    
    if not os.path.exists(file_path):
        logger.error(f"RAG entries file not found: {file_path}")
        return []
    
    with open(file_path, 'r') as f:
        return json.load(f)

def prepare_entries_with_embeddings(entries: list, embedding_service: EmbeddingService) -> list:
    """Prepare entries with embeddings for Cosmos DB"""
    cosmos_entries = []
    
    logger.info(f"Generating embeddings for {len(entries)} entries...")
    
    # Process in batches
    batch_size = 10
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i+batch_size]
        
        # Generate embeddings
        texts = [f"{entry['title']}. {entry['content']}" for entry in batch]
        
        try:
            embeddings = embedding_service.get_embeddings_batch(texts)
            
            for entry, embedding in zip(batch, embeddings):
                cosmos_entry = {
                    "id": str(uuid.uuid4()),
                    "title": entry['title'],
                    "content": entry['content'],
                    "category": entry.get('category', 'general'),
                    "embedding": embedding
                }
                cosmos_entries.append(cosmos_entry)
            
            logger.info(f"Processed {min(i+batch_size, len(entries))}/{len(entries)} entries")
            
        except Exception as e:
            logger.error(f"Error processing batch {i//batch_size + 1}: {str(e)}")
            continue
    
    return cosmos_entries

def upload_to_cosmos(entries: list, container_name: str = "KnowledgeVectors"):
    """Upload entries to Cosmos DB"""
    cosmos_client = CosmosClient()
    
    # Get or create container
    container = cosmos_client.get_container(
        database_name=cosmos_client.database_name,
        container_name=container_name,
        partition_key="/id"
    )
    
    logger.info(f"Uploading {len(entries)} entries to container: {container_name}")
    
    # Upload entries
    uploaded = 0
    failed = 0
    
    for i, entry in enumerate(entries):
        try:
            container.create_item(body=entry)
            uploaded += 1
            
            if uploaded % 50 == 0:
                logger.info(f"Uploaded {uploaded}/{len(entries)} entries")
                
        except Exception as e:
            logger.error(f"Error uploading entry {entry.get('id', 'unknown')}: {str(e)}")
            failed += 1
            continue
    
    logger.info(f"Upload complete: {uploaded} uploaded, {failed} failed")
    return uploaded, failed

def main():
    """Main function"""
    logger.info("=== RAG Data Upload Script ===")
    
    # Load entries
    logger.info("Loading RAG entries...")
    entries = load_rag_entries("rag_entries.json")
    
    if not entries:
        return
    
    logger.info(f"Loaded {len(entries)} entries")
    
    # Initialize services
    logger.info("Initializing services...")
    try:
        embedding_service = EmbeddingService()
    except Exception as e:
        logger.error(f"Failed to initialize EmbeddingService: {str(e)}")
        logger.error("Please check your Azure OpenAI configuration")
        return
    
    # Prepare entries with embeddings
    cosmos_entries = prepare_entries_with_embeddings(entries, embedding_service)
    
    if not cosmos_entries:
        logger.error("No entries prepared for upload")
        return
    
    # Upload to Cosmos DB
    uploaded, failed = upload_to_cosmos(cosmos_entries)
    
    logger.info(f"\n=== Upload Summary ===")
    logger.info(f"Total entries: {len(entries)}")
    logger.info(f"Successfully uploaded: {uploaded}")
    logger.info(f"Failed: {failed}")
    
    if uploaded > 0:
        logger.info(f"\n✅ Successfully uploaded {uploaded} RAG entries to Cosmos DB!")
        logger.info("Entries are now available for Agent 2 (Knowledge Retrieval) to use")

if __name__ == "__main__":
    main()

