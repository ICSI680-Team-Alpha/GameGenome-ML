# app/services/user_genre.py

import pandas as pd
from typing import List, Dict, Any
from app.core.db import MongoDBSingleton
from app.core.config import settings
from app.services.genre_vectorizer import GenreVectorizer


class UserGenre:    
    def __init__(self):
        pass
    
    def get_user_column_vector(self, userID: int, stationID: int, db_name: str = settings.DB_NAME, collection_name: str = "game_feedback") -> Dict[int, Dict[str, int]]:
        """Get and cache game genres."""
        mongo = MongoDBSingleton()
        database = mongo.get_database(db_name)
        collection = database[collection_name]

        user_preference = collection.find_one({"UserID": userID, "StationID": stationID})
        if user_preference is None:
            print(f"Error: No user preference data available for UserID: {userID}, StationID: {stationID}")
            return None

        rating = user_preference.get("rating", None)
        if rating is None:
            print(f"Error: No user preference data available for UserID: {userID}, StationID: {stationID}")
            return None

        genre_vectorizer_service = GenreVectorizer()
        user_vector = genre_vectorizer_service.vectorize_user_preference(rating)
        return user_vector
    
    