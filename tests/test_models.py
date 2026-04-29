"""
Unit tests for data models.
"""

import pytest
from src.models import Muscle, Exercise, MuscleGroup, EquipmentType, ExerciseDifficulty


class TestMuscle:
    """Tests for Muscle model."""

    def test_muscle_creation(self):
        """Test creating a valid muscle."""
        muscle = Muscle(
            id="biceps",
            name="Biceps",
            muscle_group=MuscleGroup.BICEPS,
            anatomical_location="Upper arm",
            description="Bicep muscle",
            color="#FF6B6B",
        )
        assert muscle.id == "biceps"
        assert muscle.name == "Biceps"
        assert muscle.muscle_group == MuscleGroup.BICEPS

    def test_muscle_with_mesh_data(self):
        """Test creating a muscle with mesh data."""
        muscle = Muscle(
            id="chest",
            name="Chest",
            muscle_group=MuscleGroup.CHEST,
            anatomical_location="Thorax",
            description="Chest muscle",
            color="#FF6B6B",
            mesh_vertices=[1, 2, 3, 4, 5],
            mesh_faces=[[1, 2, 3], [4, 5, 6]],
        )
        assert len(muscle.mesh_vertices) == 5
        assert len(muscle.mesh_faces) == 2

    def test_muscle_invalid_id(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Muscle ID cannot be empty"):
            Muscle(
                id="",
                name="Test",
                muscle_group=MuscleGroup.BACK,
                anatomical_location="Test",
                description="Test",
                color="#FF6B6B",
            )

    def test_muscle_invalid_name(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Muscle name cannot be empty"):
            Muscle(
                id="test",
                name="",
                muscle_group=MuscleGroup.BACK,
                anatomical_location="Test",
                description="Test",
                color="#FF6B6B",
            )

    def test_muscle_invalid_color(self):
        """Test that invalid color format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid color format"):
            Muscle(
                id="test",
                name="Test",
                muscle_group=MuscleGroup.BACK,
                anatomical_location="Test",
                description="Test",
                color="FF6B6B",  # Missing #
            )

    def test_muscle_to_dict(self):
        """Test converting muscle to dictionary."""
        muscle = Muscle(
            id="biceps",
            name="Biceps",
            muscle_group=MuscleGroup.BICEPS,
            anatomical_location="Upper arm",
            description="Bicep muscle",
            color="#FF6B6B",
            aliases=["bis", "guns"],
        )
        data = muscle.to_dict()
        assert data["id"] == "biceps"
        assert data["muscle_group"] == "biceps"
        assert data["aliases"] == ["bis", "guns"]

    def test_muscle_from_dict(self):
        """Test creating muscle from dictionary."""
        data = {
            "id": "biceps",
            "name": "Biceps",
            "muscle_group": "biceps",
            "anatomical_location": "Upper arm",
            "description": "Bicep muscle",
            "color": "#FF6B6B",
        }
        muscle = Muscle.from_dict(data)
        assert muscle.id == "biceps"
        assert muscle.muscle_group == MuscleGroup.BICEPS


class TestExercise:
    """Tests for Exercise model."""

    def test_exercise_creation(self):
        """Test creating a valid exercise."""
        exercise = Exercise(
            id="barbell_curl",
            name="Barbell Curl",
            target_muscles=["biceps"],
            equipment=[EquipmentType.BARBELL],
            is_machine_exercise=False,
            difficulty=ExerciseDifficulty.BEGINNER,
            instructions=["Step 1", "Step 2"],
        )
        assert exercise.id == "barbell_curl"
        assert exercise.name == "Barbell Curl"
        assert len(exercise.target_muscles) == 1

    def test_exercise_invalid_id(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Exercise ID cannot be empty"):
            Exercise(
                id="",
                name="Test",
                target_muscles=["biceps"],
                equipment=[EquipmentType.BARBELL],
                is_machine_exercise=False,
                difficulty=ExerciseDifficulty.BEGINNER,
                instructions=["Step 1"],
            )

    def test_exercise_no_target_muscles(self):
        """Test that empty target muscles raises ValueError."""
        with pytest.raises(ValueError, match="must target at least one muscle"):
            Exercise(
                id="test",
                name="Test",
                target_muscles=[],
                equipment=[EquipmentType.BARBELL],
                is_machine_exercise=False,
                difficulty=ExerciseDifficulty.BEGINNER,
                instructions=["Step 1"],
            )

    def test_exercise_no_instructions(self):
        """Test that empty instructions raises ValueError."""
        with pytest.raises(ValueError, match="must have at least one instruction"):
            Exercise(
                id="test",
                name="Test",
                target_muscles=["biceps"],
                equipment=[EquipmentType.BARBELL],
                is_machine_exercise=False,
                difficulty=ExerciseDifficulty.BEGINNER,
                instructions=[],
            )

    def test_exercise_has_equipment(self):
        """Test has_equipment method."""
        with_equipment = Exercise(
            id="curl",
            name="Curl",
            target_muscles=["biceps"],
            equipment=[EquipmentType.BARBELL],
            is_machine_exercise=False,
            difficulty=ExerciseDifficulty.BEGINNER,
            instructions=["Step 1"],
        )
        assert with_equipment.has_equipment() is True

        bodyweight = Exercise(
            id="push_up",
            name="Push-up",
            target_muscles=["chest"],
            equipment=[EquipmentType.BODYWEIGHT],
            is_machine_exercise=False,
            difficulty=ExerciseDifficulty.BEGINNER,
            instructions=["Step 1"],
        )
        # Note: BODYWEIGHT is still equipment, so this should be True
        assert bodyweight.has_equipment() is True

    def test_exercise_get_youtube_url(self):
        """Test getting YouTube URL."""
        exercise = Exercise(
            id="curl",
            name="Curl",
            target_muscles=["biceps"],
            equipment=[EquipmentType.BARBELL],
            is_machine_exercise=False,
            difficulty=ExerciseDifficulty.BEGINNER,
            instructions=["Step 1"],
            youtube_video_id="dQw4w9WgXcQ",
        )
        url = exercise.get_youtube_url()
        assert url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def test_exercise_to_dict(self):
        """Test converting exercise to dictionary."""
        exercise = Exercise(
            id="curl",
            name="Curl",
            target_muscles=["biceps"],
            equipment=[EquipmentType.BARBELL],
            is_machine_exercise=False,
            difficulty=ExerciseDifficulty.BEGINNER,
            instructions=["Step 1"],
        )
        data = exercise.to_dict()
        assert data["id"] == "curl"
        assert data["equipment"] == ["barbell"]
        assert data["difficulty"] == "beginner"

    def test_exercise_from_dict(self):
        """Test creating exercise from dictionary."""
        data = {
            "id": "curl",
            "name": "Curl",
            "target_muscles": ["biceps"],
            "equipment": ["barbell"],
            "is_machine_exercise": False,
            "difficulty": "beginner",
            "instructions": ["Step 1"],
        }
        exercise = Exercise.from_dict(data)
        assert exercise.id == "curl"
        assert exercise.equipment[0] == EquipmentType.BARBELL
        assert exercise.difficulty == ExerciseDifficulty.BEGINNER
