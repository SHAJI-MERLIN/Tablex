from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    # Step A: get the simple number fields from the form
    num_days = int(request.form["num_days"])
    periods_per_day = int(request.form["periods_per_day"])
    num_classes = int(request.form["num_classes"])

    # Step B: get the raw teacher text and break it into structured data
    raw_teacher_text = request.form["teacher_data"]
    teachers = parse_teacher_data(raw_teacher_text)

    # Step C: for now, just show what we received (to confirm it's working)
    return f"""
    <h2>Received your inputs:</h2>
    <p>Days per week: {num_days}</p>
    <p>Periods per day: {periods_per_day}</p>
    <p>Number of classes: {num_classes}</p>
    <p>Parsed teachers: {teachers}</p>
    """

def parse_teacher_data(raw_text):
    """Turn the textarea's raw text into a list of teacher dictionaries."""
    teachers = []
    lines = raw_text.strip().split("\n")   # split into one line per teacher

    for line in lines:
        name_part, subjects_part = line.split("-", 1)   # split "Priya - Math:5, Science:3"
        name = name_part.strip()

        subjects = {}
        for subject_entry in subjects_part.split(","):      # split "Math:5, Science:3" by comma
            subject_name, periods = subject_entry.split(":")  # split "Math:5" by colon
            subjects[subject_name.strip()] = int(periods.strip())

        teachers.append({"name": name, "subjects": subjects})

    return teachers

if __name__ == "__main__":
    app.run(debug=True, port=5001)