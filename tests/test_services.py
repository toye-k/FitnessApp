"""
Unit tests for services.
"""

import pytest
from src.services import YouTubeService, AnimationService


class TestYouTubeService:
    """Tests for YouTube service."""

    def test_get_watch_url(self):
        """Test getting watch URL."""
        url = YouTubeService.get_watch_url("dQw4w9WgXcQ")
        assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_get_embed_url(self):
        """Test getting embed URL."""
        url = YouTubeService.get_embed_url("dQw4w9WgXcQ")
        assert url == "https://www.youtube.com/embed/dQw4w9WgXcQ"

    def test_get_search_url(self):
        """Test getting search URL."""
        url = YouTubeService.get_search_url("barbell curl")
        assert "youtube.com" in url
        assert "barbell" in url.lower()

    def test_get_exercise_tutorial_url(self):
        """Test getting exercise tutorial URL."""
        url = YouTubeService.get_exercise_tutorial_url("Barbell Curl")
        assert "youtube.com" in url
        assert "tutorial" in url.lower() or "barbell" in url.lower()

    def test_is_valid_video_id_valid(self):
        """Test validating valid video IDs."""
        assert YouTubeService.is_valid_video_id("dQw4w9WgXcQ") is True
        assert YouTubeService.is_valid_video_id("abc123def_-") is True

    def test_is_valid_video_id_invalid(self):
        """Test validating invalid video IDs."""
        assert YouTubeService.is_valid_video_id("") is False
        assert YouTubeService.is_valid_video_id("short") is False
        assert YouTubeService.is_valid_video_id(None) is False
        assert YouTubeService.is_valid_video_id("toolongvideoidentifier") is False

    def test_extract_video_id_direct(self):
        """Test extracting video ID from direct ID."""
        video_id = YouTubeService.extract_video_id("dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_short_url(self):
        """Test extracting video ID from short URL."""
        video_id = YouTubeService.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_watch_url(self):
        """Test extracting video ID from watch URL."""
        video_id = YouTubeService.extract_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_watch_url_with_params(self):
        """Test extracting video ID from watch URL with parameters."""
        video_id = YouTubeService.extract_video_id(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=5s"
        )
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_invalid(self):
        """Test extracting video ID from invalid URL."""
        video_id = YouTubeService.extract_video_id("https://google.com")
        assert video_id is None

    def test_open_video_in_browser(self):
        """Test getting URL to open in browser."""
        url = YouTubeService.open_video_in_browser("dQw4w9WgXcQ")
        assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


class TestAnimationService:
    """Tests for Animation service."""

    def test_animation_service_init(self):
        """Test initializing animation service."""
        service = AnimationService()
        assert service.assets_dir.name == "assets"
        assert service.gifs_dir.name == "gifs"

    def test_get_animation_path(self):
        """Test getting animation path."""
        service = AnimationService()
        path = service.get_animation_path("curl.gif")
        assert "gifs" in str(path)
        assert "curl.gif" in str(path)

    def test_list_animations_empty(self):
        """Test listing animations when directory doesn't exist."""
        service = AnimationService("nonexistent")
        animations = service.list_animations()
        assert animations == []

    def test_animation_exists_false(self):
        """Test checking if animation exists when it doesn't."""
        service = AnimationService()
        exists = service.animation_exists("nonexistent.gif")
        assert exists is False

    def test_load_animation_not_found(self):
        """Test loading animation that doesn't exist."""
        service = AnimationService()
        image = service.load_animation("nonexistent.gif")
        assert image is None
