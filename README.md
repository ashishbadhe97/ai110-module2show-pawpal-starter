# PawPal+ 🐾

A smart pet care management app built with Python and Streamlit. PawPal+ helps busy pet owners plan daily care routines by tracking tasks, prioritizing activities, and generating optimized schedules with clear reasoning.

## Features

- **Multi-pet management** — Add and manage multiple pets (dogs, cats, etc.) under one owner profile
- **Smart task scheduling** — A greedy algorithm schedules tasks by mandatory status first, then priority (high → medium → low), fitting within your daily time budget
- **Scheduling reasoning** — Every scheduled and excluded task comes with a human-readable explanation of *why* it was placed or dropped
- **Time-based sorting** — Sort tasks by their preferred `HH:MM` time slot for chronological planning
- **Filtering** — Filter tasks by pet, completion status, or category (health, exercise, feeding, grooming, enrichment)
- **Recurring tasks** — Daily and weekly tasks auto-generate their next occurrence when marked complete, using Python's `timedelta`
- **Conflict detection** — Detects overlapping time slots and displays warnings so owners can resolve scheduling collisions
- **Utilization tracking** — See how much of your available time budget is used, with feedback on schedule density

## Project Structure

```
├── pawpal_system.py      # Backend logic — all classes and scheduling algorithm
├── app.py                # Streamlit UI — connected to backend
├── main.py               # CLI demo script — verifies logic independently
├── tests/
│   └── test_pawpal.py    # 30 pytest tests covering all features
├── uml_final.md          # Final Mermaid.js class diagram
├── reflection.md         # Design decisions and project reflection
└── requirements.txt      # Dependencies (streamlit, pytest)
```

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the CLI demo

```bash
python main.py
```

### Run the Streamlit app

```bash
streamlit run app.py
```

### Run tests

```bash
python -m pytest tests/test_pawpal.py -v
```

## Architecture

The system is built with six classes organized in three layers:

| Layer | Classes | Responsibility |
|-------|---------|---------------|
| **Data models** | `Task`, `Pet`, `Owner` | Hold pet care data with validation |
| **Schedule output** | `ScheduledTask`, `Schedule` | Represent the optimized daily plan |
| **Engine** | `Scheduler` | Greedy algorithm + sorting, filtering, conflict detection |

See [`uml_final.md`](uml_final.md) for the complete Mermaid.js class diagram.

## Smarter Scheduling

The scheduler uses a **greedy algorithm** that:

1. Collects all pending tasks from the owner's pets
2. Partitions into mandatory and optional groups
3. Sorts each group by priority (stable sort)
4. Places tasks sequentially into available time slots
5. Generates reasoning for every scheduling decision
6. Detects any time-slot conflicts and returns warnings

**Tradeoff**: Greedy over knapsack — produces intuitive, priority-ordered results that match how a human would plan their day, even if it doesn't maximize total scheduled time.

