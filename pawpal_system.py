"""PawPal+ core domain model.

Class skeleton generated from diagrams/uml.mmd. No scheduling logic yet —
method bodies are stubs to be filled in incrementally.

Convention: times are stored as minutes-since-midnight (ints).
480 == 08:00. Format to "HH:MM" only for display.
Convention: higher priority int == more important.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    name: str
    duration: int                          # minutes
    priority: int                          # higher == more important
    category: Optional[str] = None         # walk / feeding / meds / grooming
    preferred_time: Optional[int] = None   # minutes since midnight, if fixed
    recurrence: Optional[str] = None       # e.g. "daily", "weekly"
    due_date: Optional[date] = None        # specific date this instance is due
    pet: Optional["Pet"] = None            # back-reference, set on add_task
    completed: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as done; if recurring, register the next occurrence with the pet."""
        self.completed = True
        if self.recurrence in ("daily", "weekly") and self.pet is not None:
            delta = timedelta(days=1 if self.recurrence == "daily" else 7)
            next_due = (self.due_date or date.today()) + delta
            next_task = Task(
                name=self.name,
                duration=self.duration,
                priority=self.priority,
                category=self.category,
                preferred_time=self.preferred_time,
                recurrence=self.recurrence,
                due_date=next_due,
            )
            self.pet.add_task(next_task)
            return next_task
        return None

    def summary(self) -> str:
        """Short human-readable description for display in a plan."""
        pet_part = f"{self.pet.name}: " if self.pet else ""
        time_part = ""
        if self.preferred_time is not None:
            h, m = divmod(self.preferred_time, 60)
            time_part = f" @ {h:02d}:{m:02d}"
        return f"{pet_part}{self.name} ({self.duration} min, priority {self.priority}){time_part}"

    def is_due_today(self, day: date) -> bool:
        """Return True if this task is due on `day`. Uses due_date when set; falls back to recurrence type."""
        if self.due_date is not None:
            return self.due_date == day
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
        """Attach a task to this pet and set its back-reference; the only supported way to do so."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet and clear its back-reference."""
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
        """Clear and rebuild the daily plan (idempotent): collect → sort → anchor → fill gaps → drop overflow."""
        self.entries.clear()
        self.dropped.clear()
        tasks = self._collect_tasks()
        sorted_tasks = self._sort_tasks(tasks)
        anchored = [t for t in sorted_tasks if t.preferred_time is not None]
        unanchored = [t for t in sorted_tasks if t.preferred_time is None]
        bumped = self._place_anchored(anchored)
        self._fill_gaps(self._sort_tasks(unanchored + bumped))

    def _collect_tasks(self) -> list[Task]:
        """Gather all tasks due today across every pet; assert each has a pet back-reference."""
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
        """Sort by priority desc, then duration asc; stable sort breaks remaining ties by insertion order."""
        return sorted(tasks, key=lambda t: (-t.priority, t.duration))

    def sort_by_time(self) -> list[Task]:
        """Return all scheduled tasks sorted by start time ascending."""
        return [task for _, _, task in sorted(self.entries, key=lambda e: e[0])]

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """Return scheduled tasks matching the given filters (both optional, combinable)."""
        tasks = [task for _, _, task in self.entries]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet is not None and t.pet.name == pet_name]
        return tasks

    def _first_free_gap(self, duration: int, after: int) -> Optional[int]:
        """Return the earliest start >= `after` where `duration` minutes fit without overlap, or None."""
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
        """Place preferred-time tasks, bumping clash losers; return the bumped list for gap-fill."""
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
        """Return (winner, loser): higher priority wins, then shorter duration, then `a` by convention."""
        if a.priority != b.priority:
            return (a, b) if a.priority > b.priority else (b, a)
        if a.duration != b.duration:
            return (a, b) if a.duration <= b.duration else (b, a)
        return a, b  # `a` wins by stable convention

    def _fill_gaps(self, tasks: list[Task]) -> None:
        """Place un-timed and bumped tasks into the first available gap by priority; overflow goes to dropped."""
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
