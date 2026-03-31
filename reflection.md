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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
