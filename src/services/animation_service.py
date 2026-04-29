"""
Animation service for handling exercise GIF animations.
"""

from typing import Optional
from pathlib import Path
from PIL import Image

from src.config import GIF_MAX_SIZE


class AnimationService:
    """Service for handling exercise animation files (GIFs)."""

    def __init__(self, assets_dir: str = "assets"):
        """
        Initialize animation service.

        Args:
            assets_dir: Directory containing animation assets
        """
        self.assets_dir = Path(assets_dir)
        self.gifs_dir = self.assets_dir / "gifs"

    def get_animation_path(self, filename: str) -> Path:
        """
        Get full path to an animation file.

        Args:
            filename: Animation filename

        Returns:
            Full path to the animation file
        """
        return self.gifs_dir / filename

    def animation_exists(self, filename: str) -> bool:
        """
        Check if an animation file exists.

        Args:
            filename: Animation filename

        Returns:
            True if file exists
        """
        path = self.get_animation_path(filename)
        return path.exists() and path.is_file()

    def load_animation(self, filename: str) -> Optional[Image.Image]:
        """
        Load an animation GIF file.

        Args:
            filename: Animation filename

        Returns:
            PIL Image object or None if file not found or invalid
        """
        if not self.animation_exists(filename):
            return None

        try:
            path = self.get_animation_path(filename)
            image = Image.open(path)
            return image
        except (IOError, OSError) as e:
            print(f"Error loading animation {filename}: {e}")
            return None

    def get_animation_thumbnail(self, filename: str) -> Optional[Image.Image]:
        """
        Get first frame of animation as thumbnail.

        Args:
            filename: Animation filename

        Returns:
            PIL Image object of first frame or None
        """
        image = self.load_animation(filename)
        if image is None:
            return None

        try:
            # Ensure we get the first frame
            image.seek(0)
            # Convert to thumbnail size
            image.thumbnail(GIF_MAX_SIZE, Image.Resampling.LANCZOS)
            return image
        except Exception as e:
            print(f"Error creating thumbnail for {filename}: {e}")
            return None

    def resize_animation(
        self, filename: str, max_width: int, max_height: int
    ) -> Optional[Image.Image]:
        """
        Load and resize animation to fit within dimensions.

        Args:
            filename: Animation filename
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels

        Returns:
            Resized PIL Image object or None
        """
        image = self.load_animation(filename)
        if image is None:
            return None

        try:
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return image
        except Exception as e:
            print(f"Error resizing animation {filename}: {e}")
            return None

    def get_animation_format(self, filename: str) -> Optional[str]:
        """
        Get animation file format.

        Args:
            filename: Animation filename

        Returns:
            File format (e.g., 'GIF', 'MP4') or None if file not found
        """
        image = self.load_animation(filename)
        if image is None:
            return None

        return image.format

    def validate_animation_file(self, filename: str) -> bool:
        """
        Validate that an animation file is valid.

        Args:
            filename: Animation filename

        Returns:
            True if file is valid and readable
        """
        if not self.animation_exists(filename):
            return False

        try:
            image = self.load_animation(filename)
            return image is not None
        except Exception:
            return False

    def list_animations(self) -> list:
        """
        List all available animation files.

        Returns:
            List of animation filenames
        """
        if not self.gifs_dir.exists():
            return []

        return [f.name for f in self.gifs_dir.glob("*")]
