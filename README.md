# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

PawPal+ includes several algorithmic features beyond basic task listing:

- **Priority-aware sorting** — Tasks are sorted by priority (high → medium → low) with mandatory tasks always scheduled first, using Python's `sorted()` with a lambda key.
- **Time-based sorting** — `sort_by_time()` orders tasks by their preferred `HH:MM` scheduled time, with unscheduled tasks placed last.
- **Filtering** — Filter tasks by pet name, completion status, or category to quickly find what you need.
- **Recurring tasks** — Daily and weekly tasks automatically create their next occurrence (using `timedelta`) when marked complete, so care routines never fall through the cracks.
- **Conflict detection** — The scheduler checks all scheduled task pairs for overlapping time ranges and returns warning messages instead of crashing, so owners can resolve conflicts manually.
- **Greedy scheduling with reasoning** — A greedy algorithm fits tasks into the owner's available time budget, generating a human-readable explanation for each scheduling decision and each exclusion.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
