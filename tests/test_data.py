"""
Unit tests for data loading and processing.
"""

import pytest
from src.data import DataProcessor
from src.models import Exercise, EquipmentType, ExerciseDifficulty


class TestDataProcessor:
    """Tests for data processing."""

    @pytest.fixture
    def sample_exercises(self):
        """Create sample exercises for testing."""
        return [
            Exercise(
                id="curl",
                name="Barbell Curl",
                target_muscles=["biceps"],
                equipment=[EquipmentType.BARBELL],
                is_machine_exercise=False,
                difficulty=ExerciseDifficulty.BEGINNER,
                instructions=["Step 1"],
            ),
            Exercise(
                id="push_up",
                name="Push-up",
                target_muscles=["chest"],
                equipment=[EquipmentType.BODYWEIGHT],
                is_machine_exercise=False,
                difficulty=ExerciseDifficulty.BEGINNER,
                instructions=["Step 1"],
            ),
            Exercise(
                id="leg_press",
                name="Leg Press",
                target_muscles=["quadriceps"],
                equipment=[EquipmentType.MACHINE],
                is_machine_exercise=True,
                difficulty=ExerciseDifficulty.BEGINNER,
                instructions=["Step 1"],
            ),
            Exercise(
                id="deadlift",
                name="Deadlift",
                target_muscles=["hamstrings"],
                secondary_muscles=["back"],
                equipment=[EquipmentType.BARBELL],
                is_machine_exercise=False,
                difficulty=ExerciseDifficulty.ADVANCED,
                instructions=["Step 1"],
            ),
        ]

    def test_filter_by_equipment_has_equipment(self, sample_exercises):
        """Test filtering for exercises with equipment."""
        result = DataProcessor.filter_by_equipment(sample_exercises, has_equipment=True)
        assert len(result) == 4  # curl, push_up, leg_press, deadlift
        assert all(ex.has_equipment() for ex in result)

    def test_filter_by_machine_true(self, sample_exercises):
        """Test filtering for machine exercises."""
        result = DataProcessor.filter_by_machine(sample_exercises, is_machine=True)
        assert len(result) == 1
        assert result[0].id == "leg_press"

    def test_filter_by_machine_false(self, sample_exercises):
        """Test filtering for non-machine exercises."""
        result = DataProcessor.filter_by_machine(sample_exercises, is_machine=False)
        assert len(result) == 3
        assert all(not ex.is_machine_exercise for ex in result)

    def test_filter_by_difficulty(self, sample_exercises):
        """Test filtering by difficulty level."""
        result = DataProcessor.filter_by_difficulty(sample_exercises, ["beginner"])
        assert len(result) == 3
        assert all(ex.difficulty.value == "beginner" for ex in result)

    def test_filter_by_muscle_primary_only(self, sample_exercises):
        """Test filtering by primary target muscles."""
        result = DataProcessor.filter_by_muscle(
            sample_exercises, ["biceps"], primary_only=True
        )
        assert len(result) == 1
        assert result[0].id == "curl"

    def test_filter_by_muscle_with_secondary(self, sample_exercises):
        """Test filtering by muscles including secondary."""
        result = DataProcessor.filter_by_muscle(
            sample_exercises, ["back"], primary_only=False
        )
        assert len(result) == 1
        assert result[0].id == "deadlift"

    def test_remove_duplicates(self, sample_exercises):
        """Test removing duplicate exercises."""
        duplicated = sample_exercises + [sample_exercises[0]]
        result = DataProcessor.remove_duplicates(duplicated)
        assert len(result) == 4
        assert result[-1].id == "deadlift"

    def test_sort_by_name(self, sample_exercises):
        """Test sorting exercises by name."""
        result = DataProcessor.sort_by_name(sample_exercises)
        names = [ex.name for ex in result]
        assert names == sorted(names)

    def test_sort_by_difficulty(self, sample_exercises):
        """Test sorting exercises by difficulty."""
        result = DataProcessor.sort_by_difficulty(sample_exercises)
        difficulties = [ex.difficulty.value for ex in result]
        # Check that advanced comes after beginner
        adv_index = difficulties.index("advanced")
        beg_indices = [i for i, d in enumerate(difficulties) if d == "beginner"]
        assert all(i < adv_index for i in beg_indices)

    def test_apply_filters_by_muscle(self, sample_exercises):
        """Test applying multiple filters."""
        result = DataProcessor.apply_filters(
            sample_exercises,
            muscle_ids=["biceps"],
            show_machines=True,
            show_bodyweight=True,
        )
        assert len(result) >= 1
        assert any(ex.id == "curl" for ex in result)

    def test_apply_filters_machines_only(self, sample_exercises):
        """Test filtering for machines only."""
        result = DataProcessor.apply_filters(
            sample_exercises,
            muscle_ids=None,
            show_machines=True,
            show_bodyweight=False,
        )
        # Should filter out bodyweight exercises
        assert all(ex.has_equipment() for ex in result)

    def test_apply_filters_bodyweight_only(self, sample_exercises):
        """Test filtering for bodyweight only."""
        result = DataProcessor.apply_filters(
            sample_exercises,
            muscle_ids=None,
            show_machines=False,
            show_bodyweight=True,
        )
        # Should include push_up
        assert any(ex.id == "push_up" for ex in result)
