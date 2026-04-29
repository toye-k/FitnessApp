"""
Main application window for the Fitness Exercise Trainer.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSplitter, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer
from pathlib import Path
from typing import List, Optional

from src.ui.widgets.body_viewer import BodyViewerWidget
from src.ui.widgets.exercise_list import ExerciseListWidget
from src.ui.widgets.exercise_detail import ExerciseDetailDialog
from src.services import ExerciseService
from src.utils.logger import get_logger
from src import config

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window combining 3D body viewer with exercise list.
    """

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

        self.exercise_service = ExerciseService()
        self.current_selected_muscles: List[str] = []

        self._setup_ui()
        self._connect_signals()
        self._apply_stylesheet()

        logger.info("Initialized main window")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Left side: Body viewer
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Body viewer label
        body_label = QLabel("3D Body Model - Click muscles to select")
        left_layout.addWidget(body_label)

        # Body viewer widget
        self.body_viewer = BodyViewerWidget()
        left_layout.addWidget(self.body_viewer)

        # Clear selection button
        clear_button = QPushButton("Clear Selection")
        clear_button.clicked.connect(self._on_clear_selection)
        left_layout.addWidget(clear_button)

        # Right side: Exercise list
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Exercises label
        exercises_label = QLabel("Exercises for Selected Muscles")
        right_layout.addWidget(exercises_label)

        # Exercise list
        self.exercise_list = ExerciseListWidget()
        right_layout.addWidget(self.exercise_list)

        # Splitter between body viewer and exercise list
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status()

    def _connect_signals(self) -> None:
        """Connect all signals and slots."""
        # Body viewer signals
        self.body_viewer.muscles_changed.connect(self._on_muscles_changed)
        self.body_viewer.muscle_selected.connect(self._on_muscle_selected)

        # Exercise list signals
        self.exercise_list.exercise_selected.connect(self._on_exercise_selected)
        self.exercise_list.exercise_double_clicked.connect(
            self._on_exercise_double_clicked
        )

        logger.debug("Connected all signals and slots")

    def _apply_stylesheet(self) -> None:
        """Apply the stylesheet to the application."""
        stylesheet_path = Path(__file__).parent / "styles" / "stylesheet.qss"

        try:
            with open(stylesheet_path, "r") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)
                logger.info("Applied stylesheet")
        except FileNotFoundError:
            logger.warning(f"Stylesheet not found at {stylesheet_path}")

    def _on_muscles_changed(self, muscle_ids: List[str]) -> None:
        """
        Handle muscle selection change.

        Args:
            muscle_ids: List of currently selected muscle IDs
        """
        self.current_selected_muscles = muscle_ids
        self.exercise_list.set_exercises_for_muscles(muscle_ids)
        self._update_status()
        logger.debug(f"Muscles changed: {muscle_ids}")

    def _on_muscle_selected(self, muscle_id: str) -> None:
        """
        Handle individual muscle selection.

        Args:
            muscle_id: The muscle ID that was selected
        """
        muscle_name = self.body_viewer.get_muscle_names().get(muscle_id, muscle_id)
        logger.debug(f"Muscle selected: {muscle_name}")

    def _on_exercise_selected(self, exercise) -> None:
        """
        Handle exercise selection in the list.

        Args:
            exercise: The selected Exercise object
        """
        logger.debug(f"Exercise selected: {exercise.name}")

    def _on_exercise_double_clicked(self, exercise) -> None:
        """
        Handle exercise double-click (opens detail dialog).

        Args:
            exercise: The selected Exercise object
        """
        dialog = ExerciseDetailDialog(exercise, self)
        dialog.exec()
        logger.debug(f"Opened detail dialog for: {exercise.name}")

    def _on_clear_selection(self) -> None:
        """Handle clear selection button."""
        self.body_viewer.clear_selection()
        self.current_selected_muscles = []
        self.exercise_list.clear_selection()
        self._update_status()
        logger.debug("Cleared all selections")

    def _update_status(self) -> None:
        """Update the status bar."""
        muscle_count = len(self.current_selected_muscles)
        exercise_count = self.exercise_list.get_exercise_count()

        status_text = f"Muscles: {muscle_count} | Exercises: {exercise_count}"
        self.status_bar.showMessage(status_text)

    def closeEvent(self, event) -> None:
        """
        Handle window close event.

        Args:
            event: The close event
        """
        logger.info("Application closing")
        super().closeEvent(event)
