def check_timetable(timetable, subjects, teachers, day_names, periods_per_day, min_free_periods=1):
    errors = []

    subject_periods_needed = {s["name"]: s["periods_per_week"] for s in subjects}
    teacher_known_subjects = {t["name"]: [s.lower() for s in t["subjects"]] for t in teachers}

    teacher_usage = {}
    subject_count = {}

    for class_name, schedule in timetable.items():
        for day, periods in schedule.items():
            for period, entry in periods.items():
                if entry == "FREE":
                    continue

                subject_name = entry.split(" (")[0]
                teacher_name = entry.split("(")[1].replace(")", "")

                if subject_name.lower() not in teacher_known_subjects.get(teacher_name, []):
                    errors.append(f"{teacher_name} assigned {subject_name} but doesn't know it ({class_name}, {day} P{period})")

                key = (day, period)
                teacher_usage.setdefault(teacher_name, {})
                if key in teacher_usage[teacher_name]:
                    other_class = teacher_usage[teacher_name][key]
                    errors.append(f"CLASH: {teacher_name} teaches both {other_class} and {class_name} on {day} P{period}")
                else:
                    teacher_usage[teacher_name][key] = class_name

                subject_count[(class_name, subject_name)] = subject_count.get((class_name, subject_name), 0) + 1

    for class_name in timetable.keys():
        for subject_name, needed in subject_periods_needed.items():
            actual = subject_count.get((class_name, subject_name), 0)
            if actual != needed:
                errors.append(f"{class_name}: {subject_name} has {actual} periods, needed {needed}")

    for teacher_name in teacher_known_subjects.keys():
        for day in day_names:
            periods_used_today = sum(1 for key in teacher_usage.get(teacher_name, {}) if key[0] == day)
            free_periods_today = periods_per_day - periods_used_today
            if free_periods_today < min_free_periods:
                errors.append(f"{teacher_name} has only {free_periods_today} free period(s) on {day}, needed {min_free_periods}")

    return errors