"""
Muscle data model and related classes.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .enums import MuscleGroup


@dataclass
class Muscle:
    """
    Represents a muscle group in the human body.

    Attributes:
        id: Unique identifier for the muscle
        name: Display name of the muscle
        muscle_group: The muscle group category this belongs to
        anatomical_location: Description of where the muscle is located
        description: Detailed description of the muscle
        color: Hex color code for visualization (#RRGGBB)
        mesh_vertices: List of vertex indices for 3D mesh representation
        mesh_faces: List of face indices for 3D mesh representation
        aliases: Alternative names for the muscle
    """

    id: str
    name: str
    muscle_group: MuscleGroup
    anatomical_location: str
    description: str
    color: str
    mesh_vertices: List[int] = field(default_factory=list)
    mesh_faces: List[List[int]] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate muscle data after initialization."""
        if not self.id:
            raise ValueError("Muscle ID cannot be empty")
        if not self.name:
            raise ValueError("Muscle name cannot be empty")
        if not self.color.startswith("#"):
            raise ValueError(f"Invalid color format: {self.color}")

    def to_dict(self) -> dict:
        """Convert muscle to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "muscle_group": self.muscle_group.value,
            "anatomical_location": self.anatomical_location,
            "description": self.description,
            "color": self.color,
            "mesh_vertices": self.mesh_vertices,
            "mesh_faces": self.mesh_faces,
            "aliases": self.aliases,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Muscle":
        """Create a Muscle instance from a dictionary."""
        data_copy = data.copy()
        if isinstance(data_copy.get("muscle_group"), str):
            data_copy["muscle_group"] = MuscleGroup(data_copy["muscle_group"])
        return cls(**data_copy)
