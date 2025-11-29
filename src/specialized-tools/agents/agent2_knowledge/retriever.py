"""
Agent 2: Knowledge Retrieval Agent
Executes vector search on Cosmos DB KnowledgeVectors container.
"""
import os
import logging
from typing import List, Dict, Any
import sys

# Add shared-db to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared-db'))

from cosmos_client import CosmosClient
from embedding_service import EmbeddingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """
    Retrieves relevant medical knowledge using vector search.
    """
    
    def __init__(self):
        """Initialize Cosmos DB client and embedding service."""
        self.cosmos_client = CosmosClient()
        self.embedding_service = EmbeddingService()
        # Support both naming conventions
        self.container_name = os.getenv(
            "COSMOS_DB_KNOWLEDGE_CONTAINER"
        ) or os.getenv(
            "AZURE_COSMOSDB_KNOWLEDGE_CONTAINER",
            "KnowledgeVectors"
        )
        
        logger.info("KnowledgeRetriever initialized")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Performs vector search on knowledge base.
        
        Args:
            query: User query text
            top_k: Number of results to return
            
        Returns:
            List of relevant knowledge items with scores
        """
        try:
            # Convert query to vector
            query_vector = self.embedding_service.get_embedding(query)
            
            # Perform vector search in Cosmos DB
            container = self.cosmos_client.get_container(
                database_name=self.cosmos_client.database_name,
                container_name=self.container_name
            )
            
            # Cosmos DB vector search query
            # Note: This assumes you have a vector index on the 'embedding' field
            query_text = """
            SELECT TOP @top_k
                c.id,
                c.content,
                c.title,
                c.category,
                VectorDistance(c.embedding, @queryVector) AS similarity_score
            FROM c
            ORDER BY VectorDistance(c.embedding, @queryVector)
            """
            
            parameters = [
                {"name": "@top_k", "value": top_k},
                {"name": "@queryVector", "value": query_vector}
            ]
            
            results = container.query_items(
                query=query_text,
                parameters=parameters,
                enable_cross_partition_query=True
            )
            
            # Convert to list and format
            formatted_results = []
            for item in results:
                formatted_results.append({
                    "id": item.get("id"),
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "category": item.get("category", ""),
                    "similarity_score": item.get("similarity_score", 0.0)
                })
            
            logger.info(f"Retrieved {len(formatted_results)} knowledge items")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in knowledge retrieval: {str(e)}", exc_info=True)
            # Return empty results on error
            return []

