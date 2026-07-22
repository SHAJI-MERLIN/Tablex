from flask import Flask, render_template, request
from scheduler import generate_timetable, build_teacher_timetables
from check_timetable import check_timetable

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    num_days = int(request.form["num_days"])
    periods_per_day = int(request.form["periods_per_day"])
    num_classes = int(request.form["num_classes"])

    subjects = parse_subject_data(request.form["subject_data"])
    teachers = parse_teacher_data(request.form["teacher_data"])

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][:num_days]

    timetable = generate_timetable(num_days, periods_per_day, num_classes, subjects, teachers)
    teacher_timetables = build_teacher_timetables(timetable, teachers, day_names, periods_per_day)

    errors = check_timetable(timetable, subjects, teachers, day_names, periods_per_day)
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
        periods_per_day=periods_per_day
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