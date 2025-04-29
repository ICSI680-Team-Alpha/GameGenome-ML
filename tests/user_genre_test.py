# test_user_genre.py

import pytest
from unittest.mock import patch, MagicMock, Mock
import pandas as pd
from typing import Dict, Any

from app.services.user_genre import UserGenre
from app.services.genre_vectorizer import GenreVectorizer
from app.core.db import MongoDBSingleton


class TestUserGenre:
    """Test suite for UserGenre class to ensure proper functionality of all methods."""

    @pytest.fixture
    def user_genre(self):
        """Fixture to create a fresh UserGenre instance for each test."""
        return UserGenre()

    @pytest.fixture
    def mock_db_connection(self):
        """Fixture to create a mock database connection."""
        mongo_mock = MagicMock()
        database_mock = MagicMock()
        collection_mock = MagicMock()
        
        mongo_mock.get_database.return_value = database_mock
        database_mock.__getitem__.return_value = collection_mock
        
        with patch('app.services.user_genre.MongoDBSingleton', return_value=mongo_mock):
            yield collection_mock

    @pytest.fixture
    def mock_genre_vectorizer(self):
        """Fixture to create a mock GenreVectorizer.""" 
        vectorizer_mock = MagicMock()
        
        with patch('app.services.user_genre.GenreVectorizer', return_value=vectorizer_mock):
            yield vectorizer_mock

    def test_get_user_vector_success(self, user_genre, mock_db_connection, mock_genre_vectorizer):
        """Test successful retrieval and processing of user vector data."""
        # Arrange
        user_id = 42
        station_id = 7
        mock_rating = {"action": 5, "adventure": 3, "rpg": 4}
        expected_vector = {"genre_vector": {"action": 0.8, "adventure": 0.5, "rpg": 0.7}}
        
        # Setup mocks
        mock_db_connection.find_one.return_value = {"UserID": user_id, "StationID": station_id, "rating": mock_rating}
        mock_genre_vectorizer.vectorize_user_preference.return_value = expected_vector
        
        # Act
        result = user_genre.get_user_column_vector(user_id, station_id)
        
        # Assert
        mock_db_connection.find_one.assert_called_once_with({"UserID": user_id, "StationID": station_id})
        mock_genre_vectorizer.vectorize_user_preference.assert_called_once_with(mock_rating)
        assert result == expected_vector

    def test_get_user_vector_no_rating(self, user_genre, mock_db_connection, mock_genre_vectorizer):
        """Test behavior when user preference exists but has no rating data."""
        # Arrange
        user_id = 42
        station_id = 7
        
        # Setup mocks - return document without rating
        mock_db_connection.find_one.return_value = {"UserID": user_id, "StationID": station_id}
        
        # Act
        with patch('builtins.print') as mock_print:
            result = user_genre.get_user_column_vector(user_id, station_id)
        
        # Assert
        mock_db_connection.find_one.assert_called_once_with({"UserID": user_id, "StationID": station_id})
        mock_genre_vectorizer.vectorize_user_preference.assert_not_called()
        mock_print.assert_called_once()
        assert result is None

    def test_get_user_vector_custom_db_collection(self, user_genre, mock_db_connection, mock_genre_vectorizer):
        """Test using custom database and collection names."""
        # Arrange
        user_id = 42
        station_id = 7
        custom_db = "test_database"
        custom_collection = "test_collection"
        mock_rating = {"strategy": 5, "puzzle": 4}
        expected_vector = {"genre_vector": {"strategy": 0.9, "puzzle": 0.7}}
        
        # Setup mocks
        mock_db_connection.find_one.return_value = {"UserID": user_id, "StationID": station_id, "rating": mock_rating}
        mock_genre_vectorizer.vectorize_user_preference.return_value = expected_vector
        
        # Act
        with patch('app.services.user_genre.MongoDBSingleton') as mock_mongo_singleton:
            mock_mongo = MagicMock()
            mock_db = MagicMock()
            mock_collection = MagicMock()
            
            mock_mongo_singleton.return_value = mock_mongo
            mock_mongo.get_database.return_value = mock_db
            mock_db.__getitem__.return_value = mock_collection
            mock_collection.find_one.return_value = {"UserID": user_id, "StationID": station_id, "rating": mock_rating}
            
            result = user_genre.get_user_column_vector(user_id, station_id, db_name=custom_db, collection_name=custom_collection)
        
        # Assert
        mock_mongo.get_database.assert_called_once_with(custom_db)
        mock_db.__getitem__.assert_called_once_with(custom_collection)
        mock_collection.find_one.assert_called_once_with({"UserID": user_id, "StationID": station_id})
        mock_genre_vectorizer.vectorize_user_preference.assert_called_once_with(mock_rating)
        assert result == expected_vector

    @patch('app.services.user_genre.settings')
    def test_get_user_vector_with_default_settings(self, mock_settings, user_genre, mock_db_connection, mock_genre_vectorizer):
        """Test that default settings from app config are used when not specified."""
        # Arrange
        user_id = 42
        station_id = 7
        mock_settings.DB_NAME = "test_db"
        mock_rating = {"simulation": 3, "sports": 2}
        expected_vector = {"genre_vector": {"simulation": 0.6, "sports": 0.4}}
        
        # Setup mocks
        mock_db_connection.find_one.return_value = {"UserID": user_id, "StationID": station_id, "rating": mock_rating}
        mock_genre_vectorizer.vectorize_user_preference.return_value = expected_vector
        
        # Act
        with patch('app.services.user_genre.MongoDBSingleton') as mock_mongo_singleton:
            mock_mongo = MagicMock()
            mock_db = MagicMock()
            mock_collection = MagicMock()
            
            mock_mongo_singleton.return_value = mock_mongo
            mock_mongo.get_database.return_value = mock_db
            mock_db.__getitem__.return_value = mock_collection
            mock_collection.find_one.return_value = {"UserID": user_id, "StationID": station_id, "rating": mock_rating}
            
            result = user_genre.get_user_column_vector(user_id, station_id)
        
        # Assert
        mock_mongo.get_database.assert_called_once_with("test_db")
        mock_db.__getitem__.assert_called_once_with("game_feedback")
        assert result == expected_vector
        