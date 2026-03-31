"""PawPal+ Backend System — Core classes for pet care scheduling."""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data Classes (clean, lightweight objects from UML)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet being cared for."""

    name: str
    species: str  # "dog", "cat", "other"
    age: Optional[int] = None
    special_needs: list[str] = field(default_factory=list)


@dataclass
class Owner:
    """Represents the pet owner with a daily time budget."""

    name: str
    available_minutes: int = 120  # daily time budget for pet care


class Task:
    """Represents a single pet care activity."""

    VALID_PRIORITIES = ("high", "medium", "low")
    VALID_CATEGORIES = ("health", "exercise", "feeding", "grooming", "enrichment", "other")

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        category: str = "other",
        is_mandatory: bool = False,
    ):
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of {self.VALID_PRIORITIES}")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_mandatory = is_mandatory

    def __repr__(self) -> str:
        return f"Task({self.title!r}, {self.duration_minutes}min, {self.priority})"


@dataclass
class ScheduledTask:
    """A Task placed into a specific time slot with reasoning."""

    task: Task
    start_minute: int
    end_minute: int
    reasoning: str = ""


# ---------------------------------------------------------------------------
# Schedule — holds the complete daily plan
# ---------------------------------------------------------------------------

class Schedule:
    """The complete daily schedule produced by the Scheduler."""

    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: list[ScheduledTask] = []
        self.excluded_tasks: list[tuple[Task, str]] = []  # (task, reason)
        self.total_minutes_used: int = 0
        self.total_minutes_available: int = owner.available_minutes

    def add_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task to the plan."""
        # TODO: implement in next step
        pass

    def add_excluded(self, task: Task, reason: str) -> None:
        """Record a task that was excluded from the schedule."""
        # TODO: implement in next step
        pass

    def utilization(self) -> float:
        """Return the percentage of available time used."""
        # TODO: implement in next step
        pass

    def summary(self) -> str:
        """Return a formatted string showing the full daily plan."""
        # TODO: implement in next step
        pass


# ---------------------------------------------------------------------------
# Scheduler — the core algorithm
# ---------------------------------------------------------------------------

class Scheduler:
    """Builds an optimized daily Schedule from Owner, Pet, and Task inputs."""

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_schedule(self) -> Schedule:
        """Core algorithm: sort, prioritize, and fit tasks into available time."""
        # TODO: implement in next step
        pass

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (high → medium → low), stable sort."""
        # TODO: implement in next step
        pass

    def _generate_reasoning(self, task: Task, position: int, is_mandatory: bool) -> str:
        """Build a human-readable explanation for why a task was scheduled."""
        # TODO: implement in next step
        pass
