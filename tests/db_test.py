import pytest
from unittest.mock import patch, MagicMock
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from app.core.config import settings
from app.core.db import MongoDBSingleton


class TestMongoDBSingleton:
    """Test suite for the MongoDBSingleton class."""

    @pytest.fixture
    def reset_singleton(self):
        """Reset the singleton instance before and after each test."""
        # Reset before test
        MongoDBSingleton._instance = None
        MongoDBSingleton._client = None
        
        # Run the test
        yield
        
        # Reset after test
        MongoDBSingleton._instance = None
        MongoDBSingleton._client = None

    def test_singleton_pattern(self, reset_singleton):
        """Test that MongoDBSingleton follows the singleton pattern."""
        # Create two instances and assert they are the same object
        instance1 = MongoDBSingleton()
        instance2 = MongoDBSingleton()
        
        assert instance1 is instance2
        assert id(instance1) == id(instance2)

    @patch('app.core.db.MongoClient')
    def test_initialize_client(self, mock_client):
        """Test that the client is initialized with correct parameters."""
         # Setup mock
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.admin.command.return_value = True
        
        # Initialize singleton
        db = MongoDBSingleton()
        
        # Verify MongoClient was called with correct parameters
        mock_client.assert_called_once_with(
            settings.DB_CONNECTION_STRING,
            maxPoolSize=100,
            minPoolSize=10,
            maxIdleTimeMS=30000,
            waitQueueTimeoutMS=2000
        )
        
        # Verify ping was called
        mock_client_instance.admin.command.assert_called_once_with('ping')
        
        # Verify client is set
        assert db._client is not None
        assert db.client is mock_client_instance

    # @patch('app.core.db.MongoClient')
    # def test_initialize_client_no_connection_string(self, mock_mongo_client):
    #     """Test initialization with missing connection string."""
    #     # Temporarily modify settings to simulate missing connection string
    #     with patch('app.core.config.settings.DB_CONNECTION_STRING', None):
    #         # Reset the singleton to ensure it initializes again
    #         MongoDBSingleton._instance = None
    #         MongoDBSingleton._client = None
            
    #         # Assert it raises a ValueError
    #         with pytest.raises(ValueError, match="MONGODB_URI environment variable is not set"):
    #             MongoDBSingleton()

    # @patch('app.core.db.MongoClient')
    # def test_initialize_client_connection_failure(self, mock_mongo_client):
    #     """Test initialization with connection failure."""
    #     # Mock the MongoClient instance
    #     mock_client = MagicMock()
    #     mock_mongo_client.return_value = mock_client
        
    #     # Mock ping command to raise ConnectionFailure
    #     mock_admin = MagicMock()
    #     mock_client.admin = mock_admin
    #     mock_admin.command.side_effect = ConnectionFailure("Connection failed")
        
    #     # Reset the singleton to ensure it initializes again
    #     MongoDBSingleton._instance = None
    #     MongoDBSingleton._client = None
        
    #     # Assert it raises a ConnectionFailure
    #     with pytest.raises(ConnectionFailure, match="Connection failed"):
    #         MongoDBSingleton()

    # @patch('app.core.db.MongoClient')
    # def test_get_client(self, mock_mongo_client):
    #     """Test that client property returns the MongoDB client."""
    #     # Mock the MongoClient instance
    #     mock_client = MagicMock()
    #     mock_mongo_client.return_value = mock_client
        
    #     # Create a singleton instance
    #     instance = MongoDBSingleton()
        
    #     # Assert client property returns the mock client
    #     assert instance.client is mock_client

    # @patch('app.core.db.MongoClient')
    # def test_get_database(self, mock_mongo_client):
    #     """Test that get_database returns the correct database."""
    #     # Mock the MongoClient instance
    #     mock_client = MagicMock()
    #     mock_mongo_client.return_value = mock_client
        
    #     # Mock the database access using dictionary-style access
    #     mock_db = MagicMock()
    #     mock_client.__getitem__.return_value = mock_db
        
    #     # Create a singleton instance
    #     instance = MongoDBSingleton()
        
    #     # Get a database and assert it's the mock database
    #     db = instance.get_database("test_db")
    #     assert db is mock_db
    #     mock_client.__getitem__.assert_called_once_with("test_db")

    # @patch('app.core.db.MongoClient')
    # def test_close_connection(self, mock_mongo_client):
    #     """Test closing the MongoDB connection."""
    #     # Mock the MongoClient instance
    #     mock_client = MagicMock()
    #     mock_mongo_client.return_value = mock_client
        
    #     # Create a singleton instance and then close it
    #     instance = MongoDBSingleton()
    #     instance.close()
        
    #     # Assert close was called on the client
    #     mock_client.close.assert_called_once()
        
    #     # Assert instance and client were reset
    #     assert MongoDBSingleton._instance is None
    #     assert instance._client is None

    # @patch('app.core.db.MongoClient')
    # def test_reinitialize_after_close(self, mock_mongo_client):
    #     """Test that client is reinitialized after closing."""
    #     # Mock the MongoClient instance
    #     mock_client1 = MagicMock()
    #     mock_client2 = MagicMock()
    #     mock_mongo_client.side_effect = [mock_client1, mock_client2]
        
    #     # Create a singleton instance and then close it
    #     instance1 = MongoDBSingleton()
    #     instance1.close()
        
    #     # Create a new instance after closing
    #     instance2 = MongoDBSingleton()
        
    #     # Assert MongoClient was called twice (once for each initialization)
    #     assert mock_mongo_client.call_count == 2
        
    #     # Assert the new instance has a new client
    #     assert instance2.client is mock_client2