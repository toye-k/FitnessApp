"""
Models package containing data structures for the fitness exercise application.
"""

from .enums import EquipmentType, MuscleGroup, ExerciseDifficulty, FilterMode
from .muscle import Muscle
from .exercise import Exercise

__all__ = [
    "EquipmentType",
    "MuscleGroup",
    "ExerciseDifficulty",
    "FilterMode",
    "Muscle",
    "Exercise",
]
