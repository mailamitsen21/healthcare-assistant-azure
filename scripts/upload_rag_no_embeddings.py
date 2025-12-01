"""
Upload RAG entries to Cosmos DB without embeddings
Use this if embedding model is not available
Entries can still be searched using text-based queries
"""
import os
import sys
import json
import logging
import uuid

# Add shared-db to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'specialized-tools', 'shared-db'))

from cosmos_client import CosmosClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables
# IMPORTANT: Replace placeholder values with your actual Azure credentials
# Set these as environment variables before running, or update the defaults below
os.environ.setdefault('COSMOS_DB_ENDPOINT', os.getenv('COSMOS_DB_ENDPOINT', 'YOUR_COSMOS_DB_ENDPOINT'))
os.environ.setdefault('COSMOS_DB_KEY', os.getenv('COSMOS_DB_KEY', 'YOUR_COSMOS_DB_KEY'))
os.environ.setdefault('AZURE_COSMOSDB_DATABASE_NAME', os.getenv('AZURE_COSMOSDB_DATABASE_NAME', 'HealthcareDB'))

def load_rag_entries(file_path: str = None) -> list:
    """Load RAG entries from JSON file"""
    if file_path is None:
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
            logger.error("RAG entries file not found")
            return []
    
    with open(file_path, 'r') as f:
        return json.load(f)

def prepare_entries_for_cosmos(entries: list) -> list:
    """Prepare entries for Cosmos DB (without embeddings)"""
    cosmos_entries = []
    
    logger.info(f"Preparing {len(entries)} entries for upload...")
    
    for entry in entries:
        cosmos_entry = {
            "id": str(uuid.uuid4()),
            "title": entry['title'],
            "content": entry['content'],
            "category": entry.get('category', 'general'),
            # Create searchable text field
            "searchable_text": f"{entry['title']} {entry['content']}".lower()
        }
        cosmos_entries.append(cosmos_entry)
    
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
    logger.info("=== RAG Data Upload (No Embeddings) ===")
    logger.info("Note: Entries will be uploaded without embeddings.")
    logger.info("Text-based search will be available. Add embeddings later when embedding model is deployed.")
    
    # Load entries
    logger.info("Loading RAG entries...")
    entries = load_rag_entries()
    
    if not entries:
        return
    
    logger.info(f"Loaded {len(entries)} entries")
    
    # Prepare entries
    cosmos_entries = prepare_entries_for_cosmos(entries)
    
    # Upload to Cosmos DB
    uploaded, failed = upload_to_cosmos(cosmos_entries)
    
    logger.info(f"\n=== Upload Summary ===")
    logger.info(f"Total entries: {len(entries)}")
    logger.info(f"Successfully uploaded: {uploaded}")
    logger.info(f"Failed: {failed}")
    
    if uploaded > 0:
        logger.info(f"\n✅ Successfully uploaded {uploaded} RAG entries to Cosmos DB!")
        logger.info("Note: To enable vector search, deploy an embedding model and re-run with embeddings")

if __name__ == "__main__":
    main()

