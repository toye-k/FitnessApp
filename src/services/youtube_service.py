"""
YouTube service for handling exercise video links.
"""

from typing import Optional
from urllib.parse import quote
from src.config import YOUTUBE_SEARCH_URL


class YouTubeService:
    """Service for YouTube video integration and URL management."""

    YOUTUBE_BASE_URL = "https://www.youtube.com"
    YOUTUBE_WATCH_URL = f"{YOUTUBE_BASE_URL}/watch?v="
    YOUTUBE_EMBED_URL = "https://www.youtube.com/embed"

    @staticmethod
    def get_watch_url(video_id: str) -> str:
        """
        Get YouTube watch URL for a video ID.

        Args:
            video_id: YouTube video ID

        Returns:
            Full YouTube watch URL
        """
        return f"{YouTubeService.YOUTUBE_WATCH_URL}{video_id}"

    @staticmethod
    def get_embed_url(video_id: str) -> str:
        """
        Get YouTube embed URL for embedding in an iframe.

        Args:
            video_id: YouTube video ID

        Returns:
            Full YouTube embed URL
        """
        return f"{YouTubeService.YOUTUBE_EMBED_URL}/{video_id}"

    @staticmethod
    def get_search_url(query: str) -> str:
        """
        Get YouTube search URL for a query.

        Args:
            query: Search query (e.g., "barbell curl tutorial")

        Returns:
            Full YouTube search URL
        """
        return YOUTUBE_SEARCH_URL.format(quote(query))

    @staticmethod
    def get_exercise_tutorial_url(exercise_name: str) -> str:
        """
        Get YouTube search URL for exercise tutorial.

        Args:
            exercise_name: Name of the exercise

        Returns:
            Full YouTube search URL for the exercise tutorial
        """
        search_query = f"{exercise_name} form tutorial"
        return YouTubeService.get_search_url(search_query)

    @staticmethod
    def is_valid_video_id(video_id: str) -> bool:
        """
        Validate a YouTube video ID format.

        Args:
            video_id: Video ID to validate

        Returns:
            True if video ID format is valid
        """
        if not video_id or not isinstance(video_id, str):
            return False
        # YouTube video IDs are 11 characters long and alphanumeric with - and _
        return len(video_id) == 11 and all(
            c.isalnum() or c in "-_" for c in video_id
        )

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.

        Args:
            url: YouTube URL in various formats

        Returns:
            Video ID if valid, None otherwise
        """
        if not url:
            return None

        # Direct video ID
        if YouTubeService.is_valid_video_id(url):
            return url

        # youtu.be short URL: https://youtu.be/VIDEO_ID
        if "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
            return video_id if YouTubeService.is_valid_video_id(video_id) else None

        # Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        if "youtube.com/watch?v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
            return video_id if YouTubeService.is_valid_video_id(video_id) else None

        return None

    @staticmethod
    def open_video_in_browser(video_id: str) -> str:
        """
        Get the URL to open video in browser.

        Args:
            video_id: YouTube video ID

        Returns:
            Full YouTube watch URL
        """
        return YouTubeService.get_watch_url(video_id)
