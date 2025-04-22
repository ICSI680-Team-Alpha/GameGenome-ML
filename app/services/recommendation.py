# app/services/recommendation.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.game_genre import GameGenre
from app.services.user_genre import UserGenre
from sklearn.neighbors import NearestNeighbors


class RecommendationService:
    def __init__(self):
        self.game_genre_service = GameGenre()
        self.user_genre_service = UserGenre()
        self.game_ids = self.game_genre_service._game_ids
        self.normalized_matrix = self.game_genre_service._normalized_matrix
        self.recommender = None
        self.is_trained = False
        self.init_model()

    def init_model(self, force_rebuild: bool = False):
        """
        Initialize the recommendation model by loading the game feature matrix and user preferences.
        """
        if self.is_trained and not force_rebuild:
            return        
        self.recommender = NearestNeighbors(metric='cosine')
        self.recommender.fit(self.normalized_matrix)


    def get_recommendations_for_user(self, userID: int, stationID: int, n_recommendations: int = 5) -> list:
        """
        Get game recommendations for a specific user based on their preferences.
        """
        self.user_genre_service.get_user_vector(userID, stationID)
        