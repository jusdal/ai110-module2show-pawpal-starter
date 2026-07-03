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
python -m pytest tests/test_pawpal.py -v

# Run with coverage:
python -m pytest --cov
```

### What the tests cover

| Area | Tests |
|------|-------|
| **Task lifecycle** | Marking a task complete flips `completed`; non-recurring tasks return `None` |
| **Recurrence logic** | `daily` spawns next task +1 day; `weekly` +7 days; unknown recurrence (e.g. `"monthly"`) does not spawn; missing `due_date` falls back to `date.today()` |
| **Sorting correctness** | `sort_by_time()` returns scheduled tasks in chronological order regardless of insertion order |
| **Conflict detection** | Overlapping entries produce a `WARNING` string; back-to-back entries (end == start) are not flagged; empty schedule returns no warnings |
| **Pet & task wiring** | `add_task` sets the back-reference and grows `pet.tasks`; `is_due_today` respects `due_date` over recurrence type |

### Test run output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/justindaly/codepath/ai110-module2show-pawpal-starter
collected 13 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  7%]
tests/test_pawpal.py::test_mark_complete_daily_spawns_next_task PASSED   [ 15%]
tests/test_pawpal.py::test_mark_complete_weekly_spawns_next_task PASSED  [ 23%]
tests/test_pawpal.py::test_mark_complete_non_recurring_returns_none PASSED [ 30%]
tests/test_pawpal.py::test_mark_complete_without_pet_no_spawn PASSED     [ 38%]
tests/test_pawpal.py::test_is_due_today_uses_due_date PASSED             [ 46%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 53%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 61%]
tests/test_pawpal.py::test_mark_complete_daily_no_due_date_uses_today PASSED [ 69%]
tests/test_pawpal.py::test_mark_complete_unknown_recurrence_returns_none PASSED [ 76%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_tasks PASSED [ 84%]
tests/test_pawpal.py::test_detect_conflicts_back_to_back_not_flagged PASSED [ 92%]
tests/test_pawpal.py::test_detect_conflicts_empty_schedule_returns_no_warnings PASSED [100%]

============================== 13 passed in 0.02s ==============================
```

### Confidence Level: ★★★★☆ (4/5)

The core task lifecycle, recurrence logic, sort ordering, and conflict detection are all exercised — including key edge cases (missing due date, unknown recurrence, back-to-back entries). The scheduling pipeline internals (`_place_anchored`, `_fill_gaps`, clash resolution winner/loser, tasks dropped for lack of time) are not yet covered by unit tests, which is where the remaining uncertainty lives.

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
