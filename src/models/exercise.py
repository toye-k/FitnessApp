"""
Exercise data model and related classes.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .enums import EquipmentType, ExerciseDifficulty


@dataclass
class Exercise:
    """
    Represents a fitness exercise.

    Attributes:
        id: Unique identifier for the exercise
        name: Display name of the exercise
        target_muscles: List of muscle IDs that are the primary targets
        secondary_muscles: List of muscle IDs that are secondarily worked
        equipment: List of equipment types required
        is_machine_exercise: Whether this exercise uses a machine
        difficulty: Exercise difficulty level
        instructions: Step-by-step instructions for performing the exercise
        tips: Additional tips for proper form
        animation_file: Path to animation GIF file
        youtube_video_id: YouTube video ID for tutorial
        description: Brief description of the exercise
    """

    id: str
    name: str
    target_muscles: List[str]
    equipment: List[EquipmentType]
    is_machine_exercise: bool
    difficulty: ExerciseDifficulty
    instructions: List[str]
    secondary_muscles: List[str] = field(default_factory=list)
    tips: List[str] = field(default_factory=list)
    animation_file: Optional[str] = None
    youtube_video_id: Optional[str] = None
    description: str = ""

    def __post_init__(self) -> None:
        """Validate exercise data after initialization."""
        if not self.id:
            raise ValueError("Exercise ID cannot be empty")
        if not self.name:
            raise ValueError("Exercise name cannot be empty")
        if not self.target_muscles:
            raise ValueError("Exercise must target at least one muscle")
        if not self.instructions:
            raise ValueError("Exercise must have at least one instruction")

    def to_dict(self) -> dict:
        """Convert exercise to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "target_muscles": self.target_muscles,
            "secondary_muscles": self.secondary_muscles,
            "equipment": [eq.value for eq in self.equipment],
            "is_machine_exercise": self.is_machine_exercise,
            "difficulty": self.difficulty.value,
            "instructions": self.instructions,
            "tips": self.tips,
            "animation_file": self.animation_file,
            "youtube_video_id": self.youtube_video_id,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Exercise":
        """Create an Exercise instance from a dictionary."""
        data_copy = data.copy()

        # Convert equipment strings to EquipmentType enums
        if "equipment" in data_copy:
            data_copy["equipment"] = [
                EquipmentType(eq) if isinstance(eq, str) else eq
                for eq in data_copy["equipment"]
            ]

        # Convert difficulty string to ExerciseDifficulty enum
        if isinstance(data_copy.get("difficulty"), str):
            data_copy["difficulty"] = ExerciseDifficulty(data_copy["difficulty"])

        return cls(**data_copy)

    def has_equipment(self) -> bool:
        """Check if exercise requires any equipment."""
        return len(self.equipment) > 0

    def get_youtube_url(self) -> Optional[str]:
        """Get full YouTube URL if video ID is available."""
        if self.youtube_video_id:
            return f"https://www.youtube.com/watch?v={self.youtube_video_id}"
        return None
