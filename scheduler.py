import random
import math
from ortools.sat.python import cp_model

def generate_timetable(num_days, periods_per_day, class_names, subjects, teachers, min_free_periods=1):
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][:num_days]

    remaining_periods = {
        class_name: {subj["name"]: subj["periods_per_week"] for subj in subjects}
        for class_name in class_names
    }

    teacher_busy = {teacher["name"]: set() for teacher in teachers}
    teacher_free_count = {
        teacher["name"]: {day: 0 for day in day_names} for teacher in teachers
    }

    def teachers_for_subject(subject_name):
        return [
            t for t in teachers
            if subject_name.lower() in [s.lower() for s in t["subjects"]]
        ]

    timetable = {class_name: {day: {} for day in day_names} for class_name in class_names}

    # KEY CHANGE: loop day -> period -> classes (rotated), instead of class -> day -> period.
    # This gives every class a fair turn at each time slot, instead of finishing
    # one class entirely before starting the next.
    for day in day_names:
        for period in range(1, periods_per_day + 1):

            # Rotate which class goes first, so the same class isn't always last in line
            rotation = period % len(class_names)
            ordered_classes = class_names[rotation:] + class_names[:rotation]

            for class_name in ordered_classes:
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
                   shortfall = total_demand - total_supply
                   extra_teachers_needed = math.ceil(shortfall / max_periods_per_teacher)
       
                   warnings.append(
                       f"NOT ENOUGH TEACHERS for '{subject_name}': needs {total_demand} periods/week "
                       f"across {len(class_names)} classes, but {len(qualified_teachers)} teacher(s) "
                       f"({', '.join(t['name'] for t in qualified_teachers)}) can supply at most {total_supply} "
                       f"(short by {shortfall}). You need at least {extra_teachers_needed} more teacher(s) "
                       f"qualified in '{subject_name}' to make this work."
                   )

    return warnings
def generate_timetable_cp(num_days, periods_per_day, class_names, subjects, teachers, min_free_periods=1):
    """
    Builds a timetable using a constraint solver (OR-Tools CP-SAT) instead of guessing.
    Guarantees correctness if a valid solution exists, and tells us clearly if it doesn't.
    """
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][:num_days]
    model = cp_model.CpModel()

    def teachers_for_subject(subject_name):
        return [
            t["name"] for t in teachers
            if subject_name.lower() in [s.lower() for s in t["subjects"]]
        ]

    # DECISION VARIABLES: assign[(class, day, period, subject, teacher)] = 1 if that
    # combination happens, 0 if not. We only create variables for teachers who
    # actually CAN teach that subject - no point letting the solver even consider
    # invalid combinations.
    assign = {}
    for class_name in class_names:
        for day in day_names:
            for period in range(1, periods_per_day + 1):
                for subject in subjects:
                    for teacher_name in teachers_for_subject(subject["name"]):
                        key = (class_name, day, period, subject["name"], teacher_name)
                        assign[key] = model.NewBoolVar(f"assign_{class_name}_{day}_{period}_{subject['name']}_{teacher_name}")

    # RULE 1: each class, at each day+period, gets AT MOST one subject/teacher assigned
    for class_name in class_names:
        for day in day_names:
            for period in range(1, periods_per_day + 1):
                relevant_vars = [
                    v for (c, d, p, s, t), v in assign.items()
                    if c == class_name and d == day and p == period
                ]
                if relevant_vars:
                    model.Add(sum(relevant_vars) <= 1)

    # RULE 2: each class gets EXACTLY the required number of periods per subject, per week
    for class_name in class_names:
        for subject in subjects:
            relevant_vars = [
                v for (c, d, p, s, t), v in assign.items()
                if c == class_name and s == subject["name"]
            ]
            if relevant_vars:
                model.Add(sum(relevant_vars) == subject["periods_per_week"])

    # RULE 3: no teacher clash - at each day+period, a teacher works AT MOST one class
    for teacher in teachers:
        for day in day_names:
            for period in range(1, periods_per_day + 1):
                relevant_vars = [
                    v for (c, d, p, s, t), v in assign.items()
                    if t == teacher["name"] and d == day and p == period
                ]
                if relevant_vars:
                    model.Add(sum(relevant_vars) <= 1)

    # RULE 4: each teacher gets at least `min_free_periods` free periods per day
    for teacher in teachers:
        for day in day_names:
            relevant_vars = [
                v for (c, d, p, s, t), v in assign.items()
                if t == teacher["name"] and d == day
            ]
            if relevant_vars:
                model.Add(sum(relevant_vars) <= periods_per_day - min_free_periods)

    # Ask the solver to find an assignment satisfying ALL rules above
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 20.0
    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None  # No valid timetable exists satisfying all constraints

    # Convert the solver's yes/no decisions back into our familiar timetable format
    timetable = {class_name: {day: {} for day in day_names} for class_name in class_names}
    for class_name in class_names:
        for day in day_names:
            for period in range(1, periods_per_day + 1):
                timetable[class_name][day][period] = "FREE"

    for (class_name, day, period, subject_name, teacher_name), var in assign.items():
        if solver.Value(var) == 1:
            timetable[class_name][day][period] = f"{subject_name} ({teacher_name})"

    return timetable