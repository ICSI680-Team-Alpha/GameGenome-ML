# app/services/recommendation.py

import threading
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.game_genre import GameGenre
from app.services.user_genre import UserGenre
from sklearn.neighbors import NearestNeighbors


class RecommendationService:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        """Singleton implementation using __new__"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RecommendationService, cls).__new__(cls)
                # Initialize instance attributes only once
                cls._instance.game_genre_service = GameGenre()
                cls._instance.user_genre_service = UserGenre()
                
                cls._instance.game_ids = None
                cls._instance.recommender = None
                cls._instance.is_trained = False
                cls._instance.normalized_matrix = None
                cls._instance.initialize_model()

                # These will be initialized when needed
                # cls._instance.feature_matrix = None
            return cls._instance

    def initialize_model(self, force_rebuild: bool = False):
        """
        Initialize the recommendation model by loading the game feature matrix and user preferences.
        """
        with self._lock:
            if self.is_trained and not force_rebuild:
                return
        # breakpoint()
        self.game_ids = self.game_genre_service._game_ids
        # Load the normalized game feature matrix
        # self.normalized_matrix = self.game_genre_service.get_genres()
        self.normalized_matrix = self.game_genre_service._normalized_matrix
        self.recommender = NearestNeighbors(metric='cosine')
        self.recommender.fit(self.normalized_matrix)
        self.is_trained = True
        print("Recommendation model initialized.")

    def refresh_model(self) -> None:
        """
        Force a refresh of the recommendation model.
        Useful when new games or user preferences have been added.
        """
        self.is_trained = False
        self.initialize_model(force_rebuild=True)
        print("Recommendation model refreshed.")

    def get_recommendations_for_user(self, userID: int, stationID: int, n_recommendations: int = 5) -> list:
        """
        Get game recommendations for a specific user based on their preferences.
        """
        if not self.is_trained:
            self.initialize_model()

        n2_recommendations = 4 * n_recommendations

        user_vector = self.user_genre_service.get_user_column_vector(userID, stationID)
        
        # TODO Filter out games that the user has already rated
        # Check if user vector is None (user has no valid ratings)
        if user_vector is None:
            # TODO if user has no valid ratings, return trending games or random games
            user_vector = self.user_genre_service.get_user_column_vector(1, 1)
        user_vector_2d = user_vector.reshape(1, -1)
        # breakpoint()
        distances, indices = self.recommender.kneighbors(
            user_vector_2d, 
            n_neighbors=min(n2_recommendations, len(self.game_ids))
        )
        recommended_games = [int(self.game_ids[idx]) for idx in indices[0]]
        # random shuffle recommended_games
        np.random.shuffle(recommended_games)

        return recommended_games[:n_recommendations]