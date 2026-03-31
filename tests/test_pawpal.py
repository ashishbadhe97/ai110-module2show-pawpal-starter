"""Tests for PawPal+ scheduling system."""

import pytest
from datetime import date, timedelta
from pawpal_system import Pet, Owner, Task, Scheduler, Schedule, ScheduledTask


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
# Sorting Tests
# ---------------------------------------------------------------------------

class TestSorting:
    """Verify sort_by_time orders tasks by their HH:MM scheduled_time."""

    def test_sort_by_time_orders_correctly(self):
        tasks = [
            Task("Afternoon", 15, "low", "other", scheduled_time="14:00"),
            Task("Morning", 30, "high", "exercise", scheduled_time="07:00"),
            Task("Midday", 10, "medium", "feeding", scheduled_time="12:00"),
        ]
        sorted_tasks = Scheduler.sort_by_time(tasks)
        assert [t.title for t in sorted_tasks] == ["Morning", "Midday", "Afternoon"]

    def test_sort_by_time_no_time_goes_last(self):
        tasks = [
            Task("No time", 10, "high", "other"),
            Task("Has time", 10, "low", "other", scheduled_time="06:00"),
        ]
        sorted_tasks = Scheduler.sort_by_time(tasks)
        assert sorted_tasks[0].title == "Has time"
        assert sorted_tasks[1].title == "No time"

    def test_time_to_minutes(self):
        assert Task.time_to_minutes("08:30") == 510
        assert Task.time_to_minutes("00:00") == 0
        assert Task.time_to_minutes("23:59") == 1439


# ---------------------------------------------------------------------------
# Filtering Tests
# ---------------------------------------------------------------------------

class TestFiltering:
    """Verify filtering by pet name, status, and category."""

    def test_filter_by_pet(self):
        pairs = [
            (Task("Walk", 30, "high", "exercise"), "Mochi"),
            (Task("Feed", 10, "high", "feeding"), "Whiskers"),
            (Task("Play", 15, "medium", "enrichment"), "Mochi"),
        ]
        result = Scheduler.filter_by_pet(pairs, "Mochi")
        assert len(result) == 2
        assert all(p == "Mochi" for _, p in result)

    def test_filter_by_status_pending(self):
        t1 = Task("Walk", 30, "high", "exercise")
        t2 = Task("Feed", 10, "high", "feeding")
        t2.mark_complete()
        result = Scheduler.filter_by_status([t1, t2], completed=False)
        assert len(result) == 1
        assert result[0].title == "Walk"

    def test_filter_by_status_completed(self):
        t1 = Task("Walk", 30, "high", "exercise")
        t2 = Task("Feed", 10, "high", "feeding")
        t2.mark_complete()
        result = Scheduler.filter_by_status([t1, t2], completed=True)
        assert len(result) == 1
        assert result[0].title == "Feed"

    def test_filter_by_category(self):
        tasks = [
            Task("Walk", 30, "high", "exercise"),
            Task("Feed", 10, "high", "feeding"),
            Task("Run", 20, "medium", "exercise"),
        ]
        result = Scheduler.filter_by_category(tasks, "exercise")
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Recurring Task Tests
# ---------------------------------------------------------------------------

class TestRecurringTasks:
    """Verify that completing a recurring task creates the next occurrence."""

    def test_daily_task_creates_next_day(self):
        task = Task("Walk", 30, "high", "exercise", frequency="daily")
        next_task = task.mark_complete()
        assert next_task is not None
        assert next_task.due_date == date.today() + timedelta(days=1)
        assert next_task.is_complete is False

    def test_weekly_task_creates_next_week(self):
        task = Task("Grooming", 60, "low", "grooming", frequency="weekly")
        next_task = task.mark_complete()
        assert next_task is not None
        assert next_task.due_date == date.today() + timedelta(weeks=1)

    def test_once_task_returns_none(self):
        task = Task("Vet visit", 60, "high", "health", frequency="once")
        next_task = task.mark_complete()
        assert next_task is None

    def test_pet_complete_task_adds_next_occurrence(self):
        pet = Pet("Rex", "dog")
        pet.add_task(Task("Walk", 30, "high", "exercise", frequency="daily"))
        assert len(pet.tasks) == 1
        pet.complete_task("Walk")
        assert len(pet.tasks) == 2  # original (completed) + new occurrence
        assert pet.tasks[0].is_complete is True
        assert pet.tasks[1].is_complete is False

    def test_next_occurrence_preserves_attributes(self):
        task = Task("Walk", 30, "high", "exercise", is_mandatory=True,
                     frequency="daily", scheduled_time="07:00")
        next_task = task.mark_complete()
        assert next_task.title == "Walk"
        assert next_task.duration_minutes == 30
        assert next_task.priority == "high"
        assert next_task.is_mandatory is True
        assert next_task.scheduled_time == "07:00"


# ---------------------------------------------------------------------------
# Conflict Detection Tests
# ---------------------------------------------------------------------------

class TestConflictDetection:
    """Verify that overlapping tasks are detected as conflicts."""

    def test_overlapping_tasks_detected(self):
        owner = Owner("Test", available_minutes=120)
        schedule = Schedule(owner)
        t1 = Task("Task A", 30, "high", "exercise")
        t2 = Task("Task B", 20, "high", "feeding")
        schedule.add_task(ScheduledTask(t1, "Mochi", 0, 30))
        schedule.add_task(ScheduledTask(t2, "Whiskers", 15, 35))  # overlaps
        conflicts = Scheduler.detect_conflicts(schedule)
        assert len(conflicts) == 1
        assert "Task A" in conflicts[0]
        assert "Task B" in conflicts[0]

    def test_adjacent_tasks_no_conflict(self):
        owner = Owner("Test", available_minutes=120)
        schedule = Schedule(owner)
        t1 = Task("Task A", 30, "high", "exercise")
        t2 = Task("Task B", 20, "high", "feeding")
        schedule.add_task(ScheduledTask(t1, "Mochi", 0, 30))
        schedule.add_task(ScheduledTask(t2, "Whiskers", 30, 50))  # starts right after
        conflicts = Scheduler.detect_conflicts(schedule)
        assert len(conflicts) == 0

    def test_no_conflicts_in_normal_schedule(self):
        """The greedy scheduler should never produce overlapping tasks."""
        owner = Owner("Test", available_minutes=120)
        pet = Pet("Rex", "dog")
        pet.add_task(Task("A", 30, "high", "exercise"))
        pet.add_task(Task("B", 20, "medium", "feeding"))
        pet.add_task(Task("C", 15, "low", "grooming"))
        owner.add_pet(pet)
        schedule = Scheduler(owner).generate_schedule()
        assert len(schedule.conflicts) == 0


# ---------------------------------------------------------------------------
# Scheduler Core Tests
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
