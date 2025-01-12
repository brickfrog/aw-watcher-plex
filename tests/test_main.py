import pytest
from unittest.mock import Mock
from aw_watcher_plex.main import get_metadata_from_session

@pytest.fixture
def mock_episode_session():
    """Create a mock Plex session for a TV episode"""
    session = Mock()
    session.title = "Episode Title"
    session.type = "episode"
    session.duration = 1800000 
    session.year = 2024
    session.summary = "Episode summary"
    session.contentRating = "TV-14"
    session.genres = ["Drama", "Sci-Fi"]
    session.viewOffset = 360000 
    session.grandparentTitle = "Show Title"
    session.parentIndex = 2  
    session.index = 5  
    
    # Mock player attributes
    session.player = Mock()
    session.player.title = "Plex for Windows"
    session.player.device = "PC"
    session.player.platform = "Windows"
    session.player.state = "playing"
    
    return session

@pytest.fixture
def mock_movie_session():
    """Create a mock Plex session for a movie"""
    session = Mock()
    session.title = "Movie Title"
    session.type = "movie"
    session.duration = 7200000  
    session.year = 2024
    session.summary = "Movie summary"
    session.contentRating = "PG-13"
    session.genres = ["Action", "Adventure"]
    session.viewOffset = 900000  
    session.studio = "Universal Studios"
    session.rating = 8.5
    
    # Mock player attributes
    session.player = Mock()
    session.player.title = "Plex for TV"
    session.player.device = "Smart TV"
    session.player.platform = "Tizen"
    session.player.state = "playing"
    
    return session

def test_get_metadata_from_episode_session(mock_episode_session):
    """Test metadata extraction for TV episode"""
    data = get_metadata_from_session(mock_episode_session)
    
    assert data["title"] == "Episode Title"
    assert data["type"] == "episode"
    assert data["player_state"] == "playing"
    assert data["duration"] == 1800000
    assert data["year"] == 2024
    assert data["summary"] == "Episode summary"
    assert data["contentRating"] == "TV-14"
    assert data["genres"] == ["Drama", "Sci-Fi"]
    
    # Check progress data
    assert data["progress"]["viewOffset"] == 360000
    assert "timestamp" in data["progress"]
    
    assert data["show_title"] == "Show Title"
    assert data["season_number"] == 2
    assert data["episode_number"] == 5
    
    assert data["player"]["title"] == "Plex for Windows"
    assert data["player"]["device"] == "PC"
    assert data["player"]["platform"] == "Windows"
    assert data["player"]["state"] == "playing"

def test_get_metadata_from_movie_session(mock_movie_session):
    """Test metadata extraction for movie"""
    data = get_metadata_from_session(mock_movie_session)
    
    assert data["title"] == "Movie Title"
    assert data["type"] == "movie"
    assert data["player_state"] == "playing"
    assert data["duration"] == 7200000
    assert data["year"] == 2024
    assert data["summary"] == "Movie summary"
    assert data["contentRating"] == "PG-13"
    assert data["genres"] == ["Action", "Adventure"]
    
    # Check progress data
    assert data["progress"]["viewOffset"] == 900000
    assert "timestamp" in data["progress"]
    
    assert data["studio"] == "Universal Studios"
    assert data["rating"] == 8.5
    
    assert data["player"]["title"] == "Plex for TV"
    assert data["player"]["device"] == "Smart TV"
    assert data["player"]["platform"] == "Tizen"
    assert data["player"]["state"] == "playing"

def test_get_metadata_handles_missing_attributes():
    """Test that the metadata extraction handles missing attributes gracefully"""
    session = Mock(spec=['title', 'type', 'player']) 
    session.title = "Test Title"
    session.type = "movie"
    session.player = Mock(spec=['state'])  
    session.player.state = "playing"
    
    data = get_metadata_from_session(session)
    
    assert data["title"] == "Test Title"
    assert data["type"] == "movie"
    assert data["duration"] is None
    assert data["year"] is None
    assert data["summary"] is None
    assert data["contentRating"] is None
    assert data["genres"] == []
    assert data["progress"]["viewOffset"] == 0
    assert "timestamp" in data["progress"]
    assert data["player"]["title"] is None
    assert data["player"]["device"] is None
    assert data["player"]["platform"] is None
    assert data["player"]["state"] == "playing" 