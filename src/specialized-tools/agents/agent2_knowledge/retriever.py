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
        Performs text-based search on knowledge base.
        Falls back to text search since embeddings may not be available.
        
        Args:
            query: User query text
            top_k: Number of results to return
            
        Returns:
            List of relevant knowledge items with scores
        """
        try:
            container = self.cosmos_client.get_container(
                database_name=self.cosmos_client.database_name,
                container_name=self.container_name
            )
            
            # Try vector search first if embeddings are available
            try:
                query_vector = self.embedding_service.get_embedding(query)
                
                # Vector search query
                query_text = """
                SELECT TOP @top_k
                    c.id,
                    c.content,
                    c.title,
                    c.category,
                    VectorDistance(c.embedding, @queryVector) AS similarity_score
                FROM c
                WHERE IS_DEFINED(c.embedding)
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
                
                formatted_results = []
                for item in results:
                    formatted_results.append({
                        "id": item.get("id"),
                        "title": item.get("title", ""),
                        "content": item.get("content", ""),
                        "category": item.get("category", ""),
                        "similarity_score": item.get("similarity_score", 0.0)
                    })
                
                if formatted_results:
                    logger.info(f"Retrieved {len(formatted_results)} knowledge items using vector search")
                    return formatted_results
                    
            except Exception as vec_error:
                logger.info(f"Vector search not available, using text search: {str(vec_error)}")
            
            # Fallback to text-based search
            query_lower = query.lower()
            query_words = query_lower.split()
            
            # Build text search query
            query_text = f"""
            SELECT TOP @top_k
                c.id,
                c.content,
                c.title,
                c.category
            FROM c
            WHERE CONTAINS(c.searchable_text, @query, true) 
               OR CONTAINS(c.title, @query, true)
               OR CONTAINS(c.content, @query, true)
            """
            
            # Try each query word
            all_results = []
            seen_ids = set()
            
            for word in query_words[:3]:  # Limit to first 3 words
                if len(word) < 3:  # Skip very short words
                    continue
                    
                parameters = [
                    {"name": "@top_k", "value": top_k * 2},  # Get more to filter
                    {"name": "@query", "value": word}
                ]
                
                try:
                    results = container.query_items(
                        query=query_text,
                        parameters=parameters,
                        enable_cross_partition_query=True
                    )
                    
                    for item in results:
                        item_id = item.get("id")
                        if item_id not in seen_ids:
                            seen_ids.add(item_id)
                            all_results.append({
                                "id": item_id,
                                "title": item.get("title", ""),
                                "content": item.get("content", ""),
                                "category": item.get("category", ""),
                                "similarity_score": 1.0  # Text match score
                            })
                except Exception as e:
                    logger.warning(f"Error searching for word '{word}': {str(e)}")
                    continue
            
            # If no results, get general entries
            if not all_results:
                query_text = """
                SELECT TOP @top_k
                    c.id,
                    c.content,
                    c.title,
                    c.category
                FROM c
                """
                parameters = [{"name": "@top_k", "value": top_k}]
                
                results = container.query_items(
                    query=query_text,
                    parameters=parameters,
                    enable_cross_partition_query=True
                )
                
                for item in results:
                    all_results.append({
                        "id": item.get("id"),
                        "title": item.get("title", ""),
                        "content": item.get("content", ""),
                        "category": item.get("category", ""),
                        "similarity_score": 0.5
                    })
            
            # Return top_k results
            formatted_results = all_results[:top_k]
            logger.info(f"Retrieved {len(formatted_results)} knowledge items using text search")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in knowledge retrieval: {str(e)}", exc_info=True)
            # Return empty results on error
            return []

