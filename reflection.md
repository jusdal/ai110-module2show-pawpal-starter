# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML centered on four classes:

- **Owner** — the person using the app. Holds basic info, preferences, and the time available in a day. Owns one or more `Pet`s.
- **Pet** — basic identity (name, species, breed, age) plus the list of care `Task`s that belong to it. Responsible for managing its own tasks (`add_task()` / `remove_task()`).
- **Task** — a single care activity with a `duration` and a `priority`. This was the data the scheduler would sort and filter on.
- **Schedule** — the planner and the output. Given an owner's tasks and time budget, `generate()` would sort tasks by priority, drop the ones that didn't fit the available time, and produce an ordered daily plan it could also explain.

The core relationships were Owner → many Pets → many Tasks, with Schedule consuming the tasks to produce a daily plan. My first version was deliberately simple: a single time budget (total minutes), tasks ordered purely by priority and duration, and no notion of specific times of day — so conflicts couldn't happen yet. I kept `Task`, `Pet`, and `Owner` as dataclasses to cut boilerplate and concentrated the real logic in `Schedule`.

**b. Design changes**

Yes — the design evolved in two significant ways as I thought through real usage.

1. **Single time budget → a full timeline.** I originally gave the owner a single "available minutes" number. Once I decided tasks could have a `preferred_time` (e.g. a morning walk at 08:00), a flat budget wasn't enough — I needed to know *when* the day starts and ends. So `Owner` gained `day_start` and `day_end`, and I standardized on storing all times as minutes-since-midnight (ints) to keep the slot arithmetic simple.

2. **No conflicts → honor preferred times and bump on clash.** Supporting multiple pets for one owner meant tasks from different pets compete for the same day and could want the same time slot. I extended `Schedule.generate()` into phases: place tasks with preferred times first (resolving clashes by priority via `_resolve_clash()`), then fill the remaining gaps with the untimed tasks. To make this honest for the user, I added a `dropped` list so the plan can show what *didn't* fit and why, rather than silently discarding tasks. I also added a `pet` back-reference on `Task` so a task can still be identified after being pooled across all of the owner's pets.

A review of the skeleton (before writing any logic) surfaced several refinements I folded in while the changes were still cheap:

- **Made `generate()` idempotent.** It now clears `entries` and `dropped` at the start, so the repeated calls a Streamlit app makes on every rerun rebuild the plan instead of accumulating duplicate entries.
- **Extracted a shared `_first_free_gap()` helper.** Both anchored placement (for bumped tasks) and gap-filling need the same "where does a task of this duration fit without overlapping?" interval math, so I centralized it in one method rather than duplicating it.
- **Changed `_resolve_clash()` to return `(winner, loser)`** instead of just the winner. The earlier signature threw away the bumped task, but the loser needs to flow back into the gap-fill pool, so the caller now receives both.
- **Pinned a deterministic tie-break** in `_sort_tasks()`: priority (desc), then duration (asc), then insertion order. Without a fully specified order, identical inputs could produce different plans and make tests flaky.
- **Tightened the `Task`/`Pet` back-reference contract** so `add_task()` is the only thing that sets `task.pet` and `remove_task()` clears it, preventing dangling references.
- **Scoped recurrence to "daily" for now**, since "weekly" needs an anchor date that the model doesn't yet carry — documented as a deliberate limitation rather than a half-working feature.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

`Schedule.generate()` uses a **greedy, priority-first placement strategy**: tasks are sorted once by priority (descending), and each task is placed at the earliest valid time slot — its `preferred_time` if that slot is free, otherwise the first gap that fits. Once a task is placed, that decision is never revisited.

This means the scheduler can miss more globally efficient arrangements. For example: a high-priority 60-minute vet visit placed at 08:00 blocks two lower-priority 30-minute tasks that together have a smaller footprint and could have fit if the vet visit had been shifted to 09:00. A look-ahead or backtracking approach could find a better packing, but at the cost of significantly more complex code.

This tradeoff is reasonable for a daily pet care planner for three reasons. First, the input scale is tiny — a typical owner has fewer than 20 tasks per day — so the difference between greedy and optimal is rarely observable in practice. Second, pet care tasks are not freely interchangeable: feeding a pet at 08:30 instead of 10:00 is a real preference, not an optimization variable, and the `preferred_time` field already captures that directly. Third, a greedy algorithm is transparent: users can predict what will happen (highest priority wins) and trust the plan rather than wondering why the scheduler moved a high-priority task to make room for lower-priority ones.

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
