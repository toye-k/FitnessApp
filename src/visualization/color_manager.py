"""
Color management for muscle visualization.
Handles color conversion and palette management.
"""

from typing import Dict, Tuple, Optional
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ColorManager:
    """
    Manages colors for muscle visualization.
    Handles conversion between color formats and provides color utilities.
    """

    # Default color palette
    DEFAULT_PALETTE = {
        "muscle_default": "#808080",
        "muscle_selected": "#FFA500",
        "muscle_highlight": "#FF6B6B",
        "background": "#1a1a1a",
        "grid": "#404040",
        "text": "#FFFFFF",
    }

    # Cached conversions
    _hex_to_rgb_cache: Dict[str, Tuple[float, float, float]] = {}
    _hex_to_rgba_cache: Dict[str, Tuple[float, float, float, float]] = {}

    def __init__(self) -> None:
        """Initialize the color manager."""
        self.palette = self.DEFAULT_PALETTE.copy()
        logger.info("Initialized color manager")

    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
        """
        Convert hex color to RGB tuple (0-1 range).

        Args:
            hex_color: Hex color string (e.g., "#FF6B6B")

        Returns:
            RGB tuple with values 0-1
        """
        # Check cache
        if hex_color in ColorManager._hex_to_rgb_cache:
            return ColorManager._hex_to_rgb_cache[hex_color]

        hex_color = hex_color.lstrip("#")
        try:
            r, g, b = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
            result = (r, g, b)
            ColorManager._hex_to_rgb_cache[hex_color] = result
            return result
        except (ValueError, IndexError) as e:
            logger.warning(f"Invalid hex color: {hex_color}, using default gray")
            return (0.5, 0.5, 0.5)

    @staticmethod
    def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> Tuple[float, float, float, float]:
        """
        Convert hex color to RGBA tuple (0-1 range).

        Args:
            hex_color: Hex color string (e.g., "#FF6B6B")
            alpha: Alpha channel value (0-1)

        Returns:
            RGBA tuple with values 0-1
        """
        cache_key = f"{hex_color}_{alpha}"
        if cache_key in ColorManager._hex_to_rgba_cache:
            return ColorManager._hex_to_rgba_cache[cache_key]

        r, g, b = ColorManager.hex_to_rgb(hex_color)
        result = (r, g, b, alpha)
        ColorManager._hex_to_rgba_cache[cache_key] = result
        return result

    @staticmethod
    def rgb_to_hex(r: float, g: float, b: float) -> str:
        """
        Convert RGB values (0-1) to hex color.

        Args:
            r: Red channel (0-1)
            g: Green channel (0-1)
            b: Blue channel (0-1)

        Returns:
            Hex color string (e.g., "#FF6B6B")
        """
        try:
            r_hex = int(r * 255)
            g_hex = int(g * 255)
            b_hex = int(b * 255)
            return f"#{r_hex:02X}{g_hex:02X}{b_hex:02X}"
        except (ValueError, OverflowError) as e:
            logger.warning(f"Invalid RGB values: {r}, {g}, {b}, using default gray")
            return "#808080"

    @staticmethod
    def is_valid_hex(hex_color: str) -> bool:
        """
        Check if a string is a valid hex color.

        Args:
            hex_color: String to validate

        Returns:
            True if valid hex color, False otherwise
        """
        hex_color = hex_color.lstrip("#")
        return bool(re.match(r"^[0-9A-Fa-f]{6}$", hex_color))

    @staticmethod
    def blend_colors(
        color1: Tuple[float, float, float, float],
        color2: Tuple[float, float, float, float],
        alpha: float,
    ) -> Tuple[float, float, float, float]:
        """
        Blend two RGBA colors together.

        Args:
            color1: First RGBA color
            color2: Second RGBA color
            alpha: Blend factor (0-1), where 0 = color1, 1 = color2

        Returns:
            Blended RGBA color
        """
        alpha = max(0.0, min(1.0, alpha))
        r = color1[0] * (1 - alpha) + color2[0] * alpha
        g = color1[1] * (1 - alpha) + color2[1] * alpha
        b = color1[2] * (1 - alpha) + color2[2] * alpha
        a = color1[3] * (1 - alpha) + color2[3] * alpha
        return (r, g, b, a)

    @staticmethod
    def brighten(color: Tuple[float, float, float, float], factor: float = 0.2) -> Tuple[float, float, float, float]:
        """
        Brighten a color.

        Args:
            color: RGBA color tuple
            factor: Brightness increase factor (0-1)

        Returns:
            Brightened RGBA color
        """
        factor = max(0.0, min(1.0, factor))
        r = min(1.0, color[0] + factor)
        g = min(1.0, color[1] + factor)
        b = min(1.0, color[2] + factor)
        return (r, g, b, color[3])

    @staticmethod
    def darken(color: Tuple[float, float, float, float], factor: float = 0.2) -> Tuple[float, float, float, float]:
        """
        Darken a color.

        Args:
            color: RGBA color tuple
            factor: Darkness increase factor (0-1)

        Returns:
            Darkened RGBA color
        """
        factor = max(0.0, min(1.0, factor))
        r = max(0.0, color[0] - factor)
        g = max(0.0, color[1] - factor)
        b = max(0.0, color[2] - factor)
        return (r, g, b, color[3])

    def set_color(self, key: str, hex_color: str) -> None:
        """
        Set a color in the palette.

        Args:
            key: Color key (e.g., "muscle_default")
            hex_color: Hex color string

        Returns:
            None
        """
        if self.is_valid_hex(hex_color):
            self.palette[key] = hex_color
            # Clear relevant cache entries
            if hex_color in self._hex_to_rgb_cache:
                del self._hex_to_rgb_cache[hex_color]
            logger.debug(f"Updated palette color: {key} = {hex_color}")
        else:
            logger.warning(f"Invalid hex color for key {key}: {hex_color}")

    def get_color(self, key: str) -> Optional[str]:
        """
        Get a color from the palette.

        Args:
            key: Color key (e.g., "muscle_default")

        Returns:
            Hex color string or None if not found
        """
        return self.palette.get(key)

    def get_color_rgba(self, key: str, alpha: float = 1.0) -> Optional[Tuple[float, float, float, float]]:
        """
        Get a color from the palette as RGBA.

        Args:
            key: Color key
            alpha: Alpha channel value (0-1)

        Returns:
            RGBA tuple or None if key not found
        """
        color = self.palette.get(key)
        if color:
            return self.hex_to_rgba(color, alpha)
        return None

    def reset_palette(self) -> None:
        """Reset palette to defaults."""
        self.palette = self.DEFAULT_PALETTE.copy()
        logger.info("Reset color palette to defaults")
