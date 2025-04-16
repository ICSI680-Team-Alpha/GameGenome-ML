from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional
from app.core.config import settings

class MongoDBSingleton:
    _instance = None
    _client: Optional[MongoClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBSingleton, cls).__new__(cls)
            cls._instance._initialize_client()
        return cls._instance
    
    def _initialize_client(self):
        """Initialize the MongoDB client with connection pooling."""
        # Get connection string from environment variables
        connection_string = settings.DB_CONNECTION_STRING
        
        if not connection_string:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        # Configure connection pooling parameters
        # maxPoolSize: Maximum number of connections in the pool
        # minPoolSize: Minimum number of connections in the pool
        # maxIdleTimeMS: How long a connection can remain idle before being closed
        # waitQueueTimeoutMS: How long a thread will wait for a connection
        self._client = MongoClient(
            connection_string,
            maxPoolSize=100,
            minPoolSize=10,
            maxIdleTimeMS=30000,
            waitQueueTimeoutMS=2000
        )
        
        # Verify connection is successful
        try:
            self._client.admin.command('ping')
            print("MongoDB connection established successfully")
        except ConnectionFailure:
            print("MongoDB connection failed")
            self._client = None
            raise
    
    @property
    def client(self) -> MongoClient:
        """Get the MongoDB client instance."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def get_database(self, db_name: str):
        """Get a specific database."""
        return self.client[db_name]
    
    def close(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            MongoDBSingleton._instance = None
            print("MongoDB connection closed")
            