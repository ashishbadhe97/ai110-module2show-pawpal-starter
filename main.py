"""PawPal+ CLI Demo — verifies backend logic including sorting, filtering,
recurring tasks, and conflict detection."""

from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler, Schedule


def main():
    # --- Create Owner ---
    owner = Owner(name="Jordan", available_minutes=90)

    # --- Create Pets ---
    mochi = Pet(name="Mochi", species="dog", age=3, special_needs=["high energy"])
    whiskers = Pet(name="Whiskers", species="cat", age=7)

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Add Tasks OUT OF ORDER (to test sorting) ---
    mochi.add_task(Task("Nail trimming", 15, "low", "grooming", scheduled_time="16:00"))
    mochi.add_task(Task("Morning walk", 30, "high", "exercise", is_mandatory=True, scheduled_time="07:00"))
    mochi.add_task(Task("Training session", 20, "medium", "enrichment", scheduled_time="10:00"))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding", is_mandatory=True, scheduled_time="07:30"))

    whiskers.add_task(Task("Vet medication", 5, "high", "health", is_mandatory=True, scheduled_time="08:00"))
    whiskers.add_task(Task("Play with laser", 15, "medium", "enrichment", scheduled_time="14:00"))
    whiskers.add_task(Task("Brush fur", 10, "medium", "grooming", scheduled_time="11:00"))
    whiskers.add_task(Task("Feed wet food", 5, "high", "feeding", is_mandatory=True, scheduled_time="07:30"))

    # ==========================================
    # DEMO 1: Sorting by preferred time
    # ==========================================
    print("\n📌 DEMO 1: Sort tasks by preferred time (HH:MM)")
    print("-" * 50)
    all_tasks = owner.get_all_tasks()
    sorted_tasks = Scheduler.sort_by_time(all_tasks)
    for t in sorted_tasks:
        print(f"  {t.scheduled_time or 'N/A':>5}  {t.title} ({t.priority})")

    # ==========================================
    # DEMO 2: Filtering by pet and status
    # ==========================================
    print("\n📌 DEMO 2: Filter tasks by pet name")
    print("-" * 50)
    task_pairs = [(t, p.name) for p in owner.pets for t in p.tasks]
    mochi_tasks = Scheduler.filter_by_pet(task_pairs, "Mochi")
    print(f"  Mochi's tasks: {[t.title for t, _ in mochi_tasks]}")

    whiskers_tasks = Scheduler.filter_by_pet(task_pairs, "Whiskers")
    print(f"  Whiskers' tasks: {[t.title for t, _ in whiskers_tasks]}")

    print("\n📌 DEMO 2b: Filter by category")
    print("-" * 50)
    feeding_tasks = Scheduler.filter_by_category(all_tasks, "feeding")
    print(f"  Feeding tasks: {[t.title for t in feeding_tasks]}")

    # ==========================================
    # DEMO 3: Recurring tasks
    # ==========================================
    print("\n📌 DEMO 3: Recurring task auto-creation")
    print("-" * 50)
    print(f"  Mochi's task count before completing: {len(mochi.tasks)}")
    print(f"  Completing 'Morning walk' (frequency: daily)...")
    next_task = mochi.complete_task("Morning walk")
    print(f"  Mochi's task count after completing:  {len(mochi.tasks)}")
    if next_task:
        print(f"  Next occurrence created: due {next_task.due_date} (today + 1 day)")
    print(f"  Pending tasks: {len(mochi.pending_tasks())} "
          f"(completed walk excluded, new walk included)")

    # ==========================================
    # DEMO 4: Generate schedule + conflict detection
    # ==========================================
    print("\n📌 DEMO 4: Schedule generation")
    print("-" * 50)
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()
    print(schedule.summary())

    # ==========================================
    # DEMO 5: Force a conflict to demonstrate detection
    # ==========================================
    print("\n📌 DEMO 5: Conflict detection")
    print("-" * 50)
    # Manually create overlapping scheduled tasks to show conflict detection
    from pawpal_system import ScheduledTask
    test_schedule = Schedule(owner)
    t1 = Task("Task A", 30, "high", "exercise", scheduled_time="08:00")
    t2 = Task("Task B", 20, "high", "feeding", scheduled_time="08:15")
    test_schedule.add_task(ScheduledTask(t1, "Mochi", 0, 30))
    test_schedule.add_task(ScheduledTask(t2, "Whiskers", 15, 35))  # overlaps with Task A
    conflicts = Scheduler.detect_conflicts(test_schedule)
    if conflicts:
        print("  Conflicts found:")
        for c in conflicts:
            print(f"    ⚠ {c}")
    else:
        print("  No conflicts detected.")

    # --- Quick stats ---
    print(f"\n  Pets managed: {len(owner.pets)}")
    print(f"  Total tasks: {len(owner.get_all_tasks())}")
    print(f"  Scheduled: {len(schedule.scheduled_tasks)}")
    print(f"  Excluded: {len(schedule.excluded_tasks)}")
    print()


if __name__ == "__main__":
    main()
