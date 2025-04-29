import pytest
import numpy as np
from unittest.mock import Mock, patch
import os
from app.services.recommendation import RecommendationService
from app.services.game_genre import GameGenre
from app.services.user_genre import UserGenre

@pytest.mark.skipif(
    os.environ.get('CI') == 'true',
    reason="Local test only - skip in CI environment"
)
def test_get_recommendations_for_user_returns_five_recommendations(monkeypatch):
    """
    Test that get_recommendations_for_user returns 5 recommendations when called with (1, 1).
    This test is skipped in CI environments.
    """
    # Mock the dependencies
    mock_game_genre = Mock(spec=GameGenre)
    mock_game_genre._game_ids = np.array([101, 102, 103, 104, 105, 106, 107, 108, 109, 110])
    mock_game_genre._normalized_matrix = np.random.rand(10, 15)  # Random feature matrix
    
    mock_user_genre = Mock(spec=UserGenre)
    mock_user_genre.get_user_column_vector.return_value = np.random.rand(15)  # Random user vector
    
    # Mock the NearestNeighbors
    mock_recommender = Mock()
    mock_recommender.kneighbors.return_value = (
        np.array([[0.1, 0.2, 0.3, 0.4, 0.5]]),  # Distances
        np.array([[0, 1, 2, 3, 4]])  # Indices
    )
    
    # Patch the RecommendationService initialization
    def mock_new(cls, *args, **kwargs):
        if not hasattr(cls, '_mocked_instance'):
            cls._mocked_instance = object.__new__(cls)
            cls._mocked_instance.game_genre_service = mock_game_genre
            cls._mocked_instance.user_genre_service = mock_user_genre
            cls._mocked_instance.game_ids = mock_game_genre._game_ids
            cls._mocked_instance.normalized_matrix = mock_game_genre._normalized_matrix
            cls._mocked_instance.recommender = mock_recommender
            cls._mocked_instance.is_trained = True
        return cls._mocked_instance
    
    # Apply the patch
    monkeypatch.setattr(RecommendationService, '__new__', mock_new)
    
    # Create our service (will use the mocked dependencies)
    recommendation_service = RecommendationService()
    
    # Set up the mock to return consistent results
    np.random.seed(42)  # For reproducible shuffle behavior
    
    # Act
    result = recommendation_service.get_recommendations_for_user(1, 1)
    
    # Assert
    assert len(result) == 5, f"Expected 5 recommendations, but got {len(result)}"