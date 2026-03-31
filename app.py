import streamlit as st

# Step 1: Import backend classes into the UI
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Step 2: Use session_state to persist the Owner across reruns.
# Streamlit reruns the entire script on every interaction, so without
# session_state our Owner (and all pets/tasks) would be lost on each click.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🐾 PawPal+")
st.markdown("A smart pet care planning assistant that schedules your pet's daily routine.")

# ---------------------------------------------------------------------------
# Owner Settings
# ---------------------------------------------------------------------------
st.subheader("👤 Owner Info")

col_name, col_time = st.columns(2)
with col_name:
    new_name = st.text_input("Owner name", value=owner.name)
    if new_name != owner.name:
        owner.name = new_name
with col_time:
    new_minutes = st.number_input(
        "Available minutes per day", min_value=10, max_value=480,
        value=owner.available_minutes
    )
    if new_minutes != owner.available_minutes:
        owner.available_minutes = new_minutes

st.divider()

# ---------------------------------------------------------------------------
# Add a Pet  (Step 3: wires the form to Owner.add_pet / Pet constructor)
# ---------------------------------------------------------------------------
st.subheader("🐾 Add a Pet")

col_pname, col_species, col_age = st.columns(3)
with col_pname:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col_age:
    pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)

if st.button("Add pet"):
    # Check for duplicate names
    existing_names = [p.name for p in owner.pets]
    if pet_name in existing_names:
        st.warning(f"A pet named '{pet_name}' already exists.")
    elif not pet_name.strip():
        st.warning("Please enter a pet name.")
    else:
        new_pet = Pet(name=pet_name, species=species, age=pet_age)
        owner.add_pet(new_pet)
        st.success(f"Added {pet_name} the {species}!")

# Show current pets
if owner.pets:
    st.markdown("**Your pets:**")
    for pet in owner.pets:
        needs = f" | Needs: {', '.join(pet.special_needs)}" if pet.special_needs else ""
        st.write(f"• **{pet.name}** ({pet.species}, {pet.age} yrs) "
                 f"— {len(pet.tasks)} tasks{needs}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Add a Task to a Pet  (Step 3: wires the form to Pet.add_task / Task constructor)
# ---------------------------------------------------------------------------
st.subheader("📝 Add a Task")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    pet_options = [p.name for p in owner.pets]
    col1, col2 = st.columns(2)
    with col1:
        selected_pet_name = st.selectbox("Assign to pet", pet_options)
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")

    col3, col4, col5 = st.columns(3)
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col4:
        priority = st.selectbox("Priority", ["high", "medium", "low"])
    with col5:
        category = st.selectbox("Category", list(Task.VALID_CATEGORIES))

    col6, col7 = st.columns(2)
    with col6:
        is_mandatory = st.checkbox("Mandatory task")
    with col7:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])

    if st.button("Add task"):
        selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        try:
            new_task = Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                is_mandatory=is_mandatory,
                frequency=frequency,
            )
            selected_pet.add_task(new_task)
            st.success(f"Added '{task_title}' to {selected_pet_name}!")
        except ValueError as e:
            st.error(str(e))

    # Show tasks per pet
    st.markdown("### Current Tasks")
    for pet in owner.pets:
        if pet.tasks:
            with st.expander(f"{pet.name}'s tasks ({len(pet.tasks)})"):
                task_data = []
                for t in pet.tasks:
                    task_data.append({
                        "Title": t.title,
                        "Duration": f"{t.duration_minutes} min",
                        "Priority": t.priority,
                        "Category": t.category,
                        "Mandatory": "Yes" if t.is_mandatory else "No",
                        "Status": "Done" if t.is_complete else "Pending",
                    })
                st.table(task_data)

    if st.button("Clear all tasks"):
        for pet in owner.pets:
            pet.tasks.clear()
        st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Generate Schedule  (Step 3: wires the button to Scheduler.generate_schedule)
# ---------------------------------------------------------------------------
st.subheader("📅 Generate Schedule")
st.caption("Builds an optimized daily plan based on your pets' tasks and your time budget.")

if st.button("Generate schedule"):
    all_tasks = owner.get_all_pending_tasks()
    if not all_tasks:
        st.warning("No pending tasks to schedule. Add some tasks first!")
    else:
        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()

        # Metrics row
        m1, m2, m3 = st.columns(3)
        m1.metric("Tasks Scheduled", len(schedule.scheduled_tasks))
        m2.metric("Time Used", f"{schedule.total_minutes_used} / {schedule.total_minutes_available} min")
        m3.metric("Utilization", f"{schedule.utilization():.0f}%")

        # Scheduled tasks table
        st.markdown("### ✅ Scheduled Tasks")
        for i, st_task in enumerate(schedule.scheduled_tasks, 1):
            start = schedule._format_time(st_task.start_minute)
            end = schedule._format_time(st_task.end_minute)
            mandatory_tag = " 🔴" if st_task.task.is_mandatory else ""
            st.markdown(
                f"**{i}. [{start} – {end}] {st_task.task.title}** "
                f"({st_task.pet_name}){mandatory_tag}"
            )
            st.caption(
                f"Priority: {st_task.task.priority} | "
                f"Category: {st_task.task.category} | "
                f"Duration: {st_task.task.duration_minutes} min"
            )
            st.info(f"💡 {st_task.reasoning}")

        # Excluded tasks
        if schedule.excluded_tasks:
            st.markdown("### ⚠️ Excluded Tasks")
            for task, pet_name, reason in schedule.excluded_tasks:
                st.warning(f"**{task.title}** ({pet_name}) — {reason}")
