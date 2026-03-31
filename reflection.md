# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design consists of six classes organized into three layers: data models, schedule output, and the scheduling engine.

**Data models (inputs):**
- **Pet** (`@dataclass`) — Holds the pet's `name`, `species`, optional `age`, and a list of `special_needs`. Pure data container with no behavior. Using a dataclass keeps it clean and concise.
- **Owner** (`@dataclass`) — Stores the owner's `name` and `available_minutes` (daily time budget). This is the primary constraint the scheduler works against.
- **Task** — Represents a single care activity with `title`, `duration_minutes`, `priority` (high/medium/low), `category` (health, exercise, feeding, etc.), and `is_mandatory` flag. Unlike the dataclasses above, Task uses a regular class because it needs input validation in `__init__` — rejecting invalid priorities and non-positive durations at creation time.

**Schedule output:**
- **ScheduledTask** (`@dataclass`) — Wraps a `Task` with a `start_minute`, `end_minute`, and `reasoning` string. This is the "placed" version of a task — it knows *when* it happens and *why*.
- **Schedule** — The complete daily plan. Holds a list of `ScheduledTask` objects (the plan) and a list of excluded `(Task, reason)` tuples. Provides methods to `add_task()`, `add_excluded()`, calculate `utilization()`, and generate a `summary()` string. This separation lets the UI display both what made the cut and what didn't.

**Scheduling engine:**
- **Scheduler** — The brain of the system. Takes an `Owner`, `Pet`, and list of `Task` objects, then produces a `Schedule`. Its `generate_schedule()` method implements a greedy algorithm: mandatory tasks first, then by priority, fitting into available time. Private helpers `_sort_tasks()` and `_generate_reasoning()` keep the main method clean.

**Key relationships:** Owner → Pet (ownership), Scheduler → (Owner, Pet, Tasks) as inputs, Scheduler → Schedule as output, Schedule → ScheduledTask (composition), ScheduledTask → Task (wraps).

**b. Design changes**

Yes — after reviewing the skeleton with AI assistance, one gap was identified and fixed:

**Added `category` validation to `Task.__init__`.** The original skeleton validated `priority` (rejecting invalid values with a `ValueError`) but did not validate `category`. This was inconsistent — if we define `VALID_CATEGORIES` as a class constant but never enforce it, invalid categories could silently slip through and produce confusing output in the schedule summary. The fix was a single validation check mirroring the priority pattern:

```python
if category not in self.VALID_CATEGORIES:
    raise ValueError(f"Invalid category '{category}'. Must be one of {self.VALID_CATEGORIES}")
```

Other observations from the review (no code changes needed):
- `Schedule.add_task()` must update `total_minutes_used` when implemented — noted for the next step.
- `_generate_reasoning()` can access pet context via `self.pet` on the Scheduler — no signature change required.
- The overall class structure and relationships were confirmed to be sound with no missing classes or unnecessary complexity.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints, ranked by importance:

1. **Mandatory status** — Tasks flagged `is_mandatory` are always scheduled before optional tasks, regardless of priority. This ensures critical care (medication, feeding) never gets bumped by a nice-to-have activity.
2. **Priority (high/medium/low)** — Within each group (mandatory and optional), tasks are sorted high → medium → low using a stable sort so ties preserve insertion order.
3. **Time budget** — The owner's `available_minutes` is a hard ceiling. The greedy algorithm fills time sequentially and excludes any task that doesn't fit in the remaining window.

I decided mandatory status should outrank priority because in pet care, a mandatory low-priority task (e.g., giving daily medication — quick but essential) should never be dropped in favor of an optional high-priority task (e.g., a long training session). Time budget is the final gate because it's a physical constraint that can't be negotiated.

**b. Tradeoffs**

**Tradeoff: Greedy sequential placement vs. knapsack optimization.**

The scheduler uses a greedy algorithm — it places tasks one at a time in priority order until time runs out. A knapsack algorithm could theoretically pack *more total value* into the time budget by skipping a long high-priority task to fit two shorter medium-priority ones.

I chose greedy because it produces **predictable, explainable results**. If a pet owner sees their highest-priority task excluded in favor of two lower-priority ones, that feels wrong — even if it's mathematically optimal. The greedy approach guarantees that the most important tasks are always attempted first, which matches how a human would manually plan their day.

**Tradeoff: Conflict detection checks overlapping duration ranges, not just exact start times.**

The `detect_conflicts()` method compares every pair of scheduled tasks to see if their `[start_minute, end_minute)` ranges overlap. This is O(n²) which is fine for a daily schedule (~10-20 tasks), but would need optimization (e.g., sorting by start time first) for larger task sets. The tradeoff is simplicity and correctness over performance — reasonable given the scale of a pet care app.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used throughout every phase of this project:

1. **Design brainstorming** — I described the PawPal+ scenario and asked AI to help identify the main building blocks (classes, attributes, methods). This produced the initial 6-class architecture. The most helpful prompt was asking AI to generate a Mermaid.js class diagram from my brainstormed attributes, which made relationships visual and easy to validate.

2. **Skeleton generation** — After finalizing the UML, I asked AI to translate the diagram into Python class stubs with appropriate use of `@dataclass` for data containers vs. regular classes for objects needing validation. This saved significant boilerplate time.

3. **Algorithm implementation** — For the scheduling algorithm, I described the constraints (mandatory first, then priority, within a time budget) and AI produced the greedy placement logic. For recurring tasks, asking "how to use `timedelta` to calculate the next occurrence of a daily task" was particularly effective.

4. **Code review** — After each phase, I asked AI to review the skeleton for missing relationships or logic bottlenecks. This caught the missing `category` validation early.

5. **Test generation** — AI helped draft pytest cases for each feature (completion, addition, sorting, filtering, recurring, conflicts), which I then verified by running them.

The most effective prompts were specific and scoped: "Based on my classes in pawpal_system.py, how should the Scheduler retrieve all tasks from the Owner's pets?" worked much better than vague requests.

**b. Judgment and verification**

One key moment: when the initial skeleton was designed, AI suggested passing tasks as a flat list directly to the Scheduler. After reviewing the Phase 3 requirements, I rejected this approach because the instructions specified that Pet should hold its own tasks and Owner should manage multiple pets. I restructured so that Scheduler retrieves tasks by walking the Owner → Pets → Tasks chain, which is more realistic and supports filtering by pet.

I verified AI suggestions by: (1) running `python main.py` after every change to see if the CLI output made sense, (2) running `pytest` after adding tests to confirm behavior, and (3) manually inspecting edge cases (empty task lists, tasks exceeding time, duplicate pet names) to ensure the logic handled them gracefully.

---

## 4. Testing and Verification

**a. What you tested**

30 tests across 7 test classes covering:

- **Task completion** (3 tests) — `mark_complete()` changes status, `mark_incomplete()` resets it. Important because the scheduler filters by completion status; a broken flag means tasks get scheduled or skipped incorrectly.
- **Task addition** (4 tests) — Adding/removing tasks to a Pet changes the count correctly. Important because the Owner → Pet → Task chain is the data backbone of the system.
- **Sorting** (3 tests) — `sort_by_time()` orders tasks chronologically, tasks without a preferred time sort last, and `time_to_minutes()` converts correctly. Important for the UI's "sort by preferred time" feature.
- **Filtering** (4 tests) — Filter by pet, by pending/completed status, by category. Important because the sidebar filters directly call these methods.
- **Recurring tasks** (5 tests) — Daily tasks create next-day occurrences, weekly tasks create next-week, one-time tasks return None, `complete_task()` auto-adds the new occurrence, and all attributes are preserved. Important because recurring tasks are the core automation feature.
- **Conflict detection** (3 tests) — Overlapping tasks are detected, adjacent (non-overlapping) tasks are not flagged, and normal greedy schedules produce zero conflicts. Important because false positives would erode user trust.
- **Scheduler core** (8 tests) — Priority ordering, mandatory-first behavior, time constraint enforcement, empty task list handling, completed task exclusion, utilization calculation, reasoning generation, and invalid priority rejection.

**b. Confidence**

I'm fairly confident the scheduler works correctly for typical use cases — the 30 tests cover the main behaviors and edge cases, and the CLI demo exercises the full pipeline end-to-end.

Edge cases I'd test next with more time:
- Tasks with identical titles across different pets (name collision in `complete_task`)
- Very large task counts (100+) to verify performance of the O(n²) conflict detection
- Boundary values: exactly 0 available minutes, a single 1-minute task, available minutes equal to total task duration
- Concurrent recurring task chains (completing a recurring task that was itself a recurrence)

---

## 5. Reflection

**a. What went well**

The CLI-first workflow was the strongest part of this project. Building and verifying `pawpal_system.py` through `main.py` before touching the Streamlit UI meant that by the time I wired up `app.py`, the backend was already proven and I could focus purely on presentation. The `summary()` method that formats the schedule as a readable terminal string doubled as a debugging tool and a quick demo for stakeholders.

The modular class design also paid off — when Phase 3 required adding sorting, filtering, recurring tasks, and conflict detection, each feature dropped neatly into the existing Scheduler class as a static method without touching the core `generate_schedule()` algorithm.

**b. What you would improve**

If I had another iteration, I would:

1. **Add wall-clock time awareness** — Currently the scheduler uses minute offsets (0, 30, 50...) from an assumed 8:00 AM start. Real users might want to set a start time and see actual clock times in the schedule. The `scheduled_time` field on Task hints at this but isn't fully integrated into the scheduling algorithm.

2. **Replace O(n²) conflict detection** — Sort tasks by start time first, then do a single linear pass comparing each task to the next. This would scale better for power users with many pets and tasks.

3. **Add persistent storage** — Currently all data lives in `st.session_state` and is lost when the browser tab closes. A SQLite database or JSON file would make the app genuinely useful for daily use.

4. **Improve the recurring task UX** — Right now, completing a task silently appends the next occurrence. A notification or visual indicator showing "Next walk scheduled for tomorrow" would make the recurrence more transparent.

**c. Key takeaway**

The most important lesson was that **AI is a powerful collaborator but needs a human architect to steer it**. AI excelled at generating boilerplate, suggesting algorithms, and catching gaps in my design (like the missing category validation). But every structural decision — Pet holding its own tasks, greedy over knapsack, mandatory-first ordering — required human judgment about what would make sense to a real user. The best results came from giving AI clear, scoped prompts grounded in specific files and requirements, then critically evaluating its output before accepting it.
