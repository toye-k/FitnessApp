"""
Exercise service providing business logic for exercise operations.
"""

from typing import List, Optional

from src.data import DataLoader, DataProcessor
from src.models import Exercise


class ExerciseService:
    """
    Service layer for exercise operations.
    Consolidates business logic for filtering and retrieving exercises.
    """

    def __init__(self) -> None:
        """Initialize the exercise service."""
        self.data_loader = DataLoader()
        self.data_processor = DataProcessor()

    def get_all_exercises(self) -> List[Exercise]:
        """
        Get all available exercises.

        Returns:
            List of all Exercise objects
        """
        return self.data_loader.load_exercises()

    def get_exercises_for_muscles(
        self, muscle_ids: List[str]
    ) -> List[Exercise]:
        """
        Get exercises that target specific muscles.

        Args:
            muscle_ids: List of muscle IDs to find exercises for

        Returns:
            List of Exercise objects targeting the muscles
        """
        if not muscle_ids:
            return []

        return self.data_loader.get_exercises_for_muscles(muscle_ids)

    def filter_exercises(
        self,
        exercises: List[Exercise],
        show_machines: bool = True,
        show_bodyweight: bool = True,
        show_stretches: bool = True,
    ) -> List[Exercise]:
        """
        Filter exercises by equipment type.

        Args:
            exercises: List of exercises to filter
            show_machines: Whether to include machine exercises
            show_bodyweight: Whether to include bodyweight exercises
            show_stretches: Whether to include stretch exercises

        Returns:
            Filtered list of exercises
        """
        return self.data_processor.apply_filters(
            exercises,
            muscle_ids=None,
            show_machines=show_machines,
            show_bodyweight=show_bodyweight,
            show_stretches=show_stretches,
        )

    def get_exercises_by_muscles_and_filters(
        self,
        muscle_ids: List[str],
        show_machines: bool = True,
        show_bodyweight: bool = True,
        show_stretches: bool = True,
    ) -> List[Exercise]:
        """
        Get exercises for muscles with equipment filtering.

        Args:
            muscle_ids: List of muscle IDs to target
            show_machines: Whether to include machine exercises
            show_bodyweight: Whether to include bodyweight exercises
            show_stretches: Whether to include stretch exercises

        Returns:
            Filtered list of exercises
        """
        if not muscle_ids:
            return []

        return self.data_processor.apply_filters(
            self.get_all_exercises(),
            muscle_ids=muscle_ids,
            show_machines=show_machines,
            show_bodyweight=show_bodyweight,
            show_stretches=show_stretches,
        )

    def get_exercise_by_id(self, exercise_id: str) -> Optional[Exercise]:
        """
        Get a specific exercise by ID.

        Args:
            exercise_id: The exercise ID to retrieve

        Returns:
            Exercise object or None if not found
        """
        return self.data_loader.get_exercise_by_id(exercise_id)

    def get_exercises_by_equipment(
        self, has_equipment: bool
    ) -> List[Exercise]:
        """
        Get exercises filtered by whether they require equipment.

        Args:
            has_equipment: If True, get equipment exercises.
                          If False, get bodyweight exercises.

        Returns:
            Filtered list of exercises
        """
        all_exercises = self.get_all_exercises()
        return self.data_processor.filter_by_equipment(all_exercises, has_equipment)

    def get_exercises_by_difficulty(
        self, difficulty_levels: List[str]
    ) -> List[Exercise]:
        """
        Get exercises filtered by difficulty level.

        Args:
            difficulty_levels: List of difficulty level values (e.g., ["beginner", "intermediate"])

        Returns:
            Filtered list of exercises
        """
        all_exercises = self.get_all_exercises()
        return self.data_processor.filter_by_difficulty(all_exercises, difficulty_levels)

    def validate_muscle_ids(self, muscle_ids: List[str]) -> bool:
        """
        Validate that all muscle IDs are valid.

        Args:
            muscle_ids: List of muscle IDs to validate

        Returns:
            True if all IDs are valid, False otherwise
        """
        if not muscle_ids:
            return False

        muscles = self.data_loader.load_muscles()
        valid_ids = {m.id for m in muscles}
        return all(m_id in valid_ids for m_id in muscle_ids)
