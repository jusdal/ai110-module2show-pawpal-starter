from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration=30, priority=3)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Breakfast", duration=10, priority=4))
    assert len(pet.tasks) == 1
    pet.add_task(Task(name="Evening walk", duration=30, priority=3))
    assert len(pet.tasks) == 2
