"""PawPal+ core domain model.

Class skeleton generated from diagrams/uml.mmd. No scheduling logic yet —
method bodies are stubs to be filled in incrementally.

Convention: times are stored as minutes-since-midnight (ints).
480 == 08:00. Format to "HH:MM" only for display.
Convention: higher priority int == more important.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Task:
    name: str
    duration: int                          # minutes
    priority: int                          # higher == more important
    category: Optional[str] = None         # walk / feeding / meds / grooming
    preferred_time: Optional[int] = None   # minutes since midnight, if fixed
    recurrence: Optional[str] = None       # e.g. "daily", "weekly"
    pet: Optional["Pet"] = None            # back-reference, set on add_task

    def summary(self) -> str:
        """Short human-readable description for display in a plan."""
        pet_part = f"{self.pet.name}: " if self.pet else ""
        time_part = ""
        if self.preferred_time is not None:
            h, m = divmod(self.preferred_time, 60)
            time_part = f" @ {h:02d}:{m:02d}"
        return f"{pet_part}{self.name} ({self.duration} min, priority {self.priority}){time_part}"

    def is_due_today(self, day: date) -> bool:
        """Whether this task should run on the given day.

        For now only "daily" (and None == every day) is supported; "weekly"
        needs an anchor (a start_date/weekday on Task) and is out of scope until
        that field exists.
        """
        return self.recurrence in (None, "daily")


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0
    special_needs: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet. MUST set task.pet = self so the task stays
        attributable after Schedule pools tasks across pets. This is the only
        supported way to set a task's pet back-reference."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet and clear task.pet (avoid a dangling
        back-reference to a pet that no longer lists the task)."""
        self.tasks.remove(task)
        task.pet = None

    def tasks_by_priority(self) -> list[Task]:
        """This pet's tasks, highest priority first."""
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)


@dataclass
class Owner:
    name: str
    day_start: int = 7 * 60                 # 07:00
    day_end: int = 21 * 60                  # 21:00
    preferences: dict = field(default_factory=dict)  # reserved (README "owner preferences"); not yet consumed by Schedule
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Flat list of every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def total_task_load(self) -> int:
        """Sum of all task durations (minutes) across all pets."""
        return sum(task.duration for task in self.all_tasks())


@dataclass
class Schedule:
    owner: Owner
    date: date
    entries: list[tuple[int, Pet, Task]] = field(default_factory=list)  # (start_time, pet, task)
    dropped: list[Task] = field(default_factory=list)                   # didn't fit / bumped out

    def generate(self) -> None:
        """Build the daily plan: collect -> sort -> place anchored -> fill gaps -> drop overflow.

        Idempotent: clears self.entries and self.dropped first, so repeated calls
        (e.g. on every Streamlit rerun) rebuild the plan instead of accumulating
        duplicates.
        """
        self.entries.clear()
        self.dropped.clear()
        tasks = self._collect_tasks()
        sorted_tasks = self._sort_tasks(tasks)
        anchored = [t for t in sorted_tasks if t.preferred_time is not None]
        unanchored = [t for t in sorted_tasks if t.preferred_time is None]
        bumped = self._place_anchored(anchored)
        self._fill_gaps(self._sort_tasks(unanchored + bumped))

    def _collect_tasks(self) -> list[Task]:
        """Gather all due tasks from the owner's pets into one pool.

        Every pooled task must have task.pet set (guaranteed by Pet.add_task);
        assert this so a task added by some other path can't go unattributable.
        """
        pool = []
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.is_due_today(self.date):
                    assert task.pet is not None, (
                        f"Task '{task.name}' has no pet reference — use Pet.add_task() to attach tasks"
                    )
                    pool.append(task)
        return pool

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Deterministic ordering: priority (desc), then duration (asc), then
        insertion order (stable sort) as the final tie-break — so identical
        inputs always produce the same plan (tests depend on this)."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration))

    def _first_free_gap(self, duration: int, after: int) -> Optional[int]:
        """Earliest start time >= `after` where a `duration`-minute task fits
        without overlapping an existing entry or running past owner.day_end.
        Returns None if no such gap exists. Shared by _place_anchored (bumped
        tasks) and _fill_gaps so interval math lives in one place."""
        cursor = max(after, self.owner.day_start)
        while cursor + duration <= self.owner.day_end:
            conflict = False
            for start, _, task in self.entries:
                entry_end = start + task.duration
                if start < cursor + duration and entry_end > cursor:
                    cursor = entry_end
                    conflict = True
                    break
            if not conflict:
                return cursor
        return None

    def _place_anchored(self, tasks: list[Task]) -> list[Task]:
        """Place tasks that have a preferred_time, resolving clashes by priority.
        The loser of a clash loses its anchor and flows into the gap-fill pool.
        Returns the list of bumped tasks."""
        bumped: list[Task] = []
        for task in tasks:
            pt = task.preferred_time
            if pt is None:
                continue
            # reject tasks that fall entirely outside the owner's window
            if pt < self.owner.day_start or pt + task.duration > self.owner.day_end:
                bumped.append(task)
                continue
            # find the first existing entry that overlaps [pt, pt+duration)
            clash_idx = next(
                (
                    i for i, (s, _, t) in enumerate(self.entries)
                    if s < pt + task.duration and s + t.duration > pt
                ),
                None,
            )
            assert task.pet is not None  # guaranteed by _collect_tasks assert
            if clash_idx is None:
                self.entries.append((pt, task.pet, task))
            else:
                existing_task = self.entries[clash_idx][2]
                winner, _ = self._resolve_clash(existing_task, task)
                if winner is task:
                    self.entries[clash_idx] = (pt, task.pet, task)
                    bumped.append(existing_task)
                else:
                    bumped.append(task)
        return bumped

    def _resolve_clash(self, a: Task, b: Task) -> tuple[Task, Task]:
        """Given two tasks contending for the same slot, return (winner, loser).
        Winner = higher priority; tie -> shorter duration; still tied -> `a`
        (caller passes them in a stable order). N-way clashes are resolved by
        folding this pairwise."""
        if a.priority != b.priority:
            return (a, b) if a.priority > b.priority else (b, a)
        if a.duration != b.duration:
            return (a, b) if a.duration <= b.duration else (b, a)
        return a, b  # `a` wins by stable convention

    def _fill_gaps(self, tasks: list[Task]) -> None:
        """Place un-timed (and bumped) tasks into remaining gaps by priority,
        using _first_free_gap; tasks with no gap go to self.dropped."""
        for task in tasks:
            assert task.pet is not None  # guaranteed by _collect_tasks assert
            start = self._first_free_gap(task.duration, self.owner.day_start)
            if start is not None:
                self.entries.append((start, task.pet, task))
            else:
                self.dropped.append(task)

    def explain(self) -> str:
        """Human-readable rationale for what was scheduled and what was dropped."""
        lines = [f"Daily plan for {self.owner.name} — {self.date}"]
        if not self.entries:
            lines.append("  (nothing scheduled)")
        for start, pet, task in sorted(self.entries, key=lambda e: e[0]):
            h, m = divmod(start, 60)
            anchor = " [anchored]" if task.preferred_time == start else ""
            lines.append(
                f"  {h:02d}:{m:02d} — {task.name} for {pet.name}"
                f" ({task.duration} min, priority {task.priority}){anchor}"
            )
        if self.dropped:
            lines.append("Dropped (no time remaining):")
            for task in self.dropped:
                lines.append(
                    f"  {task.name} ({task.duration} min, priority {task.priority})"
                )
        return "\n".join(lines)

    def __str__(self) -> str:
        """Render the plan like the sample output (HH:MM — Task (dur) [priority])."""
        if not self.entries:
            return "No tasks scheduled."
        lines = []
        for start, _, task in sorted(self.entries, key=lambda e: e[0]):
            h, m = divmod(start, 60)
            lines.append(
                f"{h:02d}:{m:02d} — {task.name} ({task.duration} min) [priority: {task.priority}]"
            )
        return "\n".join(lines)
