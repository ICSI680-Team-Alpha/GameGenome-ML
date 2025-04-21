# app/services/recommendation.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.services.game_genre import GameGenre
from app.services.user_genre import UserGenre
from sklearn.neighbors import NearestNeighbors


class RecommendationService:
    def __init__(self):
        self.game_genre = GameGenre()
        self.user_genre_service = UserGenre()
        self.game_ids = self.game_genre._game_ids
        self.normalized_matrix = self.game_genre._normalized_matrix
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
        self.recommender.fit(self.normalized_features)