# app/services/genre_service.py

import pandas as pd
from typing import List, Dict, Any
from app.core.db import MongoDBSingleton
from app.core.config import settings

class UserGenre:    
    def __init__(self):
        pass
    
    def get_user_preference(self, userID: str, stationID: str, db_name: str = settings.DB_NAME, collection_name: str = "game_feedback") -> Dict[int, Dict[str, int]]:
        """Get and cache game genres."""
        mongo = MongoDBSingleton()
        database = mongo.get_database(db_name)
        collection = database[collection_name]

        user_preference = collection.find_one({"UserID": userID, "StationID": stationID})
        return user_preference
    

    def vectorize_user_preference(self, user_preference: Dict[str, Any]) -> Dict[str, int]:
        """Vectorize user preference."""
        if not user_preference:
            return {}
        
        # Assuming user_preference is a dictionary with keys as genre names and values as ratings
        vectorized = {}
    ## TODO : Add a method to convert user preference to DataFrame
    