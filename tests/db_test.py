import pytest
from unittest.mock import patch, MagicMock, call
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

    @patch('app.core.db.MongoClient')
    def test_singleton_pattern(self, mock_mongo_client, reset_singleton):
        """Test that MongoDBSingleton follows the singleton pattern."""
        # Setup mock client
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        
        # Configure the mock to successfully ping
        mock_client_instance.admin.command.return_value = True
        
        # Create two instances and assert they are the same object
        instance1 = MongoDBSingleton()
        instance2 = MongoDBSingleton()
        
        assert instance1 is instance2
        assert id(instance1) == id(instance2)

    @patch('app.core.db.MongoClient')
    def test_initialize_client(self, mock_client, reset_singleton):
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
                    waitQueueTimeoutMS=2000,
                    serverSelectionTimeoutMS=10000,
                    connectTimeoutMS=30000,
                    socketTimeoutMS=45000,
                    retryWrites=True,
                    retryReads=True,
                    heartbeatFrequencyMS=10000
                )
        
        # Verify ping was called
        mock_client_instance.admin.command.assert_called_once_with('ping')
        
        # Verify client is set
        assert db._client is not None
        assert db.client is mock_client_instance

    @patch('app.core.db.MongoClient')
    def test_initialize_client_no_connection_string(self, mock_mongo_client, reset_singleton):
        """Test initialization with missing connection string."""
        # Create a custom settings mock with controlled attribute access
        mock_settings = MagicMock()
        
        # Configure the mock to return None specifically for DB_CONNECTION_STRING
        # This avoids the AttributeError by properly simulating a None value
        mock_settings.DB_CONNECTION_STRING = None
        
        # Patch settings in the module where it's imported and used
        with patch('app.core.db.settings', mock_settings):
            # Now when the code tries to access settings.DB_CONNECTION_STRING,
            # it will get None instead of raising an AttributeError
            with pytest.raises(ValueError, match="MONGODB_URI environment variable is not set"):
                MongoDBSingleton()

    @patch('app.core.db.MongoClient')
    def test_check_connection_success(self, mock_mongo_client, reset_singleton):
        """Test that _check_connection returns True when connection is alive."""
        # Setup mock
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.admin.command.return_value = True
        
        # Create instance
        db = MongoDBSingleton()
        
        # Assert connection check succeeds
        assert db._check_connection() is True
        mock_client.admin.command.assert_called_with('ping')

    @patch('app.core.db.MongoClient')
    def test_check_connection_failure(self, mock_mongo_client, reset_singleton):
        """Test that _check_connection returns False when connection fails."""
        # Setup mock
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        mock_client.admin.command.side_effect = ConnectionFailure("Connection lost")
        
        # Create instance
        db = MongoDBSingleton()
        
        # Reset the side effect to allow initialization
        mock_client.admin.command.side_effect = None
        mock_client.admin.command.return_value = True
        
        # Now set side effect for connection check
        mock_client.admin.command.side_effect = ConnectionFailure("Connection lost")
        
        # Assert connection check fails
        assert db._check_connection() is False

    @patch('app.core.db.MongoClient')
    @patch('app.core.db.time.sleep')
    def test_reconnect_success_after_multiple_attempts(self, mock_sleep, mock_mongo_client, reset_singleton):
        """Test successful reconnection after multiple attempts."""
        # Setup mocks for initialization and reconnection attempts
        mock_clients = [MagicMock() for _ in range(4)]
        mock_mongo_client.side_effect = mock_clients
        
        # Initial client succeeds for initialization
        mock_clients[0].admin.command.return_value = True
        
        # First two reconnection attempts fail
        mock_clients[1].admin.command.side_effect = ConnectionFailure("Attempt 1 failed")
        mock_clients[2].admin.command.side_effect = ConnectionFailure("Attempt 2 failed")
        
        # Third reconnection attempt succeeds
        mock_clients[3].admin.command.return_value = True
        
        # Create instance
        db = MongoDBSingleton()
        
        # Save original max reconnect attempts value and override for test
        original_max_attempts = db._max_reconnect_attempts
        db._max_reconnect_attempts = 5
        
        # Simulate a connection failure before reconnect
        mock_clients[0].admin.command.side_effect = ConnectionFailure("Connection lost")
        
        # Call reconnect
        result = db._reconnect()
        
        # Assert reconnect was successful
        assert result is True
        assert mock_mongo_client.call_count == 4
        assert db._client is mock_clients[3]
        
        # Sleep should be called twice (after first and second failed attempts)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_has_calls([call(db._reconnect_delay_seconds), call(db._reconnect_delay_seconds)])
        
        # Restore original value
        db._max_reconnect_attempts = original_max_attempts

    @patch('app.core.db.MongoClient')
    @patch('app.core.db.time.sleep')
    def test_reconnect_all_attempts_fail(self, mock_sleep, mock_mongo_client, reset_singleton):
        """Test when all reconnection attempts fail."""
        # Setup mocks for initialization and reconnection attempts
        mock_clients = [MagicMock() for _ in range(6)]
        mock_mongo_client.side_effect = mock_clients
        
        # Initial client succeeds for initialization
        mock_clients[0].admin.command.return_value = True
        
        # All reconnection attempts fail
        for i in range(1, 6):
            mock_clients[i].admin.command.side_effect = ConnectionFailure(f"Attempt {i} failed")
        
        # Create instance
        db = MongoDBSingleton()
        
        # Save original max reconnect attempts value and override for test
        original_max_attempts = db._max_reconnect_attempts
        db._max_reconnect_attempts = 5
        
        # Simulate a connection failure before reconnect
        mock_clients[0].admin.command.side_effect = ConnectionFailure("Connection lost")
        
        # Call reconnect
        result = db._reconnect()
        
        # Assert reconnect failed
        assert result is False
        assert mock_mongo_client.call_count == 6  # 1 initial + 5 retry attempts
        
        # Sleep should be called 4 times (after each failed attempt except the last)
        assert mock_sleep.call_count == 4
        mock_sleep.assert_has_calls([call(db._reconnect_delay_seconds)] * 4)
        
        # Restore original value
        db._max_reconnect_attempts = original_max_attempts

    @patch('app.core.db.MongoClient')
    def test_get_client(self, mock_mongo_client, reset_singleton):
        """Test that client property returns the MongoDB client."""
        # Mock the MongoClient instance
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # Create a singleton instance
        instance = MongoDBSingleton()
        
        # Assert client property returns the mock client
        assert instance.client is mock_client

    @patch('app.core.db.MongoClient')
    def test_get_database(self, mock_mongo_client, reset_singleton):
        """Test that get_database returns the correct database."""
        # Mock the MongoClient instance
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # Mock the database access using dictionary-style access
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        # Create a singleton instance
        instance = MongoDBSingleton()
        
        # Get a database and assert it's the mock database
        db = instance.get_database("test_db")
        assert db is mock_db
        mock_client.__getitem__.assert_called_once_with("test_db")

    @patch('app.core.db.MongoClient')
    def test_close_connection(self, mock_mongo_client, reset_singleton):
        """Test closing the MongoDB connection."""
        # Mock the MongoClient instance
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        # Create a singleton instance and then close it
        instance = MongoDBSingleton()
        instance.close()
        
        # Assert close was called on the client
        mock_client.close.assert_called_once()
        
        # Assert instance and client were reset
        assert MongoDBSingleton._instance is None
        assert instance._client is None

    @patch('app.core.db.MongoClient')
    def test_reinitialize_after_close(self, mock_mongo_client, reset_singleton):
        """Test that client is reinitialized after closing."""
        # Mock the MongoClient instance
        mock_client1 = MagicMock()
        mock_client2 = MagicMock()
        mock_mongo_client.side_effect = [mock_client1, mock_client2]
        
        # Create a singleton instance and then close it
        instance1 = MongoDBSingleton()
        instance1.close()
        
        # Create a new instance after closing
        instance2 = MongoDBSingleton()
        
        # Assert MongoClient was called twice (once for each initialization)
        assert mock_mongo_client.call_count == 2
        
        # Assert the new instance has a new client
        assert instance2.client is mock_client2