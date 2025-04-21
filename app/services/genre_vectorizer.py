# app/services/genre_vectorizer.py

import numpy as np
from typing import List, Dict, Any, Union
import pandas as pd

class GenreVectorizer:
    """
    Service for vectorizing game and user genre data.
    This class handles the transformation of raw genre data into feature vectors
    that can be used by the recommendation system.
    """
    
    def __init__(self):
        # self.game_genre_service = GameGenre()
        # self.user_genre_service = UserGenre()
        self.genre_list = None
    
    def vectorize_game(self, game_data: List) -> np.ndarray:
        """
        Convert a game's genre data from Cursor into a feature vector.
        
        Args:
            game_data: Game data retrieved from database in Cursor format
            
        Returns:
            A numpy array representing the vectorized game genres
        """
        df = pd.DataFrame(game_data)
        
        # df.drop(columns=['_id'], inplace=True, errors='ignore')
        
        if df is None or df.empty:
            print("Error: No genre data available")
        
        genre_list = set()
        genre_dict = df.iloc[0]['genre']
        genre_list.update(genre_dict.keys())

        
        genre_matrix = pd.DataFrame(genre_dict, index=df.index)
        ## TODO Double check if the AppID is necessary
        genre_matrix['AppID'] = df['AppID']
        return genre_matrix
    
    def vectorize_user_preference(self, user_preference: Dict[str, Any]) -> np.ndarray:
        """
        Convert user preference data into a feature vector.
        
        Args:
            user_preference: User preference data from database
            
        Returns:
            A numpy array representing the vectorized user preferences
        """
        
        return ...
    
    def build_game_feature_matrix(self, game_data) -> tuple:
        """
        Build a feature matrix for all games in the database.
        
        Returns:
            A tuple containing (game_ids, feature_matrix)
            - game_ids: List of game IDs
            - feature_matrix: Numpy array where each row corresponds to a game's feature vector
        """
        if game_data is None or game_data.empty:
            print("Error: No genre data available")
            return None, None
        # check game_data have AppID column
        if 'AppID' not in game_data.columns:
            print("Error: AppID column is missing")
            return None, None
        game_ids = game_data['AppID'].to_numpy()
        feature_matrix = game_data.drop(columns='AppID').to_numpy()
        
        return game_ids, feature_matrix
    
    def normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """
        Normalize feature vectors to have unit norm (for cosine similarity).
        
        Args:
            vectors: Input feature vectors
            
        Returns:
            Normalized feature vectors
        """
        # Avoid division by zero by adding a small epsilon to zero vectors
        norms = np.linalg.norm(vectors, axis=1)
        norms[norms == 0] = 1e-10
        
        # Normalize by dividing by the norm
        normalized_vectors = vectors / norms[:, np.newaxis]
        
        return normalized_vectors