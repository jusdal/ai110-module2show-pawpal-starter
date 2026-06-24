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
        raise NotImplementedError

    def is_due_today(self, day: date) -> bool:
        """Whether this task should run on the given day (recurrence aware)."""
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0
    special_needs: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet (sets the task's pet back-reference)."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet."""
        raise NotImplementedError

    def tasks_by_priority(self) -> list[Task]:
        """This pet's tasks, highest priority first."""
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    day_start: int = 7 * 60                 # 07:00
    day_end: int = 21 * 60                  # 21:00
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        raise NotImplementedError

    def all_tasks(self) -> list[Task]:
        """Flat list of every task across all of this owner's pets."""
        raise NotImplementedError

    def total_task_load(self) -> int:
        """Sum of all task durations (minutes) across all pets."""
        raise NotImplementedError


@dataclass
class Schedule:
    owner: Owner
    date: date
    entries: list[tuple[int, Pet, Task]] = field(default_factory=list)  # (start_time, pet, task)
    dropped: list[Task] = field(default_factory=list)                   # didn't fit / bumped out

    def generate(self) -> None:
        """Build the daily plan: collect -> sort -> place anchored -> fill gaps -> drop overflow."""
        raise NotImplementedError

    def _collect_tasks(self) -> list[Task]:
        """Gather all due tasks from the owner's pets into one pool."""
        raise NotImplementedError

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (desc), then duration. Tie-break documented in generate()."""
        raise NotImplementedError

    def _place_anchored(self, tasks: list[Task]) -> None:
        """Place tasks that have a preferred_time, resolving clashes by priority."""
        raise NotImplementedError

    def _resolve_clash(self, a: Task, b: Task) -> Task:
        """Return the task that wins a contested slot; the loser gets bumped."""
        raise NotImplementedError

    def _fill_gaps(self, tasks: list[Task]) -> None:
        """Place un-timed (and bumped) tasks into remaining gaps by priority."""
        raise NotImplementedError

    def explain(self) -> str:
        """Human-readable rationale for what was scheduled and what was dropped."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Render the plan like the sample output (HH:MM — Task (dur) [priority])."""
        raise NotImplementedError
