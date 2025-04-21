# app/services/game_genre.py

import pandas as pd
from typing import List, Dict, Any
from app.core.db import MongoDBSingleton
from app.core.config import settings
from app.services.genre_vectorizer import GenreVectorizer


class GameGenre:
    _instance = None
    _genre_cache = None
    _game_ids = None
    _feature_matrix = None
    _normalized_matrix = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameGenre, cls).__new__(cls)
            print(f"Loading game genres...")
            cls._genre_cache, cls._game_ids, cls._feature_matrix, cls._normalized_matrix = cls._instance.get_genres()
            print(f"Game genres loaded and cached.") 
        return cls._instance
    

    def get_genres(self, db_name: str = settings.DB_NAME, collection_name: str = "steam_genre") -> List:
        """Get and cache game genres."""
        if self._genre_cache is not None:
            return self._genre_cache
        mongo = MongoDBSingleton()
        database = mongo.get_database(db_name)
        collection = database[collection_name]

        all_genres = collection.find({}, {"_id": 0}).sort("AppID", 1)
        
        genreVectorizer = GenreVectorizer()
        df = genreVectorizer.vectorize_game(all_genres)
        if df is None or df.empty:
            print("Error: No genre data available")
            return None
        game_ids, feature_matrix = genreVectorizer.build_game_feature_matrix(df)
        normalized_matrix = genreVectorizer.normalize_matrix(feature_matrix)
        return df, game_ids, feature_matrix, normalized_matrix
    

    def get_multiple_genres(self, appID_list: List[int], db_name: str = settings.DB_NAME, collection_name: str = "steam_genre") -> List:
        """Get multiple genres by their IDs."""
        if appID_list is None:
            return {}

        mongo = MongoDBSingleton()
        database = mongo.get_database(db_name)
        collection = database[collection_name]

        # Query for documents where AppID is in the provided list
        genres = collection.find({"AppID": {"$in": appID_list}}, {"_id": 0}).sort("AppID", 1)
        print(f"Game genres loaded from {db_name}.{collection_name} for AppIDs: {appID_list}.")

        return genres