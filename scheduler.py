import random

def generate_timetable(num_days, periods_per_day, class_names, subjects, teachers, min_free_periods=1):
    """
    Builds a clash-free timetable for every class.
    Returns a dictionary like:
    {
        "Class 1": {
            "Monday": {1: "Math (Priya)", 2: "FREE", ...},
            "Tuesday": {...},
            ...
        },
        "Class 2": {...}
    }
    """
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][:num_days]
   
    # Track how many periods still needed per subject, PER CLASS
    remaining_periods = {
        class_name: {subj["name"]: subj["periods_per_week"] for subj in subjects}
        for class_name in class_names
    }

    # Track which (day, period) slots each teacher is already busy in
    teacher_busy = {teacher["name"]: set() for teacher in teachers}

    # Track how many free periods each teacher has been given per day (need at least 1)
    teacher_free_count = {
        teacher["name"]: {day: 0 for day in day_names} for teacher in teachers
    }

    # Build a lookup: which teachers can teach which subject (case-insensitive)
    def teachers_for_subject(subject_name):
        return [
            t for t in teachers
            if subject_name.lower() in [s.lower() for s in t["subjects"]]
        ]

    timetable = {class_name: {day: {} for day in day_names} for class_name in class_names}

    for class_name in class_names:
        for day in day_names:
            for period in range(1, periods_per_day + 1):

                available_subjects = [
                    s for s in subjects if remaining_periods[class_name][s["name"]] > 0
                ]

                assigned = False
                random.shuffle(available_subjects)

                for subject in available_subjects:
                    candidate_teachers = teachers_for_subject(subject["name"])
                    random.shuffle(candidate_teachers)

                    for teacher in candidate_teachers:
                        slot = (day, period)

                        if slot in teacher_busy[teacher["name"]]:
                            continue

                        periods_left_today = periods_per_day - period + 1
                        free_periods_still_needed = min_free_periods - teacher_free_count[teacher["name"]][day]
                        if free_periods_still_needed >= periods_left_today:
                            continue

                        timetable[class_name][day][period] = f"{subject['name']} ({teacher['name']})"
                        teacher_busy[teacher["name"]].add(slot)
                        remaining_periods[class_name][subject["name"]] -= 1
                        assigned = True
                        break

                    if assigned:
                        break

                if not assigned:
                    timetable[class_name][day][period] = "FREE"

    return timetable


def build_teacher_timetables(timetable, teachers, day_names, periods_per_day):
    """
    Builds a separate schedule for each teacher, showing which class they teach
    each period, or 'FREE' if they have no class at that time.
    """
    teacher_timetables = {
        teacher["name"]: {day: {p: "FREE" for p in range(1, periods_per_day + 1)} for day in day_names}
        for teacher in teachers
    }

    for class_name, schedule in timetable.items():
        for day, periods in schedule.items():
            for period, entry in periods.items():
                if entry == "FREE":
                    continue
                teacher_name = entry.split("(")[1].replace(")", "")
                teacher_timetables[teacher_name][day][period] = f"{entry.split(' (')[0]} - {class_name}"

    return teacher_timetables
def check_feasibility(class_names, subjects, teachers, num_days, periods_per_day, min_free_periods=1):
    """
    Checks whether there are enough teachers to realistically cover demand,
    BEFORE attempting to generate a timetable. Returns a list of warning messages.
    """
    warnings = []
    max_periods_per_teacher = num_days * (periods_per_day - min_free_periods)

    for subject in subjects:
        subject_name = subject["name"]
        periods_needed_per_class = subject["periods_per_week"]
        total_demand = periods_needed_per_class * len(class_names)

        qualified_teachers = [
            t for t in teachers
            if subject_name.lower() in [s.lower() for s in t["subjects"]]
        ]

        if not qualified_teachers:
            warnings.append(f"No teacher at all can teach '{subject_name}' — every class needs it but nobody is qualified.")
            continue

        total_supply = len(qualified_teachers) * max_periods_per_teacher

        if total_demand > total_supply:
            warnings.append(
                f"NOT ENOUGH TEACHERS for '{subject_name}': needs {total_demand} periods/week "
                f"across {len(class_names)} classes, but {len(qualified_teachers)} teacher(s) "
                f"({', '.join(t['name'] for t in qualified_teachers)}) can supply at most {total_supply}. "
                f"Consider adding more teachers for '{subject_name}'."
            )

    return warnings