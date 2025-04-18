# app/services/game_genre.py

import pandas as pd
from typing import List, Dict, Any
from app.core.db import MongoDBSingleton
from app.core.config import settings

class GameGenre:
    _instance = None
    _genre_cache = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameGenre, cls).__new__(cls)
        return cls._instance
    

    def get_genres(self, db_name: str = settings.DB_NAME, collection_name: str = "steam_genre") -> Dict[int, Dict[str, int]]:
        """Get and cache game genres."""
        if self._genre_cache is None:
            mongo = MongoDBSingleton()
            database = mongo.get_database(db_name)
            collection = database[collection_name]

            all_genres = collection.find({}, {"_id": 0})
            
            self._genre_cache = all_genres        
        return self._genre_cache
    

    def get_multiple_genre(self, appID_list: List[int], db_name: str = settings.DB_NAME, collection_name: str = "steam_genre") -> Dict[int, Dict[str, Any]]:
        """Get multiple genres by their IDs."""
        mongo = MongoDBSingleton()
        database = mongo.get_database(db_name)
        collection = database[collection_name]

        # Query for documents where AppID is in the provided list
        genres = collection.find({"AppID": {"$in": appID_list}})
        
        # Convert cursor to dictionary with AppID as key
        result = {}
        for genre in genres:
            app_id = genre.get("AppID")
            if app_id:
                result[app_id] = genre
        
        return result
    
    ## TODO : Add a method to convert Genre to DataFrame
    # def convert_genre_to_dataframe(self, genres: Dict[int, Dict[str, int]]) -> pd.DataFrame:
    #     """Convert the genre dictionary to a DataFrame."""
    #     df = pd.DataFrame.from_dict(genres, orient='index')
    #     return df.reset_index(drop=True) if not df.empty else pd.DataFrame()
    