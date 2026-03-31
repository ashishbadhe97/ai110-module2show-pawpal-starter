"""PawPal+ Backend System — Core classes for pet care scheduling."""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Task — a single pet care activity
# ---------------------------------------------------------------------------

class Task:
    """Represents a single pet care activity with scheduling metadata."""

    VALID_PRIORITIES = ("high", "medium", "low")
    VALID_CATEGORIES = ("health", "exercise", "feeding", "grooming", "enrichment", "other")

    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str = "medium",
        category: str = "other",
        is_mandatory: bool = False,
        frequency: str = "daily",
    ):
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Must be one of {self.VALID_PRIORITIES}")
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of {self.VALID_CATEGORIES}")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.is_mandatory = is_mandatory
        self.frequency = frequency
        self.is_complete = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_complete = True

    def mark_incomplete(self) -> None:
        """Reset this task to incomplete."""
        self.is_complete = False

    def __repr__(self) -> str:
        status = "✓" if self.is_complete else "○"
        return f"Task({status} {self.title!r}, {self.duration_minutes}min, {self.priority})"


# ---------------------------------------------------------------------------
# Pet — holds pet details and its own list of tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    """Represents a pet with its associated care tasks."""

    name: str
    species: str  # "dog", "cat", "other"
    age: Optional[int] = None
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Returns True if found and removed."""
        for i, task in enumerate(self.tasks):
            if task.title == title:
                self.tasks.pop(i)
                return True
        return False

    def pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks."""
        return [t for t in self.tasks if not t.is_complete]


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and provides access to all tasks
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    """Represents the pet owner who manages multiple pets."""

    name: str
    available_minutes: int = 120
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_all_pending_tasks(self) -> list[Task]:
        """Retrieve all incomplete tasks across all pets."""
        pending = []
        for pet in self.pets:
            pending.extend(pet.pending_tasks())
        return pending


# ---------------------------------------------------------------------------
# ScheduledTask — a task placed into a time slot
# ---------------------------------------------------------------------------

@dataclass
class ScheduledTask:
    """A Task placed into a specific time slot with reasoning."""

    task: Task
    pet_name: str
    start_minute: int
    end_minute: int
    reasoning: str = ""


# ---------------------------------------------------------------------------
# Schedule — the complete daily plan
# ---------------------------------------------------------------------------

class Schedule:
    """The complete daily schedule produced by the Scheduler."""

    DAY_START_HOUR = 8  # schedules start at 8:00 AM

    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled_tasks: list[ScheduledTask] = []
        self.excluded_tasks: list[tuple[Task, str, str]] = []  # (task, pet_name, reason)
        self.total_minutes_used: int = 0
        self.total_minutes_available: int = owner.available_minutes

    def add_task(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task and update time tracking."""
        self.scheduled_tasks.append(scheduled_task)
        self.total_minutes_used += scheduled_task.task.duration_minutes

    def add_excluded(self, task: Task, pet_name: str, reason: str) -> None:
        """Record a task that didn't make the schedule."""
        self.excluded_tasks.append((task, pet_name, reason))

    def utilization(self) -> float:
        """Return percentage of available time used (0-100)."""
        if self.total_minutes_available == 0:
            return 0.0
        return (self.total_minutes_used / self.total_minutes_available) * 100

    @staticmethod
    def _format_time(minute_offset: int, start_hour: int = 8) -> str:
        """Convert a minute offset to HH:MM format."""
        total_minutes = start_hour * 60 + minute_offset
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}:{minutes:02d}"

    def summary(self) -> str:
        """Return a formatted string showing the full daily plan."""
        lines = []
        lines.append("=" * 60)
        lines.append(f"  📋 Daily Schedule for {self.owner.name}")
        lines.append(f"  Time budget: {self.total_minutes_used}/{self.total_minutes_available} min "
                      f"({self.utilization():.0f}% utilized)")
        lines.append("=" * 60)

        if not self.scheduled_tasks:
            lines.append("\n  No tasks scheduled.\n")
        else:
            lines.append("")
            for i, st in enumerate(self.scheduled_tasks, 1):
                time_start = self._format_time(st.start_minute)
                time_end = self._format_time(st.end_minute)
                mandatory = " [MANDATORY]" if st.task.is_mandatory else ""
                lines.append(f"  {i}. [{time_start} - {time_end}] {st.task.title} "
                             f"({st.pet_name}){mandatory}")
                lines.append(f"     Priority: {st.task.priority} | "
                             f"Category: {st.task.category} | "
                             f"Duration: {st.task.duration_minutes} min")
                lines.append(f"     Reason: {st.reasoning}")
                lines.append("")

        if self.excluded_tasks:
            lines.append("-" * 60)
            lines.append("  ⚠ Excluded Tasks (not enough time):")
            lines.append("")
            for task, pet_name, reason in self.excluded_tasks:
                lines.append(f"  • {task.title} ({pet_name}) — {reason}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler — the core scheduling algorithm
# ---------------------------------------------------------------------------

class Scheduler:
    """Builds an optimized daily Schedule by retrieving tasks from the Owner's pets."""

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_schedule(self) -> Schedule:
        """Core algorithm: retrieve tasks from owner's pets, sort, and fit into available time."""
        schedule = Schedule(self.owner)

        # Collect all pending tasks paired with their pet name
        task_pet_pairs: list[tuple[Task, str]] = []
        for pet in self.owner.pets:
            for task in pet.pending_tasks():
                task_pet_pairs.append((task, pet.name))

        if not task_pet_pairs:
            return schedule

        # Partition into mandatory and optional
        mandatory = [(t, p) for t, p in task_pet_pairs if t.is_mandatory]
        optional = [(t, p) for t, p in task_pet_pairs if not t.is_mandatory]

        # Sort each group by priority (stable sort preserves insertion order for ties)
        mandatory = self._sort_task_pairs(mandatory)
        optional = self._sort_task_pairs(optional)

        # Mandatory tasks first, then optional
        ordered = mandatory + optional

        # Greedy placement
        current_minute = 0
        position = 0

        for task, pet_name in ordered:
            if current_minute + task.duration_minutes <= self.owner.available_minutes:
                position += 1
                reasoning = self._generate_reasoning(task, pet_name, position)
                scheduled = ScheduledTask(
                    task=task,
                    pet_name=pet_name,
                    start_minute=current_minute,
                    end_minute=current_minute + task.duration_minutes,
                    reasoning=reasoning,
                )
                schedule.add_task(scheduled)
                current_minute += task.duration_minutes
            else:
                remaining = self.owner.available_minutes - current_minute
                if task.duration_minutes > self.owner.available_minutes:
                    reason = (f"Task duration ({task.duration_minutes} min) exceeds "
                              f"total available time ({self.owner.available_minutes} min)")
                else:
                    reason = (f"Not enough time remaining "
                              f"(needs {task.duration_minutes} min, only {remaining} min left)")
                schedule.add_excluded(task, pet_name, reason)

        return schedule

    def _sort_task_pairs(self, pairs: list[tuple[Task, str]]) -> list[tuple[Task, str]]:
        """Sort task-pet pairs by priority (high → medium → low)."""
        return sorted(pairs, key=lambda pair: self.PRIORITY_ORDER[pair[0].priority])

    def _generate_reasoning(self, task: Task, pet_name: str, position: int) -> str:
        """Build a human-readable explanation for scheduling this task."""
        parts = []

        if task.is_mandatory:
            parts.append(f"Mandatory {task.category} task for {pet_name}")
        else:
            parts.append(f"{task.priority.capitalize()}-priority {task.category} task for {pet_name}")

        if position == 1:
            parts.append("scheduled first")
        else:
            parts.append(f"scheduled at position {position}")

        if task.is_mandatory and task.priority == "high":
            parts.append("— critical care item")
        elif task.is_mandatory:
            parts.append("— must be completed today")

        return ", ".join(parts)
