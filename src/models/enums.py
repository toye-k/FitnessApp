"""
Enumeration definitions for the fitness exercise application.
"""

from enum import Enum, auto


class EquipmentType(Enum):
    """Equipment types for exercises."""
    BARBELL = "barbell"
    DUMBBELL = "dumbbell"
    KETTLEBELL = "kettlebell"
    CABLE = "cable"
    MACHINE = "machine"
    RESISTANCE_BAND = "resistance_band"
    PLATE = "plate"
    BODYWEIGHT = "bodyweight"
    EZ_BAR = "ez_bar"
    MEDICINE_BALL = "medicine_ball"
    TREADMILL = "treadmill"
    STATIONARY_BIKE = "stationary_bike"
    ROWING_MACHINE = "rowing_machine"
    ELLIPTICAL = "elliptical"
    OTHER = "other"
    STRETCH = "stretch"


class MuscleGroup(Enum):
    """Major muscle groups in the human body."""
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    FOREARMS = "forearms"
    WRISTS = "wrists"
    ABS = "abs"
    UPPER_ABS = "upper_abs"
    LOWER_ABS = "lower_abs"
    OBLIQUES = "obliques"
    LOWER_BACK = "lower_back"
    UPPER_BACK = "upper_back"
    QUADRICEPS = "quadriceps"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    GLUTEUS_MAXIMUS = "gluteus_maximus"
    GLUTEUS_MEDIUS = "gluteus_medius"
    GLUTEUS_MINIMUS = "gluteus_minimus"
    CALVES = "calves"
    ADDUCTORS = "adductors"
    ABDUCTORS = "abductors"
    HIP_FLEXORS = "hip_flexors"
    LATS = "lats"
    TRAPS = "traps"
    NECK = "neck"


class ExerciseDifficulty(Enum):
    """Exercise difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class FilterMode(Enum):
    """Filter mode for exercise display."""
    SHOW_ALL = "show_all"
    MACHINE_ONLY = "machine_only"
    BODYWEIGHT_ONLY = "bodyweight_only"
