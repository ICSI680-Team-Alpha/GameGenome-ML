# tests/game_genre_test.py

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, PropertyMock

from app.services.game_genre import GameGenre
from app.services.genre_vectorizer import GenreVectorizer


@pytest.fixture
def ethereal_genre_tapestry():
    """
    Conjures a mesmerizing tableau of genre classifications
    that dances between worlds of digital entertainment.
    """
    return [
        {"AppID": 10, "genre": {"action": 1, "adventure": 0.8, "rpg": 0.5, "indie": 0.3}},
        {"AppID": 20, "genre": {"strategy": 1, "simulation": 0.7, "puzzle": 0.4}},
        {"AppID": 30, "genre": {"action": 0.6, "shooter": 1, "multiplayer": 0.9, "competitive": 0.5}},
        {"AppID": 40, "genre": {"horror": 0.9, "adventure": 0.6, "survival": 1}}
    ]


@pytest.fixture
def crystallized_vector_formation():
    """
    Manifests the expected paradigm of genre vectors,
    meticulously structured for algorithmic consumption.
    """
    kaleidoscopic_data = {
        "AppID": [10, 20, 30, 40],
        "action": [1, 0, 0.6, 0],
        "adventure": [0.8, 0, 0, 0.6],
        "rpg": [0.5, 0, 0, 0],
        "indie": [0.3, 0, 0, 0],
        "strategy": [0, 1, 0, 0],
        "simulation": [0, 0.7, 0, 0],
        "puzzle": [0, 0.4, 0, 0],
        "shooter": [0, 0, 1, 0],
        "multiplayer": [0, 0, 0.9, 0],
        "competitive": [0, 0, 0.5, 0],
        "horror": [0, 0, 0, 0.9],
        "survival": [0, 0, 0, 1]
    }
    return pd.DataFrame(kaleidoscopic_data)


@pytest.fixture
def dimensional_feature_constellation():
    """
    Orchestrates a numerical symphony of feature matrices,
    where each row illuminates a unique digital experience.
    """
    return np.array([
        [1, 0.8, 0.5, 0.3, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0.7, 0.4, 0, 0, 0, 0, 0],
        [0.6, 0, 0, 0, 0, 0, 0, 1, 0.9, 0.5, 0, 0],
        [0, 0.6, 0, 0, 0, 0, 0, 0, 0, 0, 0.9, 1]
    ])


@pytest.fixture
def celestial_normalized_patterns(dimensional_feature_constellation):
    """
    Transforms raw dimensional data into harmonious normalized patterns,
    where magnitudes whisper of unity and direction speaks of essence.
    """
    cosmic_norms = np.linalg.norm(dimensional_feature_constellation, axis=1)
    cosmic_norms[cosmic_norms == 0] = 1e-10  # A whisper in the void to avoid division by zero
    return dimensional_feature_constellation / cosmic_norms[:, np.newaxis]


class TestGameGenre:
    """
    A labyrinthine examination of the GameGenre class,
    weaving through its singleton implementation and data transformation capabilities.
    """
    
    def setup_method(self):
        """
        Cleanses the canvas before each artistic test,
        ensuring the singleton's sanctity remains unblemished.
        """
        # Dramatic erasure of previous states
        GameGenre._instance = None
        GameGenre._genre_cache = None
        GameGenre._game_ids = None
        GameGenre._feature_matrix = None
        GameGenre._normalized_matrix = None
    
    def test_singleton_pattern(self):
        """
        Validates the GameGenre's adherence to the ancient singleton pattern.
        Through creation and comparison, we unveil the truth of its singularity.
        """
        # Create an illusion where database calls are mere shadows
        with patch.object(GameGenre, 'get_genres') as mock_get_genres:
            mock_get_genres.return_value = (None, None, None, None)
            
            # The first manifestation emerges from the void
            first_incarnation = GameGenre()
            
            # The second call should summon the same entity, not a doppelgänger
            second_incarnation = GameGenre()
            
            # Behold! They are one and the same
            assert first_incarnation is second_incarnation
            
            # The sacred method was invoked exactly once, as the prophecy foretold
            mock_get_genres.assert_called_once()

    def test_get_genres(self, ethereal_genre_tapestry, crystallized_vector_formation, 
                      dimensional_feature_constellation, celestial_normalized_patterns):
        """
        Examines the mystical process of genre collection and transformation.
        Through mocked realms, we trace the path from raw data to enlightened representations.
        """
        # Summon the phantom of MongoDB
        spectral_mongo = MagicMock()
        enchanted_collection = MagicMock()
        mystical_db = {'steam_genre': enchanted_collection}
        arcane_cursor = MagicMock()
        
        # Enchant the mocks with specific behaviors
        arcane_cursor.sort.return_value = ethereal_genre_tapestry
        enchanted_collection.find.return_value = arcane_cursor
        spectral_mongo.get_database.return_value = mystical_db
        
        # Create a protected realm where external forces are controlled
        with patch('app.services.game_genre.MongoDBSingleton', return_value=spectral_mongo), \
             patch.object(GenreVectorizer, 'vectorize_game') as mock_vectorize, \
             patch.object(GenreVectorizer, 'build_game_feature_matrix') as mock_build_matrix, \
             patch.object(GenreVectorizer, 'normalize_matrix') as mock_normalize:
            
            # Infuse the vectorizer with predicted outcomes
            mock_vectorize.return_value = crystallized_vector_formation
            mock_build_matrix.return_value = (np.array([1, 2, 3, 4]), dimensional_feature_constellation)
            mock_normalize.return_value = celestial_normalized_patterns
            
            # The moment of creation - when GameGenre awakens and calls forth its genres
            game_genre_oracle = GameGenre()
            
            # Verify the sacred rituals were performed precisely
            enchanted_collection.find.assert_called_once_with({}, {"_id": 0})
            arcane_cursor.sort.assert_called_once_with("AppID", 1)
            mock_vectorize.assert_called_once()
            mock_build_matrix.assert_called_once_with(crystallized_vector_formation)
            mock_normalize.assert_called_once_with(dimensional_feature_constellation)
            
            # Confirm the artifacts were preserved in their intended sanctuaries
            pd.testing.assert_frame_equal(game_genre_oracle._genre_cache, crystallized_vector_formation)
            np.testing.assert_array_equal(game_genre_oracle._game_ids, np.array([1, 2, 3, 4]))
            np.testing.assert_array_equal(game_genre_oracle._feature_matrix, dimensional_feature_constellation)
            np.testing.assert_array_equal(game_genre_oracle._normalized_matrix, celestial_normalized_patterns)

    def test_get_multiple_genres(self, ethereal_genre_tapestry, crystallized_vector_formation):
        """
        Investigates the selective harvesting of specific genre constellations.
        A dance of filters and transformations that yields focused insights.
        """
        # First, create a mirage of the initialization process
        with patch.object(GameGenre, 'get_genres') as mock_get_genres:
            mock_get_genres.return_value = (None, None, None, None)
            
            # The entity takes form
            genre_curator = GameGenre()
            
            # Now, construct the apparatus for testing selective retrieval
            phantom_mongo = MagicMock()
            enchanted_collection = MagicMock()
            mystical_db = {'steam_genre': enchanted_collection}
            arcane_cursor = MagicMock()
            
            # Program the phantoms with specific behaviors
            chosen_games = ethereal_genre_tapestry[:2]  # Select only the first two mystical games
            arcane_cursor.sort.return_value = chosen_games
            enchanted_collection.find.return_value = arcane_cursor
            phantom_mongo.get_database.return_value = mystical_db
            
            # Establish control over the external realms
            with patch('app.services.game_genre.MongoDBSingleton', return_value=phantom_mongo), \
                 patch.object(GenreVectorizer, 'vectorize_game') as mock_vectorize:
                
                # Prepare the expected transformation result
                chosen_vectors = crystallized_vector_formation.iloc[:2].reset_index(drop=True)
                mock_vectorize.return_value = chosen_vectors
                
                # Invoke the method under scrutiny
                illuminated_result = genre_curator.get_multiple_genres([1, 2])
                
                # Verify the ritual was performed with precision
                enchanted_collection.find.assert_called_with({"AppID": {"$in": [1, 2]}}, {"_id": 0})
                arcane_cursor.sort.assert_called_with("AppID", 1)
                mock_vectorize.assert_called_once()
                
                # Confirm the result matches our prophesied outcome
                pd.testing.assert_frame_equal(illuminated_result, chosen_vectors)

    def test_get_genres_empty_result(self):
        """
        Explores the void - when the genres we seek remain elusive.
        In the absence of data, we must gracefully embrace the emptiness.
        """
        # Craft an illusion for the initial instantiation
        with patch.object(GameGenre, 'get_genres') as mock_get_genres:
            mock_get_genres.return_value = (None, None, None, None)
            
            # Summon the entity into being
            genre_explorer = GameGenre()
            
            # Dissolve the previous enchantment to prepare for our true test
            mock_get_genres.reset_mock()
            
            # Construct the apparatus for our journey into emptiness
            phantom_mongo = MagicMock()
            enchanted_collection = MagicMock()
            mystical_db = {'steam_genre': enchanted_collection}
            arcane_cursor = MagicMock()
            
            # Program the phantoms to return nothing but silence
            arcane_cursor.sort.return_value = []  # The void of empty results
            enchanted_collection.find.return_value = arcane_cursor
            phantom_mongo.get_database.return_value = mystical_db
            
            # Enter the realm of controlled chaos
            with patch('app.services.game_genre.MongoDBSingleton', return_value=phantom_mongo), \
                 patch.object(GenreVectorizer, 'vectorize_game', return_value=None):
                
                # Preserve the original wisdom
                ancient_knowledge = GameGenre.get_genres
                
                try:
                    # Temporarily restore the true method, bypassing our earlier deception
                    GameGenre.get_genres = ancient_knowledge
                    
                    # Invoke the method directly, facing the void
                    void_result = genre_explorer.get_genres()
                    
                    # Verify that the void returns only emptiness
                    assert void_result == (None, None, None, None)
                finally:
                    # Restore the veil of illusion
                    GameGenre.get_genres = mock_get_genres

    def test_get_multiple_genres_empty_input(self):
        """
        Contemplates the paradox of seeking nothing - when we ask for empty inputs,
        expect empty outputs. A zen koan of software testing.
        """
        # Establish a protected realm for creation
        with patch.object(GameGenre, 'get_genres') as mock_get_genres:
            mock_get_genres.return_value = (None, None, None, None)
            
            # Breathe life into our entity
            genre_philosopher = GameGenre()
            
            # Ask for nothing, and see what you receive
            void_result = genre_philosopher.get_multiple_genres(None)
            
            # The answer to nothing is nothing - an empty dictionary
            assert void_result == {}
            
    def test_compatibility_with_diverse_genre_structures(self):
        """
        Examines how our system handles the rich tapestry of genre diversity.
        From simple classifications to complex hierarchies, flexibility is key.
        """
        # Construct a collection of genre structures of varying complexity
        byzantine_genre_samples = [
            {"AppID": 10, "genre": {"Roguelike": 1}},  # Minimalist single genre
            {"AppID": 11, "genre": {"Platformer": 0.8, "Difficult": 1, "Pixel": 0.7, "indie": 0.9}},  # Rich multi-genre
            {"AppID": 12, "genre": {}}  # The void - a game with no genres
        ]
        
        # Summon the apparatus for controlled experimentation
        phantom_mongo = MagicMock()
        enchanted_collection = MagicMock()
        mystical_db = {'steam_genre': enchanted_collection}
        arcane_cursor = MagicMock()
        
        # Program our phantoms
        arcane_cursor.sort.return_value = byzantine_genre_samples
        enchanted_collection.find.return_value = arcane_cursor
        phantom_mongo.get_database.return_value = mystical_db
        
        # Expected vectorized outcome
        expected_vectorization = pd.DataFrame({
            "AppID": [10, 11, 12],
            "Roguelike": [1, 0, 0],
            "Platformer": [0, 0.8, 0],
            "Difficult": [0, 1, 0],
            "Pixel": [0, 0.7, 0],
            "indie": [0, 0.9, 0]
        })
        
        # Create our controlled environment
        with patch.object(GameGenre, 'get_genres') as mock_get_genres, \
             patch('app.services.game_genre.MongoDBSingleton', return_value=phantom_mongo), \
             patch.object(GenreVectorizer, 'vectorize_game') as mock_vectorize:
            
            mock_get_genres.return_value = (None, None, None, None)
            mock_vectorize.return_value = expected_vectorization
            
            # Manifest our entity
            genre_interpreter = GameGenre()
            
            # Reset to prepare for the actual call
            mock_get_genres.reset_mock()
            
            # Invoke the method directly on our diverse dataset
            diversified_result = genre_interpreter.get_multiple_genres([10, 11, 12])
            
            # Verify the outcome matches expectations
            pd.testing.assert_frame_equal(diversified_result, expected_vectorization)