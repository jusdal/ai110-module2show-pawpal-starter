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

## 🖥️ Streamlit UI Features

The app is launched with:

```bash
streamlit run app.py
```

### Owner setup
Set the owner name and the day's start/end times (defaults: 07:00–21:00). The schedule respects this window — tasks that don't fit before day-end are dropped.

### Pet & task management
- Add pets with name, species, and optional breed.
- Add tasks with title, duration, priority, category, recurrence, and optional preferred time.
- Remove any task directly from the task list. Removing a task clears the stale schedule so you're prompted to regenerate.

### Schedule view
After clicking **Generate schedule**, the UI shows:

- **Summary metrics** — tasks scheduled, completed count, total time, and % of the day used.
- **Conflict warnings** — if two tasks overlap in the final plan, each conflict appears as a yellow warning above the table so it can't be missed.
- **Rescheduled tasks** — tasks that had a preferred time but were moved by the scheduler appear in an expandable section (distinct from unresolved conflicts).
- **Interactive schedule table** — sorted by start time, with columns for Time, Pet, Task, Duration, Priority, and Category. Each row has a checkbox to mark the task complete; checking it strikes through the task name and updates the metrics immediately.
- **Category filter** — narrow the schedule view to a single category (walk, feeding, meds, grooming).
- **Dropped tasks** — tasks that couldn't fit in the day window are listed in a bordered warning block.
- **Why this plan?** — an expandable section that explains the scheduling decisions: how tasks were prioritized, which kept their preferred time, which were moved and why, and which were dropped.

### "Why this plan?" example output

```
How today's plan was built (2026-07-03):

1. Prioritization: tasks were sorted by priority (high → low), then by
duration (shortest first) so more tasks fit when time is tight.

2. Placement: 3 task(s) kept their preferred time (anchored), 0 task(s)
had no preferred time and were fitted into open gaps.

3. Rescheduled (1 task(s) couldn't keep their preferred time):
   - Midori's 'Morning walk': requested 09:45, placed at 07:00
     (preferred slot was taken by a higher- or equal-priority task).

4. All tasks fit — nothing was dropped.
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
| **Pet & task wiring** | `add_task` sets the back-reference and grows `pet.tasks`; `is_due_today` respects `due_date` over recurrence type; `remove_task` removes the task and clears its pet reference |
| **explain() rationale** | Output describes prioritization logic; anchored vs unanchored counts are accurate; moved tasks show original requested time; dropped tasks are named with reason; "all fit" and "no moves" messages appear when appropriate |
| **Pet reference healing** | A task added directly to `pet.tasks` (bypassing `add_task`) has its `pet` reference re-attached during `generate()` without crashing |
| **Owner day window** | Defaults to 07:00–21:00; unanchored tasks start at `day_start`; tasks that can't fit before `day_end` are dropped |
| **filter_tasks** | Filter by pet name; filter by completion status; combined pet + completed filter; no-match returns empty list |

### Test run output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/justindaly/codepath/ai110-module2show-pawpal-starter
collected 29 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  3%]
tests/test_pawpal.py::test_mark_complete_daily_spawns_next_task PASSED   [  6%]
tests/test_pawpal.py::test_mark_complete_weekly_spawns_next_task PASSED  [ 10%]
tests/test_pawpal.py::test_mark_complete_non_recurring_returns_none PASSED [ 13%]
tests/test_pawpal.py::test_mark_complete_without_pet_no_spawn PASSED     [ 17%]
tests/test_pawpal.py::test_is_due_today_uses_due_date PASSED             [ 20%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 24%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 27%]
tests/test_pawpal.py::test_mark_complete_daily_no_due_date_uses_today PASSED [ 31%]
tests/test_pawpal.py::test_mark_complete_unknown_recurrence_returns_none PASSED [ 34%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_tasks PASSED [ 37%]
tests/test_pawpal.py::test_detect_conflicts_back_to_back_not_flagged PASSED [ 41%]
tests/test_pawpal.py::test_detect_conflicts_empty_schedule_returns_no_warnings PASSED [ 44%]
tests/test_pawpal.py::test_explain_describes_prioritization PASSED       [ 48%]
tests/test_pawpal.py::test_explain_counts_anchored_and_unanchored PASSED [ 51%]
tests/test_pawpal.py::test_explain_shows_moved_task_with_times PASSED    [ 55%]
tests/test_pawpal.py::test_explain_shows_dropped_task_with_name PASSED   [ 58%]
tests/test_pawpal.py::test_explain_all_fit_nothing_dropped_message PASSED [ 62%]
tests/test_pawpal.py::test_explain_no_moves_when_all_preferred_times_kept PASSED [ 65%]
tests/test_pawpal.py::test_collect_tasks_heals_missing_pet_reference PASSED [ 68%]
tests/test_pawpal.py::test_owner_day_window_defaults PASSED              [ 72%]
tests/test_pawpal.py::test_unanchored_task_starts_at_day_start PASSED    [ 75%]
tests/test_pawpal.py::test_task_dropped_when_day_window_too_small PASSED [ 79%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED               [ 82%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name_no_match_returns_empty PASSED [ 86%]
tests/test_pawpal.py::test_filter_tasks_by_completed_status PASSED       [ 89%]
tests/test_pawpal.py::test_filter_tasks_combined_pet_name_and_completed PASSED [ 93%]
tests/test_pawpal.py::test_remove_task_removes_from_pet_tasks PASSED     [ 96%]
tests/test_pawpal.py::test_remove_task_clears_pet_reference PASSED       [100%]

29 passed in 0.05s ==============================
```

### Confidence Level: ★★★★★ (5/5)

All core behaviors are exercised — task lifecycle, recurrence, sort ordering, conflict detection, scheduling pipeline internals (day window enforcement, task drop when no gap fits, preferred-time clash resolution), `explain()` rationale content, `filter_tasks` combinations, and the pet back-reference healing fix.

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
