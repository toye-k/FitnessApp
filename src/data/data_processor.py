"""
Data processing module for filtering and transforming exercise data.
"""

from typing import List
from src.models import Exercise, EquipmentType


class DataProcessor:
    """Handles filtering and processing of exercise data."""

    @staticmethod
    def filter_by_equipment(
        exercises: List[Exercise], has_equipment: bool
    ) -> List[Exercise]:
        """
        Filter exercises by whether they require equipment.

        Args:
            exercises: List of exercises to filter
            has_equipment: If True, only return exercises with equipment.
                          If False, only return bodyweight exercises.

        Returns:
            Filtered list of exercises
        """
        return [ex for ex in exercises if ex.has_equipment() == has_equipment]

    @staticmethod
    def filter_by_machine(
        exercises: List[Exercise], is_machine: bool
    ) -> List[Exercise]:
        """
        Filter exercises by machine type.

        Args:
            exercises: List of exercises to filter
            is_machine: If True, only return machine exercises.
                       If False, only return non-machine exercises.

        Returns:
            Filtered list of exercises
        """
        return [ex for ex in exercises if ex.is_machine_exercise == is_machine]

    @staticmethod
    def filter_by_difficulty(
        exercises: List[Exercise], difficulty_levels: List[str]
    ) -> List[Exercise]:
        """
        Filter exercises by difficulty level.

        Args:
            exercises: List of exercises to filter
            difficulty_levels: List of difficulty level values to include

        Returns:
            Filtered list of exercises
        """
        return [
            ex for ex in exercises
            if ex.difficulty.value in difficulty_levels
        ]

    @staticmethod
    def filter_by_muscle(
        exercises: List[Exercise], muscle_ids: List[str], primary_only: bool = False
    ) -> List[Exercise]:
        """
        Filter exercises that work specific muscles.

        Args:
            exercises: List of exercises to filter
            muscle_ids: List of muscle IDs to filter by
            primary_only: If True, only match primary target muscles.
                         If False, match both primary and secondary.

        Returns:
            Filtered list of exercises
        """
        muscle_set = set(muscle_ids)
        result = []

        for exercise in exercises:
            if primary_only:
                if muscle_set & set(exercise.target_muscles):
                    result.append(exercise)
            else:
                target_and_secondary = set(exercise.target_muscles + exercise.secondary_muscles)
                if muscle_set & target_and_secondary:
                    result.append(exercise)

        return result

    @staticmethod
    def remove_duplicates(exercises: List[Exercise]) -> List[Exercise]:
        """
        Remove duplicate exercises by ID.

        Args:
            exercises: List of exercises that may contain duplicates

        Returns:
            List of unique exercises (first occurrence kept)
        """
        seen = set()
        result = []
        for ex in exercises:
            if ex.id not in seen:
                result.append(ex)
                seen.add(ex.id)
        return result

    @staticmethod
    def sort_by_name(exercises: List[Exercise]) -> List[Exercise]:
        """
        Sort exercises alphabetically by name.

        Args:
            exercises: List of exercises to sort

        Returns:
            Sorted list of exercises
        """
        return sorted(exercises, key=lambda ex: ex.name)

    @staticmethod
    def sort_by_difficulty(exercises: List[Exercise]) -> List[Exercise]:
        """
        Sort exercises by difficulty level.

        Args:
            exercises: List of exercises to sort

        Returns:
            Sorted list of exercises (beginner to expert)
        """
        difficulty_order = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}
        return sorted(
            exercises,
            key=lambda ex: difficulty_order.get(ex.difficulty.value, 999)
        )

    @staticmethod
    def apply_filters(
        exercises: List[Exercise],
        muscle_ids: List[str] = None,
        show_machines: bool = True,
        show_bodyweight: bool = True,
        show_stretches: bool = True,
        difficulty_levels: List[str] = None,
    ) -> List[Exercise]:
        """
        Apply multiple filters to exercises.

        Args:
            exercises: List of exercises to filter
            muscle_ids: List of muscle IDs to filter by (None = no filter)
            show_machines: Whether to include machine exercises
            show_bodyweight: Whether to include bodyweight exercises
            show_stretches: Whether to include stretch exercises
            difficulty_levels: List of difficulty levels to include (None = all)

        Returns:
            Filtered list of exercises
        """
        result = exercises

        # Filter by muscle
        if muscle_ids:
            result = DataProcessor.filter_by_muscle(result, muscle_ids, primary_only=False)

        # Filter by exercise category
        if not (show_machines and show_bodyweight and show_stretches):
            def should_show(ex: Exercise) -> bool:
                if EquipmentType.STRETCH in ex.equipment:
                    return show_stretches
                elif EquipmentType.BODYWEIGHT in ex.equipment:
                    return show_bodyweight
                else:
                    return show_machines
            result = [ex for ex in result if should_show(ex)]

        # Filter by difficulty
        if difficulty_levels:
            result = DataProcessor.filter_by_difficulty(result, difficulty_levels)

        # Remove duplicates
        result = DataProcessor.remove_duplicates(result)

        # Sort by name
        result = DataProcessor.sort_by_name(result)

        return result
