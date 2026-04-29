"""
PyQt6 widget for 3D body visualization using Vispy.
Provides interactive muscle selection and viewing.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
import numpy as np
from typing import Optional, List, Dict, Set

try:
    from vispy import scene
    from vispy.scene import visuals
    from vispy import color as vis_color
    from vispy.visuals.filters import ShadingFilter
except ImportError:
    raise ImportError("Vispy is required. Install with: pip install vispy")

from src.visualization.body_model import BodyModel
from src.visualization.color_manager import ColorManager
from src.utils.logger import get_logger
from src import config

logger = get_logger(__name__)


class BodyViewerWidget(QWidget):
    """
    PyQt6 widget for viewing and interacting with 3D body model.
    Supports mouse-based muscle selection.
    """

    # Signals
    muscle_selected = pyqtSignal(str)  # Emitted when a muscle is selected
    muscles_changed = pyqtSignal(list)  # Emitted when selection changes

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the body viewer widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.body_model = BodyModel()
        self.color_manager = ColorManager()
        self._selected_visuals: Set[str] = set()  # Track visual selection locally
        self._secondary_visuals: Set[str] = set()  # Track secondary muscle visuals

        # Vispy canvas and scene
        self.canvas = scene.SceneCanvas(
            keys="interactive",
            show=False,
            bgcolor="black",
        )
        self.view = self.canvas.central_widget.add_view()

        # Set up camera - use TurntableCamera instead of ArcballCamera
        self.view.camera = scene.cameras.TurntableCamera(
            distance=3.0,
            elevation=30,
            azimuth=45
        )

        # Muscle visuals
        self.muscle_visuals: Dict[str, visuals.Mesh] = {}
        self._create_muscle_visuals()

        # Mouse tracking
        self.canvas.events.mouse_move.connect(self._on_mouse_move)
        self.canvas.events.mouse_press.connect(self._on_mouse_press)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas.native)
        self.setLayout(layout)

        logger.info("Initialized body viewer widget")

    def _create_muscle_visuals(self) -> None:
        """Create Vispy visuals for individual BodyParts3D muscles."""
        try:
            from src.visualization.isolated_muscles_loader import IsolatedMusclesLoader

            # Load individual muscle models (preserves spatial positions)
            muscle_models = IsolatedMusclesLoader.get_major_muscles()

            if not muscle_models:
                logger.warning("No muscle models loaded")
                return

            # Create a separate mesh visual for each muscle
            for muscle_name, (vertices, faces) in muscle_models.items():
                try:
                    # Create mesh with default color
                    mesh = visuals.Mesh(
                        vertices=vertices,
                        faces=faces,
                        color=(0.85, 0.7, 0.6, 0.9),  # Brighter skin tone
                        shading=None
                    )
                    # Attach headlight shading filter - light always faces camera
                    mesh.attach(ShadingFilter(shading='smooth', light_dir=(0, 0, 2)))
                    mesh.interactive = True
                    self.view.add(mesh)

                    # Store mesh for later manipulation
                    self.muscle_visuals[muscle_name] = mesh

                except Exception as e:
                    logger.debug(f"Failed to create visual for {muscle_name}: {e}")

            logger.info(f"Created {len(self.muscle_visuals)} individual muscle visuals")

        except ImportError:
            logger.warning("Could not import isolated muscles loader")
            return

        # Auto-fit the camera to the scene
        self.view.camera.view_changed()

    def _on_mouse_press(self, event) -> None:
        """
        Handle mouse press event for muscle selection.
        Uses 3D picking to find which muscle visual is under the cursor.
        Supports toggle selection: click to select, click again to deselect.

        Args:
            event: Mouse event from Vispy
        """
        if event.button != 1:  # Left click only
            return

        try:
            # Hit-test: find which visual is under the cursor
            visual = self.canvas.visual_at(event.pos)

            # Reverse-lookup: find which group name owns this visual
            muscle_name = None
            for name, mesh in self.muscle_visuals.items():
                if mesh is visual:
                    muscle_name = name
                    break

            if muscle_name is None:
                return  # Clicked empty space — do nothing

            # Toggle: if already selected, deselect; otherwise select
            if muscle_name in self._selected_visuals:
                self._selected_visuals.discard(muscle_name)
            else:
                self._selected_visuals.add(muscle_name)

            self._update_muscle_visuals()
            self.muscles_changed.emit(list(self._selected_visuals))
            logger.debug(f"Toggled muscle: {muscle_name}, selected: {muscle_name in self._selected_visuals}")
        except Exception as e:
            logger.warning(f"Error handling mouse press: {e}")

    def _on_mouse_move(self, event) -> None:
        """
        Handle mouse move event for highlighting.

        Args:
            event: Mouse event from Vispy
        """
        # Could implement highlighting on hover here
        pass

    def _update_muscle_visuals(self) -> None:
        """Update muscle colors based on selection state."""
        primary_color = (1.0, 0.2, 0.2, 1.0)  # Red for primary
        secondary_color = (1.0, 0.6, 0.1, 1.0)  # Orange for secondary
        default_color = (0.7, 0.5, 0.4, 0.9)  # Skin tone

        for muscle_name, mesh in self.muscle_visuals.items():
            if muscle_name in self._selected_visuals:
                mesh.color = primary_color
            elif muscle_name in self._secondary_visuals:
                mesh.color = secondary_color
            else:
                mesh.color = default_color

    def clear_selection(self) -> None:
        """Clear all selected muscles."""
        self._selected_visuals.clear()
        self._secondary_visuals.clear()
        self.body_model.clear_selection()
        self._update_muscle_visuals()
        self.muscles_changed.emit([])

    def highlight_muscles(
        self,
        primary_muscle_ids: List[str],
        secondary_muscle_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Programmatically highlight muscles for an exercise infographic.

        Args:
            primary_muscle_ids: Muscle IDs to highlight in red
            secondary_muscle_ids: Muscle IDs to highlight in orange
        """
        from src.visualization.isolated_muscles_loader import IsolatedMusclesLoader

        # Maps legacy/composite exercise IDs to MUSCLE_GROUPS keys
        EXERCISE_ID_TO_GROUPS = {
            "glutes": ["gluteus_maximus", "gluteus_medius", "gluteus_minimus"],
            "back": ["upper_back", "lats"],
            "abs": ["upper_abs", "lower_abs", "obliques"],
        }

        muscle_groups = IsolatedMusclesLoader.MUSCLE_GROUPS

        def resolve(muscle_id: str) -> List[str]:
            return EXERCISE_ID_TO_GROUPS.get(muscle_id, [muscle_id])

        self._selected_visuals.clear()
        self._secondary_visuals.clear()

        for muscle_id in primary_muscle_ids:
            for group_key in resolve(muscle_id):
                for name in muscle_groups.get(group_key, []):
                    if name in self.muscle_visuals:
                        self._selected_visuals.add(name)

        for muscle_id in (secondary_muscle_ids or []):
            for group_key in resolve(muscle_id):
                for name in muscle_groups.get(group_key, []):
                    if name in self.muscle_visuals and name not in self._selected_visuals:
                        self._secondary_visuals.add(name)

        self._update_muscle_visuals()

    def set_camera(
        self,
        distance: float = 3.0,
        elevation: float = 20.0,
        azimuth: float = 0.0,
    ) -> None:
        """
        Override camera parameters.

        Args:
            distance: Camera distance from center
            elevation: Camera elevation angle
            azimuth: Camera azimuth angle
        """
        self.view.camera.distance = distance
        self.view.camera.elevation = elevation
        self.view.camera.azimuth = azimuth

    def get_selected_muscles(self) -> List[str]:
        """
        Get list of currently selected muscles.

        Returns:
            List of selected muscle IDs
        """
        return self.body_model.get_selected_muscles()

    def get_muscle_names(self) -> Dict[str, str]:
        """
        Get mapping of muscle IDs to display names.

        Returns:
            Dictionary mapping muscle IDs to names
        """
        result = {}
        for muscle_id in self.body_model.geometries.keys():
            name = self.body_model.get_muscle_name(muscle_id)
            if name:
                result[muscle_id] = name
        return result

