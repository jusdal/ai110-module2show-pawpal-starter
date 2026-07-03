from datetime import date, timedelta

from pawpal_system import Pet, Task


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
