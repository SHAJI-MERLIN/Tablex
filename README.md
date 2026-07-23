# Tablex — Automated Timetable Generator

Tablex is a web app that automatically generates clash-free weekly timetables for schools, given any number of classes, teachers, and subjects. It uses a constraint solver to *guarantee* a correct result whenever one is mathematically possible — not just a best-effort guess.

**Live demo:** https://tablex.onrender.com

## Features

- **Fully configurable inputs** — number of working days, periods per day, minimum free periods per teacher per day, class names/divisions (e.g. `1-A`, `1-B`), subjects with periods-per-week, and teachers with the subjects they can teach.
- **Clash-free scheduling** — no teacher is ever assigned to two classes at the same time.
- **Guaranteed correctness** — built on [Google OR-Tools](https://developers.google.com/optimization) (CP-SAT constraint solver), so if a valid timetable exists for the given inputs, Tablex will find it.
- **Feasibility pre-check** — before generating, Tablex checks whether there's actually enough teacher capacity to meet demand. If not, it clearly explains which subject is understaffed and **suggests exactly how many more teachers are needed**.
- **Two views** — a timetable per class, and a separate timetable per teacher (showing their own schedule and free periods across all classes).
- **Automated correctness checker** — independently re-verifies every generated timetable against all rules (no clashes, correct subject counts, minimum free periods, teachers only assigned subjects they know).
- **Case-insensitive subject matching** — "Math", "math", and "MATH" are all treated as the same subject.
- **Excel export** — download the generated timetable as an `.xlsx` file, with one sheet per class.

## Tech stack

- **Backend:** Python + Flask
- **Scheduling engine:** Google OR-Tools (CP-SAT constraint solver)
- **Frontend:** HTML + Jinja2 templates
- **Excel export:** openpyxl
- **Deployment:** Render

## Running locally

```bash
git clone https://github.com/SHAJI-MERLIN/Tablex.git
cd Tablex
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
Then open `http://127.0.0.1:5001` in your browser.

## Input formats

**Subjects** (one per line): `SubjectName:PeriodsPerWeek`