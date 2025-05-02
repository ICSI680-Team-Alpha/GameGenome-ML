# app/services/user_genre.py

import pandas as pd
from typing import List, Dict, Any
from app.core.db import MongoDBSingleton
from app.core.config import settings
from app.services.genre_vectorizer import GenreVectorizer


class UserGenre:    
    def __init__(self):
        user_preference = None
        self.rating = None
        self.genre_vectorizer_service = GenreVectorizer()

    def load_ratings(self, userID: int, stationID: int, db_name: str = settings.DB_NAME, collection_name: str = "game_feedback") -> bool:
        """Load user ratings from the database."""
        mongo = MongoDBSingleton()
        database = mongo.get_database(db_name)
        collection = database[collection_name]

        user_preference = collection.find_one({"UserID": userID, "StationID": stationID})
        if user_preference is None:
            ## TODO suppose to raise an exception, but for now just print the error message and return use default ratings
            user_preference = collection.find_one({"UserID": 1, "StationID": 1})
            # return None

        self.rating = user_preference.get("rating", None)
        if self.rating is None:
            
            ## TODO suppose to raise an exception, but for now just print the error message and return use default ratings
            user_preference = collection.find_one({"UserID": 1, "StationID": 1})
            self.rating = user_preference.get("rating", None)
            if self.rating is None:
                print(f"Error: No user preference data available for UserID: 1, StationID: 1")
                return False
            # TODO return None

        return True
    
    def get_user_column_vector(self) -> Dict[int, Dict[str, int]]:
        """Get and cache game genres."""
        user_vector = self.genre_vectorizer_service.vectorize_user_preference(self.rating)
        return user_vector
    
    def get_rated_geme_list(self):
        if self.rating is None:
            print("Error: No rating data available. Call load_ratings first.")
            return []
        
        # extract AppID from user
        # if unsuccessful, raise an exception
        try:
            return [int(rating.get("AppID")) for rating in self.rating]
        except ValueError as e:
            raise ValueError(f"Invalid game ID in rating data: {e}")