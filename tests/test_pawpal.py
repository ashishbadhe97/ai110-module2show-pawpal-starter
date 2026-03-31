"""Tests for PawPal+ scheduling system."""

import pytest
from pawpal_system import Pet, Owner, Task, Scheduler


# ---------------------------------------------------------------------------
# Task Completion Tests
# ---------------------------------------------------------------------------

class TestTaskCompletion:
    """Verify that mark_complete() changes the task's status."""

    def test_task_starts_incomplete(self):
        task = Task("Walk", 30, "high", "exercise")
        assert task.is_complete is False

    def test_mark_complete_changes_status(self):
        task = Task("Walk", 30, "high", "exercise")
        task.mark_complete()
        assert task.is_complete is True

    def test_mark_incomplete_resets_status(self):
        task = Task("Walk", 30, "high", "exercise")
        task.mark_complete()
        task.mark_incomplete()
        assert task.is_complete is False


# ---------------------------------------------------------------------------
# Task Addition Tests
# ---------------------------------------------------------------------------

class TestTaskAddition:
    """Verify that adding a task to a Pet increases that pet's task count."""

    def test_pet_starts_with_no_tasks(self):
        pet = Pet(name="Buddy", species="dog")
        assert len(pet.tasks) == 0

    def test_adding_task_increases_count(self):
        pet = Pet(name="Buddy", species="dog")
        pet.add_task(Task("Walk", 30, "high", "exercise"))
        assert len(pet.tasks) == 1

    def test_adding_multiple_tasks(self):
        pet = Pet(name="Buddy", species="dog")
        pet.add_task(Task("Walk", 30, "high", "exercise"))
        pet.add_task(Task("Feed", 10, "high", "feeding"))
        pet.add_task(Task("Brush", 15, "low", "grooming"))
        assert len(pet.tasks) == 3

    def test_remove_task_decreases_count(self):
        pet = Pet(name="Buddy", species="dog")
        pet.add_task(Task("Walk", 30, "high", "exercise"))
        pet.add_task(Task("Feed", 10, "high", "feeding"))
        pet.remove_task("Walk")
        assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Scheduler Tests
# ---------------------------------------------------------------------------

class TestScheduler:
    """Verify core scheduling behaviors."""

    def test_priority_ordering(self):
        owner = Owner("Test", available_minutes=120)
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Low task", 10, "low", "other"))
        pet.add_task(Task("High task", 10, "high", "other"))
        pet.add_task(Task("Medium task", 10, "medium", "other"))
        owner.add_pet(pet)

        schedule = Scheduler(owner).generate_schedule()
        titles = [st.task.title for st in schedule.scheduled_tasks]
        assert titles == ["High task", "Medium task", "Low task"]

    def test_mandatory_tasks_scheduled_first(self):
        owner = Owner("Test", available_minutes=120)
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Optional high", 10, "high", "other", is_mandatory=False))
        pet.add_task(Task("Mandatory low", 10, "low", "other", is_mandatory=True))
        owner.add_pet(pet)

        schedule = Scheduler(owner).generate_schedule()
        assert schedule.scheduled_tasks[0].task.title == "Mandatory low"

    def test_time_constraint_enforcement(self):
        owner = Owner("Test", available_minutes=30)
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Task A", 20, "high", "other"))
        pet.add_task(Task("Task B", 20, "medium", "other"))
        owner.add_pet(pet)

        schedule = Scheduler(owner).generate_schedule()
        assert schedule.total_minutes_used <= 30
        assert len(schedule.excluded_tasks) > 0

    def test_empty_task_list(self):
        owner = Owner("Test", available_minutes=60)
        pet = Pet("Rex", "dog")
        owner.add_pet(pet)

        schedule = Scheduler(owner).generate_schedule()
        assert len(schedule.scheduled_tasks) == 0
        assert schedule.summary() is not None

    def test_completed_tasks_are_excluded_from_schedule(self):
        owner = Owner("Test", available_minutes=120)
        pet = Pet("Rex", "dog")
        task = Task("Walk", 30, "high", "exercise")
        task.mark_complete()
        pet.add_task(task)
        owner.add_pet(pet)

        schedule = Scheduler(owner).generate_schedule()
        assert len(schedule.scheduled_tasks) == 0

    def test_utilization_calculation(self):
        owner = Owner("Test", available_minutes=100)
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Task A", 50, "high", "other"))
        owner.add_pet(pet)

        schedule = Scheduler(owner).generate_schedule()
        assert schedule.utilization() == 50.0

    def test_reasoning_is_generated(self):
        owner = Owner("Test", available_minutes=60)
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Walk", 30, "high", "exercise"))
        owner.add_pet(pet)

        schedule = Scheduler(owner).generate_schedule()
        assert schedule.scheduled_tasks[0].reasoning != ""

    def test_invalid_priority_raises(self):
        with pytest.raises(ValueError):
            Task("Bad task", 10, "urgent", "other")
