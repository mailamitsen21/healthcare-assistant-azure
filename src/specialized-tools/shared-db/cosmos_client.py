"""
Cosmos DB Client
Centralized Cosmos DB initialization and connection management.
"""
import os
import logging
from azure.cosmos import CosmosClient as AzureCosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CosmosClient:
    """
    Centralized Cosmos DB client for all agents.
    Manages connections and provides container access.
    """
    
    def __init__(self):
        """Initialize Cosmos DB client with connection details."""
        # Support both naming conventions
        endpoint = os.getenv("COSMOS_DB_ENDPOINT") or os.getenv("AZURE_COSMOSDB_ENDPOINT")
        key = os.getenv("COSMOS_DB_KEY") or os.getenv("AZURE_COSMOSDB_KEY")
        database_name = os.getenv("AZURE_COSMOSDB_DATABASE_NAME", "HealthcareDB")
        
        if not endpoint or not key:
            raise ValueError(
                "COSMOS_DB_ENDPOINT (or AZURE_COSMOSDB_ENDPOINT) and COSMOS_DB_KEY (or AZURE_COSMOSDB_KEY) must be set"
            )
        
        self.client = AzureCosmosClient(endpoint, key)
        self.database_name = database_name
        
        # Ensure database exists
        self._ensure_database_exists()
        
        logger.info(f"CosmosClient initialized for database: {database_name}")
    
    def _ensure_database_exists(self):
        """Creates the database if it doesn't exist."""
        try:
            self.client.create_database_if_not_exists(id=self.database_name)
            logger.info(f"Database '{self.database_name}' ready")
        except Exception as e:
            logger.error(f"Error ensuring database exists: {str(e)}")
            raise
    
    def get_container(
        self,
        database_name: str,
        container_name: str,
        partition_key: str = "/id"
    ):
        """
        Gets or creates a container.
        
        Args:
            database_name: Name of the database
            container_name: Name of the container
            partition_key: Partition key path (default: /id)
            
        Returns:
            Container object
        """
        try:
            database = self.client.get_database_client(database_name)
            
            # Try to get existing container
            try:
                container = database.get_container_client(container_name)
                # Test if container exists by trying to read its properties
                container.read()
                return container
            except CosmosResourceNotFoundError:
                # Container doesn't exist, create it
                logger.info(f"Creating container: {container_name}")
                container = database.create_container(
                    id=container_name,
                    partition_key=PartitionKey(path=partition_key),
                    offer_throughput=400
                )
                return container
                
        except Exception as e:
            logger.error(f"Error getting container {container_name}: {str(e)}")
            raise
    
    def create_container_if_not_exists(
        self,
        container_name: str,
        partition_key: str = "/id"
    ):
        """
        Creates a container if it doesn't exist.
        
        Args:
            container_name: Name of the container
            partition_key: Partition key path
        """
        try:
            self.get_container(self.database_name, container_name, partition_key)
        except Exception as e:
            logger.error(f"Error creating container: {str(e)}")
            raise

