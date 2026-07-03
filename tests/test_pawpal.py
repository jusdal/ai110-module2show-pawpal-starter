from datetime import date, timedelta

from pawpal_system import Owner, Pet, Schedule, Task


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=30, priority=3)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_daily_spawns_next_task():
    pet = Pet(name="Biscuit", species="dog")
    today = date(2026, 7, 2)
    task = Task(name="Morning walk", duration=30, priority=3, recurrence="daily", due_date=today)
    pet.add_task(task)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.recurrence == "daily"
    assert next_task.completed is False
    assert next_task in pet.tasks


def test_mark_complete_weekly_spawns_next_task():
    pet = Pet(name="Biscuit", species="dog")
    today = date(2026, 7, 2)
    task = Task(name="Bath time", duration=45, priority=2, recurrence="weekly", due_date=today)
    pet.add_task(task)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)
    assert next_task.recurrence == "weekly"


def test_mark_complete_non_recurring_returns_none():
    pet = Pet(name="Biscuit", species="dog")
    task = Task(name="Vet visit", duration=60, priority=5)
    pet.add_task(task)

    result = task.mark_complete()

    assert task.completed is True
    assert result is None
    assert len(pet.tasks) == 1  # no new task added


def test_mark_complete_without_pet_no_spawn():
    task = Task(name="Morning walk", duration=30, priority=3, recurrence="daily")
    result = task.mark_complete()
    assert task.completed is True
    assert result is None


def test_is_due_today_uses_due_date():
    today = date(2026, 7, 2)
    task_today = Task(name="Walk", duration=20, priority=1, recurrence="weekly", due_date=today)
    task_tomorrow = Task(name="Walk", duration=20, priority=1, recurrence="weekly", due_date=today + timedelta(days=1))
    assert task_today.is_due_today(today) is True
    assert task_tomorrow.is_due_today(today) is False


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Breakfast", duration=10, priority=4))
    assert len(pet.tasks) == 1
    pet.add_task(Task(name="Evening walk", duration=30, priority=3))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="dog")
    owner.add_pet(pet)
    today = date(2026, 7, 3)

    morning = Task(name="Morning walk", duration=20, priority=2, preferred_time=8 * 60, due_date=today)
    noon = Task(name="Feeding", duration=10, priority=2, preferred_time=12 * 60, due_date=today)
    evening = Task(name="Evening walk", duration=20, priority=2, preferred_time=18 * 60, due_date=today)
    for t in (morning, noon, evening):
        pet.add_task(t)

    schedule = Schedule(owner=owner, date=today)
    schedule.generate()

    assert schedule.sort_by_time() == [morning, noon, evening]


# ---------------------------------------------------------------------------
# Recurrence edge cases
# ---------------------------------------------------------------------------

def test_mark_complete_daily_no_due_date_uses_today():
    """When no due_date is set, spawn advances from date.today()."""
    pet = Pet(name="Biscuit", species="dog")
    task = Task(name="Walk", duration=30, priority=3, recurrence="daily")
    pet.add_task(task)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_mark_complete_unknown_recurrence_returns_none():
    """Unrecognised recurrence values (e.g. 'monthly') do not spawn a follow-up."""
    pet = Pet(name="Biscuit", species="dog")
    task = Task(name="Monthly groom", duration=60, priority=2, recurrence="monthly")
    pet.add_task(task)

    result = task.mark_complete()

    assert task.completed is True
    assert result is None
    assert len(pet.tasks) == 1  # no new task added


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks():
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="dog")
    owner.add_pet(pet)
    today = date(2026, 7, 3)
    schedule = Schedule(owner=owner, date=today)

    walk = Task(name="Walk", duration=60, priority=3)
    feeding = Task(name="Feeding", duration=30, priority=2)
    pet.add_task(walk)
    pet.add_task(feeding)

    # Walk 08:00–09:00, Feeding 08:30–09:00 — clear overlap
    schedule.entries = [(8 * 60, pet, walk), (8 * 60 + 30, pet, feeding)]

    warnings = schedule.detect_conflicts()
    assert len(warnings) == 1
    assert "WARNING" in warnings[0]


def test_detect_conflicts_back_to_back_not_flagged():
    """End of one task == start of next is NOT a conflict."""
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="dog")
    owner.add_pet(pet)
    today = date(2026, 7, 3)
    schedule = Schedule(owner=owner, date=today)

    walk = Task(name="Walk", duration=60, priority=3)
    feeding = Task(name="Feeding", duration=30, priority=2)
    pet.add_task(walk)
    pet.add_task(feeding)

    # Walk 08:00–09:00, Feeding 09:00–09:30 — back-to-back, no overlap
    schedule.entries = [(8 * 60, pet, walk), (9 * 60, pet, feeding)]

    assert schedule.detect_conflicts() == []


def test_detect_conflicts_empty_schedule_returns_no_warnings():
    owner = Owner(name="Alex")
    schedule = Schedule(owner=owner, date=date(2026, 7, 3))
    assert schedule.detect_conflicts() == []
