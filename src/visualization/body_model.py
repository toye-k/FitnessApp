"""
3D Body Model for visualization with muscle mapping.
Creates a simple geometric body representation using Vispy.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from src.models import Muscle, MuscleGroup
from src.data import DataLoader
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MuscleGeometry:
    """Represents the 3D geometry for a muscle group."""

    muscle_id: str
    muscle_name: str
    vertices: np.ndarray  # (N, 3) array of vertex positions
    faces: np.ndarray  # (M, 3) array of face indices
    color: Tuple[float, float, float, float]  # RGBA color
    normal_color: Tuple[float, float, float, float]
    highlight_color: Tuple[float, float, float, float]
    is_selected: bool = False


class BodyModel:
    """
    3D body model that creates a simplified geometric representation of the human body.
    Each muscle group is represented as a geometric shape that can be clicked and selected.
    """

    def __init__(self) -> None:
        """Initialize the body model with default geometry."""
        self.data_loader = DataLoader()
        self.muscles: Dict[str, Muscle] = {}
        self.geometries: Dict[str, MuscleGeometry] = {}
        self.selected_muscles: set = set()

        self._load_muscles()
        self._create_geometries()

    def _load_muscles(self) -> None:
        """Load muscle data from the data loader."""
        muscles = self.data_loader.load_muscles()
        self.muscles = {muscle.id: muscle for muscle in muscles}
        logger.info(f"Loaded {len(self.muscles)} muscle groups")

    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0) -> Tuple[float, float, float, float]:
        """
        Convert hex color to RGBA tuple (0-1 range).

        Args:
            hex_color: Hex color string (e.g., "#FF6B6B")
            alpha: Alpha channel value (0-1)

        Returns:
            RGBA tuple with values 0-1
        """
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        return (r, g, b, alpha)

    def _create_geometries(self) -> None:
        """Create geometry metadata for each muscle group."""
        dummy_verts = np.zeros((3, 3), dtype=np.float32)
        dummy_faces = np.array([[0, 1, 2]], dtype=np.uint32)

        for muscle_id, muscle in self.muscles.items():
            try:
                normal_color = self._hex_to_rgba(muscle.color, 0.8)
                highlight_color = self._hex_to_rgba(muscle.color, 1.0)

                self.geometries[muscle_id] = MuscleGeometry(
                    muscle_id=muscle_id,
                    muscle_name=muscle.name,
                    vertices=dummy_verts,
                    faces=dummy_faces,
                    color=normal_color,
                    normal_color=normal_color,
                    highlight_color=highlight_color,
                )
            except Exception as e:
                logger.warning(f"Failed to create geometry for {muscle_id}: {e}")

        logger.info(f"Created geometries for {len(self.geometries)} muscles")

    def select_muscle(self, muscle_id: str) -> None:
        """
        Select a muscle, adding it to the selected set.

        Args:
            muscle_id: The ID of the muscle to select
        """
        if muscle_id in self.geometries:
            self.selected_muscles.add(muscle_id)
            logger.debug(f"Selected muscle: {muscle_id}")

    def deselect_muscle(self, muscle_id: str) -> None:
        """
        Deselect a muscle, removing it from the selected set.

        Args:
            muscle_id: The ID of the muscle to deselect
        """
        if muscle_id in self.selected_muscles:
            self.selected_muscles.discard(muscle_id)
            logger.debug(f"Deselected muscle: {muscle_id}")

    def toggle_muscle(self, muscle_id: str) -> None:
        """
        Toggle the selection state of a muscle.

        Args:
            muscle_id: The ID of the muscle to toggle
        """
        if muscle_id in self.selected_muscles:
            self.deselect_muscle(muscle_id)
        else:
            self.select_muscle(muscle_id)

    def clear_selection(self) -> None:
        """Clear all selected muscles."""
        self.selected_muscles.clear()
        logger.debug("Cleared all muscle selections")

    def get_selected_muscles(self) -> List[str]:
        """
        Get list of currently selected muscle IDs.

        Returns:
            List of muscle IDs that are currently selected
        """
        return list(self.selected_muscles)

    def is_muscle_selected(self, muscle_id: str) -> bool:
        """
        Check if a muscle is currently selected.

        Args:
            muscle_id: The ID of the muscle to check

        Returns:
            True if the muscle is selected, False otherwise
        """
        return muscle_id in self.selected_muscles

    def get_muscle_geometry(self, muscle_id: str) -> Optional[MuscleGeometry]:
        """
        Get the geometry for a specific muscle.

        Args:
            muscle_id: The ID of the muscle

        Returns:
            MuscleGeometry object or None if not found
        """
        return self.geometries.get(muscle_id)

    def get_all_geometries(self) -> Dict[str, MuscleGeometry]:
        """
        Get all muscle geometries.

        Returns:
            Dictionary mapping muscle IDs to MuscleGeometry objects
        """
        return self.geometries.copy()

    def get_muscle_name(self, muscle_id: str) -> Optional[str]:
        """
        Get the display name of a muscle.

        Args:
            muscle_id: The ID of the muscle

        Returns:
            Muscle name or None if not found
        """
        muscle = self.muscles.get(muscle_id)
        return muscle.name if muscle else None
