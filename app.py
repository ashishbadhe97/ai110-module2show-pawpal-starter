import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session State — persist Owner across Streamlit reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=120)
if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = None

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🐾 PawPal+")
st.markdown("A smart pet care planning assistant that schedules your pet's daily routine.")

# ---------------------------------------------------------------------------
# Sidebar — Owner Settings & Filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    new_name = st.text_input("Owner name", value=owner.name)
    if new_name != owner.name:
        owner.name = new_name

    new_minutes = st.number_input(
        "Available minutes per day", min_value=10, max_value=480,
        value=owner.available_minutes
    )
    if new_minutes != owner.available_minutes:
        owner.available_minutes = new_minutes

    st.divider()
    st.header("🔍 Filter Tasks")

    filter_pet = st.selectbox(
        "Filter by pet",
        ["All pets"] + [p.name for p in owner.pets]
    )
    filter_status = st.selectbox(
        "Filter by status",
        ["All", "Pending only", "Completed only"]
    )
    filter_category = st.selectbox(
        "Filter by category",
        ["All categories"] + list(Task.VALID_CATEGORIES)
    )
    sort_option = st.selectbox(
        "Sort tasks by",
        ["Priority (default)", "Preferred time (HH:MM)"]
    )

# ---------------------------------------------------------------------------
# Add a Pet
# ---------------------------------------------------------------------------
st.subheader("🐾 Manage Pets")

with st.expander("Add a new pet", expanded=not bool(owner.pets)):
    col_pname, col_species, col_age = st.columns(3)
    with col_pname:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col_species:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col_age:
        pet_age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)

    if st.button("Add pet"):
        existing_names = [p.name for p in owner.pets]
        if pet_name in existing_names:
            st.warning(f"A pet named '{pet_name}' already exists.")
        elif not pet_name.strip():
            st.warning("Please enter a pet name.")
        else:
            new_pet = Pet(name=pet_name, species=species, age=pet_age)
            owner.add_pet(new_pet)
            st.success(f"Added {pet_name} the {species}!")
            st.rerun()

if owner.pets:
    cols = st.columns(len(owner.pets))
    for i, pet in enumerate(owner.pets):
        with cols[i]:
            pending = len(pet.pending_tasks())
            total = len(pet.tasks)
            st.metric(f"🐾 {pet.name}", f"{pending} pending", f"{total} total tasks")
            st.caption(f"{pet.species}, {pet.age} yrs")
else:
    st.info("No pets yet. Add one above to get started.")

st.divider()

# ---------------------------------------------------------------------------
# Add a Task
# ---------------------------------------------------------------------------
st.subheader("📝 Add a Task")

if not owner.pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.expander("New task", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            selected_pet_name = st.selectbox("Assign to pet", [p.name for p in owner.pets])
        with col2:
            task_title = st.text_input("Task title", value="Morning walk")

        col3, col4, col5 = st.columns(3)
        with col3:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col4:
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        with col5:
            category = st.selectbox("Category", list(Task.VALID_CATEGORIES))

        col6, col7, col8 = st.columns(3)
        with col6:
            is_mandatory = st.checkbox("Mandatory")
        with col7:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
        with col8:
            scheduled_time = st.text_input("Preferred time (HH:MM)", value="", placeholder="e.g. 08:00")

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
                    scheduled_time=scheduled_time if scheduled_time.strip() else None,
                )
                selected_pet.add_task(new_task)
                st.success(f"Added '{task_title}' to {selected_pet_name}!")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    # ---------------------------------------------------------------------------
    # Task List — with filtering and sorting
    # ---------------------------------------------------------------------------
    st.markdown("### Current Tasks")

    # Collect tasks based on filters
    display_pets = owner.pets if filter_pet == "All pets" else [
        p for p in owner.pets if p.name == filter_pet
    ]

    for pet in display_pets:
        # Apply status filter
        if filter_status == "Pending only":
            tasks = Scheduler.filter_by_status(pet.tasks, completed=False)
        elif filter_status == "Completed only":
            tasks = Scheduler.filter_by_status(pet.tasks, completed=True)
        else:
            tasks = list(pet.tasks)

        # Apply category filter
        if filter_category != "All categories":
            tasks = Scheduler.filter_by_category(tasks, filter_category)

        # Apply sorting
        if sort_option == "Preferred time (HH:MM)":
            tasks = Scheduler.sort_by_time(tasks)

        if tasks:
            with st.expander(f"{pet.name}'s tasks ({len(tasks)})", expanded=True):
                task_data = []
                for t in tasks:
                    task_data.append({
                        "Title": t.title,
                        "Time": t.scheduled_time or "—",
                        "Duration": f"{t.duration_minutes} min",
                        "Priority": t.priority,
                        "Category": t.category,
                        "Mandatory": "✅" if t.is_mandatory else "",
                        "Frequency": t.frequency,
                        "Status": "✅ Done" if t.is_complete else "⏳ Pending",
                    })
                st.table(task_data)

    # Task management buttons
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("Mark all tasks complete"):
            for pet in owner.pets:
                for task in pet.pending_tasks():
                    pet.complete_task(task.title)
            st.success("All tasks marked complete. Recurring tasks regenerated.")
            st.rerun()
    with btn_col2:
        if st.button("Clear all tasks"):
            for pet in owner.pets:
                pet.tasks.clear()
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Generate Schedule
# ---------------------------------------------------------------------------
st.subheader("📅 Daily Schedule")
st.caption("Builds an optimized plan using priority sorting, time constraints, and conflict detection.")

if st.button("🚀 Generate Schedule", type="primary"):
    all_tasks = owner.get_all_pending_tasks()
    if not all_tasks:
        st.warning("No pending tasks to schedule. Add some tasks first!")
    else:
        scheduler = Scheduler(owner)
        schedule = scheduler.generate_schedule()
        st.session_state.last_schedule = schedule

# Display the last generated schedule (persists across reruns)
schedule = st.session_state.last_schedule
if schedule is not None:
    # Conflict warnings — shown prominently at the top
    if schedule.conflicts:
        st.error(f"⚡ **{len(schedule.conflicts)} conflict(s) detected!** "
                 "Review overlapping tasks below.")
        for conflict in schedule.conflicts:
            st.warning(f"⏰ {conflict}")
        st.markdown("---")

    # Metrics row
    m1, m2, m3 = st.columns(3)
    m1.metric("Tasks Scheduled", len(schedule.scheduled_tasks))
    m2.metric("Time Used", f"{schedule.total_minutes_used}/{schedule.total_minutes_available} min")
    utilization = schedule.utilization()
    m3.metric("Utilization", f"{utilization:.0f}%")

    # Utilization feedback
    if utilization >= 90:
        st.success("🎯 Excellent! Your day is well-packed with pet care.")
    elif utilization >= 60:
        st.info("👍 Good schedule coverage. Some room for extra activities.")
    else:
        st.warning("💡 You have spare time — consider adding enrichment or bonding tasks.")

    # Scheduled tasks
    st.markdown("### ✅ Scheduled Tasks")
    for i, st_task in enumerate(schedule.scheduled_tasks, 1):
        start = Schedule._format_time(st_task.start_minute)
        end = Schedule._format_time(st_task.end_minute)
        mandatory_tag = " 🔴 MANDATORY" if st_task.task.is_mandatory else ""

        with st.container():
            st.markdown(
                f"**{i}. [{start} – {end}] {st_task.task.title}** "
                f"({st_task.pet_name}){mandatory_tag}"
            )
            detail_cols = st.columns(4)
            detail_cols[0].caption(f"⏱ {st_task.task.duration_minutes} min")
            detail_cols[1].caption(f"📊 {st_task.task.priority}")
            detail_cols[2].caption(f"📁 {st_task.task.category}")
            detail_cols[3].caption(f"🔄 {st_task.task.frequency}")
            st.info(f"💡 {st_task.reasoning}")

    # Excluded tasks
    if schedule.excluded_tasks:
        st.markdown("### ⚠️ Excluded Tasks")
        st.caption("These tasks didn't fit in your available time budget.")
        for task, pet_name, reason in schedule.excluded_tasks:
            st.warning(f"**{task.title}** ({pet_name}) — {reason}")

    # No conflicts message
    if not schedule.conflicts:
        st.success("✅ No scheduling conflicts detected.")
