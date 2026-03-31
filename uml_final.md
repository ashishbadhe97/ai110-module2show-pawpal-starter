# PawPal+ Final UML Class Diagram

```mermaid
classDiagram
    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +bool is_mandatory
        +String frequency
        +String scheduled_time
        +date due_date
        +bool is_complete
        +mark_complete() Optional~Task~
        +mark_incomplete() void
        +time_to_minutes(String) int
        -_create_next_occurrence() Optional~Task~
        -_validate_time_format(String) void
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~String~ special_needs
        +List~Task~ tasks
        +add_task(Task) void
        +remove_task(String) bool
        +pending_tasks() List~Task~
        +complete_task(String) Optional~Task~
    }

    class Owner {
        +String name
        +int available_minutes
        +List~Pet~ pets
        +add_pet(Pet) void
        +get_all_tasks() List~Task~
        +get_all_pending_tasks() List~Task~
    }

    class ScheduledTask {
        +Task task
        +String pet_name
        +int start_minute
        +int end_minute
        +String reasoning
    }

    class Schedule {
        +Owner owner
        +List~ScheduledTask~ scheduled_tasks
        +List~Tuple~ excluded_tasks
        +List~String~ conflicts
        +int total_minutes_used
        +int total_minutes_available
        +add_task(ScheduledTask) void
        +add_excluded(Task, String, String) void
        +utilization() float
        +summary() String
        +_format_time(int) String
    }

    class Scheduler {
        +Owner owner
        +generate_schedule() Schedule
        +sort_by_time(List~Task~) List~Task~
        +filter_by_pet(List, String) List
        +filter_by_status(List~Task~, bool) List~Task~
        +filter_by_category(List~Task~, String) List~Task~
        +detect_conflicts(Schedule) List~String~
        -_sort_task_pairs(List) List
        -_generate_reasoning(Task, String, int) String
    }

    Owner "1" --> "1..*" Pet : manages
    Pet "1" --> "*" Task : contains
    Scheduler --> Owner : reads pets & tasks from
    Scheduler --> Schedule : produces
    Schedule "1" --> "*" ScheduledTask : contains
    Schedule "1" --> "*" Task : excludes (with reason)
    ScheduledTask --> Task : wraps with time slot
    Task ..> Task : creates next occurrence (recurring)
```

## Changes from Initial UML

1. **Task gained new attributes**: `frequency`, `scheduled_time` (HH:MM), `due_date`, `is_complete` — all added during Phase 3 for recurring tasks and time-based sorting.
2. **Task gained methods**: `mark_complete()` now returns the next occurrence, `_create_next_occurrence()` uses `timedelta`, `time_to_minutes()` for sort key.
3. **Pet gained `complete_task()`**: Handles marking complete + auto-adding the recurring next occurrence.
4. **Pet now holds tasks directly** (composition) — initial UML had tasks passed separately to Scheduler.
5. **Owner now holds pets** and provides `get_all_tasks()` / `get_all_pending_tasks()` — Scheduler retrieves tasks through Owner → Pets chain.
6. **Scheduler gained static methods**: `sort_by_time()`, `filter_by_pet()`, `filter_by_status()`, `filter_by_category()`, `detect_conflicts()`.
7. **Schedule gained `conflicts` list** — populated by `detect_conflicts()` during schedule generation.
8. **ScheduledTask gained `pet_name`** — needed since tasks come from multiple pets.
