from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule

owner = Owner("Jordan", day_start=7 * 60, day_end=21 * 60)

biscuit = Pet("Biscuit", species="dog", breed="Golden Retriever", age=3)
mochi = Pet("Mochi", species="cat", breed="Tabby", age=5)

owner.add_pet(biscuit)
owner.add_pet(mochi)

# Tasks added out of order to exercise sort_by_time()
biscuit.add_task(Task("Evening walk",  duration=30, priority=3, category="walk",    preferred_time=18 * 60))
biscuit.add_task(Task("Flea meds",     duration=5,  priority=5, category="meds"))
biscuit.add_task(Task("Morning walk",  duration=30, priority=3, category="walk",    preferred_time=8 * 60))
biscuit.add_task(Task("Breakfast",     duration=10, priority=4, category="feeding", preferred_time=8 * 60 + 30))

mochi.add_task(Task("Evening feeding", duration=5,  priority=4, category="feeding", preferred_time=18 * 60))
mochi.add_task(Task("Playtime",        duration=20, priority=2, category="grooming"))
mochi.add_task(Task("Morning feeding", duration=5,  priority=4, category="feeding", preferred_time=7 * 60 + 30))

sched = Schedule(owner=owner, date=date.today())
sched.generate()

# --- sort_by_time() ---
print(f"Today's Schedule — {sched.date} (sorted by time)")
print("=" * 40)
for task in sched.sort_by_time():
    print(f"  • {task.summary()}")

# --- filter_tasks(pet_name=) ---
print()
print("Biscuit's tasks only:")
print("-" * 40)
for task in sched.filter_tasks(pet_name="Biscuit"):
    print(f"  • {task.summary()}")

# Mark one task complete to exercise the completed filter
biscuit_tasks = sched.filter_tasks(pet_name="Biscuit")
if biscuit_tasks:
    biscuit_tasks[0].mark_complete()

# --- filter_tasks(completed=True) ---
print()
print("Completed tasks:")
print("-" * 40)
completed = sched.filter_tasks(completed=True)
if completed:
    for task in completed:
        print(f"  ✓ {task.summary()}")
else:
    print("  (none)")

# --- filter_tasks(completed=False) ---
print()
print("Remaining tasks:")
print("-" * 40)
for task in sched.filter_tasks(completed=False):
    print(f"  • {task.summary()}")

if sched.dropped:
    print()
    print("Couldn't fit:")
    for task in sched.dropped:
        print(f"  • {task.summary()}")

# --- conflict detection ---
# Force two overlapping entries (same start, different pets) to demonstrate detection.
vet_visit   = Task("Vet checkup",      duration=60, priority=5, category="meds",     preferred_time=10 * 60)
grooming    = Task("Grooming session", duration=45, priority=3, category="grooming", preferred_time=10 * 60 + 20)
biscuit.add_task(vet_visit)
mochi.add_task(grooming)
sched.entries.append((10 * 60,      biscuit, vet_visit))   # 10:00–11:00
sched.entries.append((10 * 60 + 20, mochi,   grooming))    # 10:20–11:05 — overlaps vet visit

print()
print("Conflict Detection:")
print("-" * 40)
conflicts = sched.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")
