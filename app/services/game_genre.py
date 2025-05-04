# app/services/game_genre.py

import threading
import numpy as np
from app.core.db import MongoDBSingleton
from app.core.config import settings
from typing import Dict, Any, Optional
import time
import sys

class GameGenre:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        """Singleton implementation using __new__"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(GameGenre, cls).__new__(cls)
                # Initialize instance attributes only once
                cls._instance._genres = None
                cls._instance._game_ids = None
                cls._instance._normalized_matrix = None
                cls._instance._is_loading = False
                
                try:
                    cls._instance._load_game_genres()
                except Exception as e:
                    print(f"Warning: Failed to load game genres: {e}")
                    # Set minimal fallback data
                    cls._instance._genres = []
                    cls._instance._game_ids = []
                    cls._instance._normalized_matrix = np.array([])
                    
            return cls._instance
    
    def _load_game_genres(self, max_documents: int = 10000, timeout: int = 30):
        """Load game genres from the database with memory optimization and timeouts."""
        with self._lock:
            if self._is_loading:
                return
            
            self._is_loading = True
            start_time = time.time()
            
            try:
                print(f"Loading game genres with timeout: {timeout}s...")
                
                mongo = MongoDBSingleton()
                database = mongo.get_database(settings.DB_NAME)
                collection = database["steam_genre"]
                
                # Query with limit and batch processing
                batch_size = 1000
                documents = []
                
                cursor = collection.find().limit(max_documents)
                batch = []
                
                for doc in cursor:
                    batch.append(doc)
                    
                    if len(batch) >= batch_size:
                        documents.extend(batch)
                        batch = []
                        
                        # Check timeout
                        if time.time() - start_time > timeout:
                            print(f"Warning: Timeout reached after {timeout}s. Loaded {len(documents)} documents.")
                            break
                        
                        # Give other threads a chance
                        time.sleep(0.01)
                
                # Add remaining documents
                documents.extend(batch)
                
                print(f"Loaded {len(documents)} documents in {time.time() - start_time:.2f}s")
                
                if not documents:
                    print("No documents found in steam_genre collection")
                    return
                
                # Extract and process data
                self._extract_data(documents)
                
                print("Game genres loaded and cached.")
                
            except Exception as e:
                print(f"Error loading game genres: {e}")
                raise
            finally:
                self._is_loading = False
    
    def _extract_data(self, documents):
        """Extract and process data from documents."""
        genres = []
        game_ids = []
        
        for doc in documents:
            try:
                if "AppID" in doc and "genre" in doc:
                    genres.append(doc["genre"])
                    game_ids.append(doc["AppID"])
            except Exception as e:
                print(f"Error processing document: {e}")
                continue
        
        self._genres = genres
        self._game_ids = game_ids
        
        # Convert genres to matrix (memory efficient)
        if genres:
            self._normalized_matrix = self._convert_to_normalized_matrix(genres)
        else:
            self._normalized_matrix = np.array([])
    
    def _convert_to_normalized_matrix(self, genres) -> np.ndarray:
        """Convert genre dictionaries to normalized matrix efficiently."""
        # Get all unique genre keys
        all_keys = set()
        for genre_dict in genres:
            all_keys.update(genre_dict.keys())
        
        all_keys = sorted(list(all_keys))
        
        # Create matrix
        matrix = np.zeros((len(genres), len(all_keys)))
        
        for i, genre_dict in enumerate(genres):
            for j, key in enumerate(all_keys):
                if key in genre_dict:
                    matrix[i, j] = genre_dict[key]
        
        # Normalize rows
        row_sums = matrix.sum(axis=1)
        normalized_matrix = matrix / row_sums[:, np.newaxis]
        
        return normalized_matrix
    
    def get_normalized_matrix(self) -> np.ndarray:
        """Get the normalized genre matrix."""
        if self._normalized_matrix is None:
            # Try to reload if not loaded
            self._load_game_genres()
        
        return self._normalized_matrix
    
    def get_genres(self) -> list:
        """Get the raw genre data."""
        if self._genres is None:
            # Try to reload if not loaded
            self._load_game_genres()
        
        return self._genres
    
    def reload(self, max_documents: int = 10000, timeout: int = 30):
        """Reload game genres with custom parameters."""
        self._genres = None
        self._game_ids = None
        self._normalized_matrix = None
        self._load_game_genres(max_documents, timeout)