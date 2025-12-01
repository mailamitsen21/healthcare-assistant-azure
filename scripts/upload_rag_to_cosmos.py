"""
Upload RAG entries to Cosmos DB
Generates embeddings and uploads to KnowledgeVectors container
"""
import os
import sys
import json
import logging
import uuid
from typing import List, Dict, Any
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'specialized-tools', 'shared-db'))

from cosmos_client import CosmosClient
from embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables should be set in Azure or local.settings.json

def load_rag_entries(file_path: str = "rag_entries.json") -> List[Dict[str, Any]]:
    """Load RAG entries from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def prepare_entries_for_cosmos(entries: List[Dict[str, Any]], embedding_service: EmbeddingService) -> List[Dict[str, Any]]:
    """Prepare entries with embeddings for Cosmos DB"""
    cosmos_entries = []
    
    logger.info(f"Generating embeddings for {len(entries)} entries...")
    
    # Process in batches to avoid rate limits
    batch_size = 10
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i+batch_size]
        
        # Generate embeddings for batch
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
            # Continue with next batch
            continue
    
    return cosmos_entries

def upload_to_cosmos(entries: List[Dict[str, Any]], container_name: str = "KnowledgeVectors"):
    """Upload entries to Cosmos DB"""
    cosmos_client = CosmosClient()
    
    # Get or create container
    container = cosmos_client.get_container(
        database_name=cosmos_client.database_name,
        container_name=container_name,
        partition_key="/id"
    )
    
    logger.info(f"Uploading {len(entries)} entries to container: {container_name}")
    
    # Upload in batches
    batch_size = 10
    uploaded = 0
    failed = 0
    
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i+batch_size]
        
        for entry in batch:
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
    # Check if entries file exists
    entries_file = "rag_entries.json"
    if not os.path.exists(entries_file):
        logger.error(f"RAG entries file not found: {entries_file}")
        logger.info("Please run generate_rag_data.py first to create the entries file")
        return
    
    # Load entries
    logger.info("Loading RAG entries...")
    entries = load_rag_entries(entries_file)
    logger.info(f"Loaded {len(entries)} entries")
    
    # Initialize services
    logger.info("Initializing services...")
    embedding_service = EmbeddingService()
    
    # Prepare entries with embeddings
    cosmos_entries = prepare_entries_for_cosmos(entries, embedding_service)
    
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

