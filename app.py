from flask import Flask, render_template, request, send_file
from scheduler import generate_timetable_cp, build_teacher_timetables, check_feasibility
from check_timetable import check_timetable
import openpyxl
import io

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    num_days = int(request.form["num_days"])
    periods_per_day = int(request.form["periods_per_day"])
    min_free_periods = int(request.form["min_free_periods"])

    class_names = [line.strip() for line in request.form["class_data"].strip().split("\n")]
    subjects = parse_subject_data(request.form["subject_data"])
    teachers = parse_teacher_data(request.form["teacher_data"])

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][:num_days]

    feasibility_warnings = check_feasibility(class_names, subjects, teachers, num_days, periods_per_day, min_free_periods)
    if feasibility_warnings:
        return render_template("infeasible.html", warnings=feasibility_warnings)

    timetable = generate_timetable_cp(num_days, periods_per_day, class_names, subjects, teachers, min_free_periods)

    if timetable is None:
        return render_template(
            "infeasible.html",
            warnings=["The solver could not find any valid timetable satisfying all constraints. "
                      "Try adding more teachers, reducing classes, or relaxing the free-period requirement."]
        )

    teacher_timetables = build_teacher_timetables(timetable, teachers, day_names, periods_per_day)

    errors = check_timetable(timetable, subjects, teachers, day_names, periods_per_day, min_free_periods)
    if errors:
        print("⚠️ TIMETABLE ERRORS FOUND:")
        for e in errors:
            print(" -", e)
    else:
        print("✅ Timetable passed all checks!")

    return render_template(
        "result.html",
        timetable=timetable,
        teacher_timetables=teacher_timetables,
        periods_per_day=periods_per_day,
        num_days=num_days,
        min_free_periods=min_free_periods,
        class_data=request.form["class_data"],
        subject_data=request.form["subject_data"],
        teacher_data=request.form["teacher_data"]
    )

@app.route("/download/excel", methods=["POST"])
def download_excel():
    num_days = int(request.form["num_days"])
    periods_per_day = int(request.form["periods_per_day"])
    min_free_periods = int(request.form["min_free_periods"])
    class_names = [line.strip() for line in request.form["class_data"].strip().split("\n")]
    subjects = parse_subject_data(request.form["subject_data"])
    teachers = parse_teacher_data(request.form["teacher_data"])
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][:num_days]

    timetable = generate_timetable_cp(num_days, periods_per_day, class_names, subjects, teachers, min_free_periods)

    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)

    for class_name, schedule in timetable.items():
        sheet = workbook.create_sheet(title=class_name[:31])
        sheet.append(["Day"] + [f"Period {p}" for p in range(1, periods_per_day + 1)])

        for day in day_names:
            row = [day]
            for period in range(1, periods_per_day + 1):
                row.append(schedule[day][period])
            sheet.append(row)

    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="tablex_timetable.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def parse_subject_data(raw_text):
    """Turn 'Math:5' lines into a list like [{'name': 'Math', 'periods_per_week': 5}]"""
    subjects = []
    lines = raw_text.strip().split("\n")

    for line in lines:
        name, periods = line.split(":")
        subjects.append({"name": name.strip(), "periods_per_week": int(periods.strip())})

    return subjects

def parse_teacher_data(raw_text):
    """Turn 'Priya - Math, Science' lines into [{'name': 'Priya', 'subjects': ['Math', 'Science']}]"""
    teachers = []
    lines = raw_text.strip().split("\n")

    for line in lines:
        name_part, subjects_part = line.split("-", 1)
        name = name_part.strip()
        subject_list = [s.strip() for s in subjects_part.split(",")]
        teachers.append({"name": name, "subjects": subject_list})

    return teachers

if __name__ == "__main__":
    app.run(debug=True, port=5001)