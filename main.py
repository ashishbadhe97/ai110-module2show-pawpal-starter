"""PawPal+ CLI Demo — verifies backend logic before connecting to Streamlit."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Create Owner ---
    owner = Owner(name="Jordan", available_minutes=90)

    # --- Create Pets ---
    mochi = Pet(name="Mochi", species="dog", age=3, special_needs=["high energy"])
    whiskers = Pet(name="Whiskers", species="cat", age=7)

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Add Tasks to Mochi (dog) ---
    mochi.add_task(Task("Morning walk", 30, "high", "exercise", is_mandatory=True))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding", is_mandatory=True))
    mochi.add_task(Task("Training session", 20, "medium", "enrichment"))
    mochi.add_task(Task("Nail trimming", 15, "low", "grooming"))

    # --- Add Tasks to Whiskers (cat) ---
    whiskers.add_task(Task("Feed wet food", 5, "high", "feeding", is_mandatory=True))
    whiskers.add_task(Task("Brush fur", 10, "medium", "grooming"))
    whiskers.add_task(Task("Play with laser", 15, "medium", "enrichment"))
    whiskers.add_task(Task("Vet medication", 5, "high", "health", is_mandatory=True))

    # --- Generate and print the schedule ---
    scheduler = Scheduler(owner)
    schedule = scheduler.generate_schedule()
    print(schedule.summary())

    # --- Show quick stats ---
    print(f"  Pets managed: {len(owner.pets)}")
    print(f"  Total tasks: {len(owner.get_all_tasks())}")
    print(f"  Scheduled: {len(schedule.scheduled_tasks)}")
    print(f"  Excluded: {len(schedule.excluded_tasks)}")
    print()


if __name__ == "__main__":
    main()
