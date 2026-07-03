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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Today's Schedule — 2026-07-02
========================================
07:00 — Flea meds (5 min) [priority: 5]
07:05 — Playtime (20 min) [priority: 2]
07:30 — Morning feeding (5 min) [priority: 4]
08:00 — Morning walk (30 min) [priority: 3]
08:30 — Breakfast (10 min) [priority: 4]
08:40 — Evening walk (30 min) [priority: 3]
18:00 — Evening feeding (5 min) [priority: 4]

Daily plan for Jordan — 2026-07-02
  07:00 — Flea meds for Biscuit (5 min, priority 5)
  07:05 — Playtime for Mochi (20 min, priority 2)
  07:30 — Morning feeding for Mochi (5 min, priority 4) [anchored]
  08:00 — Morning walk for Biscuit (30 min, priority 3) [anchored]
  08:30 — Breakfast for Biscuit (10 min, priority 4) [anchored]
  08:40 — Evening walk for Biscuit (30 min, priority 3)
  18:00 — Evening feeding for Mochi (5 min, priority 4) [anchored]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
collected 7 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 14%]
tests/test_pawpal.py::test_mark_complete_daily_spawns_next_task PASSED   [ 28%]
tests/test_pawpal.py::test_mark_complete_weekly_spawns_next_task PASSED  [ 42%]
tests/test_pawpal.py::test_mark_complete_non_recurring_returns_none PASSED [ 57%]
tests/test_pawpal.py::test_mark_complete_without_pet_no_spawn PASSED     [ 71%]
tests/test_pawpal.py::test_is_due_today_uses_due_date PASSED             [ 85%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [100%]

============================== 7 passed in 0.02s ===============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Description |
|---------|-----------|-------------|
| **Time-ordered view** | `Schedule.sort_by_time()` | Returns all scheduled tasks sorted by assigned start time ascending. Useful for displaying the plan chronologically after `generate()` packs tasks by priority. |
| **Task filtering** | `Schedule.filter_tasks(completed, pet_name)` | Filters scheduled tasks by completion status, pet name, or both combined. Passing `completed=False` shows what still needs doing; `pet_name="Biscuit"` narrows results to one pet's tasks. |
| **Conflict detection** | `Schedule.detect_conflicts()` | Scans all scheduled entries for overlapping time windows and returns a list of human-readable warning strings — one per conflict — without raising. Labels each conflict as same-pet or different-pets. |
| **Recurring tasks** | `Task.mark_complete()` | Marking a recurring task complete (`recurrence="daily"` or `"weekly"`) automatically creates and registers the next occurrence with its pet, advancing `due_date` by 1 or 7 days. |

### Conflict detection example

Two tasks are forced to overlap (Biscuit's 60-min vet visit at 10:00 and Mochi's 45-min grooming at 10:20) to demonstrate the warning output:

```
Conflict Detection:
----------------------------------------
  WARNING: Conflict (different pets) — 'Vet checkup' for Biscuit @ 10:00 overlaps 'Grooming session' for Mochi @ 10:20
```

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
