class Teacher:
    def __init__(self, name, subjects):
        self.name = name
        self.subjects = subjects  # list of subject names this teacher can teach

class Subject:
    def __init__(self, name, periods_per_week):
        self.name = name
        self.periods_per_week = periods_per_week  # how many periods this subject needs each week

class ClassGroup:
    def __init__(self, name):
        self.name = name  # e.g. "Grade 8 - A"
        self.timetable = {}  # will hold the final schedule for this class
        