import pytest
import os
from app.services.recommendation import RecommendationService

@pytest.mark.skipif(
    os.environ.get('CI') == 'true',
    reason="Local test only - skip in CI environment"
)
class TestRecommendationService:
    """Test class for RecommendationService."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Automatically used fixture to set up the recommendation service."""
        self.recommendation_service = RecommendationService()
        self.recommendation_service.refresh_model()

    
    def test_get_recommendations_for_user(self):
        """Test that get_recommendations_for_user returns 5 recommendations."""
        userID = 1
        stationID = 1

        recommendations = self.recommendation_service.get_recommendations_for_user(userID, stationID)

        assert len(recommendations) == 5, f"Expected 5 recommendations, but got {len(recommendations)}"
    
    def test_get_recommendations_for_user_return_five(self):
        """Test that get_recommendations_for_user returns 5 recommendations."""
        userID = 1
        stationID = 1
        n_recommendations = 5

        recommendations = self.recommendation_service.get_recommendations_for_user(userID, stationID, n_recommendations)

        assert len(recommendations) == n_recommendations, f"Expected {n_recommendations} recommendations, but got {len(recommendations)}"
    
    def test_get_recommendations_for_user_return_three(self):
        """Test that get_recommendations_for_user returns 5 recommendations."""
        userID = 1
        stationID = 1
        n_recommendations = 3

        recommendations = self.recommendation_service.get_recommendations_for_user(userID, stationID, n_recommendations)

        assert len(recommendations) == n_recommendations, f"Expected {n_recommendations} recommendations, but got {len(recommendations)}"