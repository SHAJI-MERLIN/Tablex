from models import Teacher, Subject, ClassGroup

priya = Teacher("Priya", ["Math", "Science"])
arjun = Teacher("Arjun", ["English"])

math = Subject("Math", periods_per_week=5)

grade8a = ClassGroup("Grade 8 - A")

print(priya.name, priya.subjects)
print(arjun.name, arjun.subjects)
print(math.name, math.periods_per_week)
print(grade8a.name)