from datetime import date
from pawpal_system import Owner, Pet, Task, Schedule

owner = Owner("Jordan", day_start=7 * 60, day_end=21 * 60)

biscuit = Pet("Biscuit", species="dog", breed="Golden Retriever", age=3)
mochi = Pet("Mochi", species="cat", breed="Tabby", age=5)

owner.add_pet(biscuit)
owner.add_pet(mochi)

# Biscuit's tasks
biscuit.add_task(Task("Morning walk",  duration=30, priority=3, category="walk",     preferred_time=8 * 60))
biscuit.add_task(Task("Breakfast",     duration=10, priority=4, category="feeding",  preferred_time=8 * 60 + 30))
biscuit.add_task(Task("Evening walk",  duration=30, priority=3, category="walk",     preferred_time=18 * 60))
biscuit.add_task(Task("Flea meds",    duration=5,  priority=5, category="meds"))

# Mochi's tasks
mochi.add_task(Task("Morning feeding", duration=5,  priority=4, category="feeding",  preferred_time=7 * 60 + 30))
mochi.add_task(Task("Playtime",        duration=20, priority=2, category="grooming"))
mochi.add_task(Task("Evening feeding", duration=5,  priority=4, category="feeding",  preferred_time=18 * 60))

sched = Schedule(owner=owner, date=date.today())
sched.generate()

print(f"Today's Schedule — {sched.date}")
print("=" * 40)
print(sched)

if sched.dropped:
    print()
    print("Couldn't fit:")
    for task in sched.dropped:
        print(f"  • {task.summary()}")

print()
print(sched.explain())
