"""
Data loading module for exercises and muscle information.
Handles JSON file loading and conversion to data models.
"""

import json
import os
from typing import List, Optional
from pathlib import Path

from src.models import Exercise, Muscle


class DataLoader:
    """
    Handles loading and caching of exercise and muscle data.
    Implements singleton pattern to ensure single data instance.
    """

    _instance: Optional["DataLoader"] = None
    _exercises: Optional[List[Exercise]] = None
    _muscles: Optional[List[Muscle]] = None

    def __new__(cls) -> "DataLoader":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize data loader."""
        self.data_dir = Path("data")
        self.exercises_file = self.data_dir / "exercise_data.json"
        self.muscles_file = self.data_dir / "muscle_data.json"

    def load_exercises(self) -> List[Exercise]:
        """
        Load exercises from JSON file.

        Returns:
            List of Exercise objects

        Raises:
            FileNotFoundError: If exercise data file not found
            json.JSONDecodeError: If JSON is invalid
        """
        if self._exercises is not None:
            return self._exercises

        if not self.exercises_file.exists():
            raise FileNotFoundError(f"Exercise data file not found: {self.exercises_file}")

        with open(self.exercises_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        exercises = []
        for item in data.get("exercises", []):
            try:
                exercise = Exercise.from_dict(item)
                exercises.append(exercise)
            except ValueError as e:
                print(f"Warning: Skipping invalid exercise {item.get('id', 'unknown')}: {e}")

        self._exercises = exercises
        return exercises

    def load_muscles(self) -> List[Muscle]:
        """
        Load muscles from JSON file.

        Returns:
            List of Muscle objects

        Raises:
            FileNotFoundError: If muscle data file not found
            json.JSONDecodeError: If JSON is invalid
        """
        if self._muscles is not None:
            return self._muscles

        if not self.muscles_file.exists():
            raise FileNotFoundError(f"Muscle data file not found: {self.muscles_file}")

        with open(self.muscles_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        muscles = []
        for item in data.get("muscles", []):
            try:
                muscle = Muscle.from_dict(item)
                muscles.append(muscle)
            except ValueError as e:
                print(f"Warning: Skipping invalid muscle {item.get('id', 'unknown')}: {e}")

        self._muscles = muscles
        return muscles

    def get_exercise_by_id(self, exercise_id: str) -> Optional[Exercise]:
        """
        Get a specific exercise by ID.

        Args:
            exercise_id: The exercise ID to find

        Returns:
            Exercise object or None if not found
        """
        exercises = self.load_exercises()
        return next((ex for ex in exercises if ex.id == exercise_id), None)

    def get_muscle_by_id(self, muscle_id: str) -> Optional[Muscle]:
        """
        Get a specific muscle by ID.

        Args:
            muscle_id: The muscle ID to find

        Returns:
            Muscle object or None if not found
        """
        muscles = self.load_muscles()
        return next((m for m in muscles if m.id == muscle_id), None)

    def get_exercises_for_muscles(self, muscle_ids: List[str]) -> List[Exercise]:
        """
        Get all exercises that target any of the given muscle IDs.

        Args:
            muscle_ids: List of muscle IDs to find exercises for

        Returns:
            List of Exercise objects that target the muscles
        """
        exercises = self.load_exercises()
        muscle_set = set(muscle_ids)
        return [
            ex for ex in exercises
            if muscle_set & set(ex.target_muscles + ex.secondary_muscles)
        ]

    def clear_cache(self) -> None:
        """Clear the data cache (forces reload on next access)."""
        self._exercises = None
        self._muscles = None

    @classmethod
    def reset_singleton(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None
        cls._exercises = None
        cls._muscles = None
