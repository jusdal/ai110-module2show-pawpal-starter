from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Schedule, Task

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# Initialize the Owner object once; it persists across reruns as a real Python object.
# Tasks added to its pet accumulate here instead of in a separate dict list.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
    st.session_state.owner.add_pet(Pet(name="Mochi", species="dog"))

owner = st.session_state.owner
pet = owner.pets[0]

# --- Owner & Pet ---
st.subheader("Owner & Pet")
owner.name = st.text_input("Owner name", value=owner.name)
pet.name = st.text_input("Pet name", value=pet.name)
species_options = ["dog", "cat", "other"]
pet.species = st.selectbox("Species", species_options,
                           index=species_options.index(pet.species))

# --- Tasks ---
st.subheader("Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    pet.add_task(Task(
        name=task_title,
        duration=int(duration),
        priority=PRIORITY_MAP[priority],
    ))

if pet.tasks:
    st.table([
        {"title": t.name, "duration_minutes": t.duration, "priority": t.priority}
        for t in pet.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule ---
if st.button("Generate schedule"):
    if not pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        sched = Schedule(owner=owner, date=date.today())
        sched.generate()
        st.session_state.schedule = sched

if "schedule" in st.session_state:
    sched = st.session_state.schedule
    st.subheader("Today's Schedule")
    st.code(str(sched), language=None)

    if sched.dropped:
        st.warning("Couldn't fit everything:")
        for task in sched.dropped:
            st.write(f"- {task.summary()}")

    with st.expander("Why this plan?"):
        st.text(sched.explain())
