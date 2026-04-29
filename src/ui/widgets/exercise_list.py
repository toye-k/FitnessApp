"""
Exercise list widget for displaying and filtering exercises.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QCheckBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from typing import List, Optional, Dict
from src.models import Exercise
from src.services import ExerciseService
from src.utils.logger import get_logger
from src import config

logger = get_logger(__name__)


class ExerciseListWidget(QWidget):
    """
    Widget for displaying a list of exercises with filtering options.
    """

    # Signals
    exercise_selected = pyqtSignal(Exercise)  # Emitted when an exercise is selected
    exercise_double_clicked = pyqtSignal(Exercise)  # Emitted when an exercise is double-clicked

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the exercise list widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.exercise_service = ExerciseService()
        self.current_exercises: List[Exercise] = []
        self.show_machines = config.DEFAULT_SHOW_MACHINES
        self.show_bodyweight = config.DEFAULT_SHOW_BODYWEIGHT
        self.show_stretches = config.DEFAULT_SHOW_STRETCHES

        self._setup_ui()
        logger.info("Initialized exercise list widget")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        main_layout = QVBoxLayout()

        # Filter controls
        filter_layout = QHBoxLayout()

        self.machines_checkbox = QCheckBox("Show Machines")
        self.machines_checkbox.setChecked(self.show_machines)
        self.machines_checkbox.stateChanged.connect(self._on_machines_filter_changed)
        filter_layout.addWidget(self.machines_checkbox)

        self.bodyweight_checkbox = QCheckBox("Show Bodyweight")
        self.bodyweight_checkbox.setChecked(self.show_bodyweight)
        self.bodyweight_checkbox.stateChanged.connect(self._on_bodyweight_filter_changed)
        filter_layout.addWidget(self.bodyweight_checkbox)

        self.stretches_checkbox = QCheckBox("Show Stretches")
        self.stretches_checkbox.setChecked(self.show_stretches)
        self.stretches_checkbox.stateChanged.connect(self._on_stretches_filter_changed)
        filter_layout.addWidget(self.stretches_checkbox)

        filter_layout.addStretch()

        main_layout.addLayout(filter_layout)

        # Exercise list
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self._on_exercise_selected)
        self.list_widget.itemDoubleClicked.connect(self._on_exercise_double_clicked)
        main_layout.addWidget(self.list_widget)

        self.setLayout(main_layout)

    def _on_machines_filter_changed(self) -> None:
        """Handle machines filter checkbox change."""
        self.show_machines = self.machines_checkbox.isChecked()
        self._refresh_exercises()

    def _on_bodyweight_filter_changed(self) -> None:
        """Handle bodyweight filter checkbox change."""
        self.show_bodyweight = self.bodyweight_checkbox.isChecked()
        self._refresh_exercises()

    def _on_stretches_filter_changed(self) -> None:
        """Handle stretches filter checkbox change."""
        self.show_stretches = self.stretches_checkbox.isChecked()
        self._refresh_exercises()

    def _on_exercise_selected(self) -> None:
        """Handle exercise selection."""
        current_item = self.list_widget.currentItem()
        if current_item:
            exercise = current_item.data(Qt.ItemDataRole.UserRole)
            if exercise:
                self.exercise_selected.emit(exercise)
                logger.debug(f"Selected exercise: {exercise.name}")

    def _on_exercise_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle exercise double-click."""
        exercise = item.data(Qt.ItemDataRole.UserRole)
        if exercise:
            self.exercise_double_clicked.emit(exercise)
            logger.debug(f"Double-clicked exercise: {exercise.name}")

    def _refresh_exercises(self) -> None:
        """Refresh the exercise list with current filters."""
        self.list_widget.clear()

        filtered = self.exercise_service.filter_exercises(
            self.current_exercises,
            show_machines=self.show_machines,
            show_bodyweight=self.show_bodyweight,
            show_stretches=self.show_stretches,
        )

        self._populate_list(filtered)
        logger.debug(f"Refreshed exercise list with {len(filtered)} exercises")

    def _populate_list(self, exercises: List[Exercise]) -> None:
        """
        Populate the list widget with exercises.

        Args:
            exercises: List of exercises to display
        """
        for exercise in exercises:
            item = QListWidgetItem(exercise.name)
            item.setData(Qt.ItemDataRole.UserRole, exercise)
            self.list_widget.addItem(item)

    def set_exercises_for_muscles(self, muscle_ids: List[str]) -> None:
        """
        Set the list of exercises for the given muscles.

        Args:
            muscle_ids: List of muscle IDs to get exercises for
        """
        if not muscle_ids:
            self.current_exercises = []
        else:
            self.current_exercises = self.exercise_service.get_exercises_for_muscles(
                muscle_ids
            )

        self._refresh_exercises()
        logger.debug(f"Set exercises for {len(muscle_ids)} muscles")

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.list_widget.clearSelection()

    def get_exercise_count(self) -> int:
        """
        Get the number of exercises currently displayed.

        Returns:
            Number of exercises in the list
        """
        return self.list_widget.count()

