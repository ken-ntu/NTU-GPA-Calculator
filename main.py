import itertools
import arg_conf
import pdfplumber
from log import get_logger
import re

args = arg_conf.ArgParser().parse_args()

file_path = args.path
if args.ignore_warnings:
    import logging

    get_logger("pdfminer").setLevel(logging.ERROR)

LOGGER = get_logger()

if args.debug:
    import logging

    LOGGER.setLevel(logging.DEBUG)

# extract course details from transcript
course_detail_pattern = r"(?=^)([A-Za-z0-9\-\:\,\.\(\)\~\!\u2160-\u216F\u2606]+) (\d) ([A-C][+-]?|[FX]|PASS|W|EX|TR|NG|IP)(?=$)"
semester_title_pattern = r"^(1st|2nd)Semester\d{4}\/\d{4}$"
session_title_pattern = r"^(Summer|Winter)Session\d{4}\/\d{4}$"
semester_grades = {}
semester = ""
grades = []
with pdfplumber.open(file_path) as pdf_file:
    for i, page in enumerate(pdf_file.pages):
        text = page.extract_text()
        if "NATIONAL TAIWAN UNIVERSITY\nTRANSCRIPTOF ACADEMIC RECORD" in text:
            tables = page.extract_tables()
            lines = itertools.chain.from_iterable(
                col.split("\n") for table in tables for row in table for col in row
            )
            for line in lines:
                if re.match(f"{semester_title_pattern}|{session_title_pattern}", line):
                    if semester:
                        semester_grades[semester] = grades
                        grades = []
                    semester = line
                if match := re.match(course_detail_pattern, line):
                    grades.append(match.groups())
            semester_grades[semester] = grades

grade_to_points = {
    "A+": 4.3,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "F": 0,
    "X": 0,
}

# calculate overall GPA
total_credits = 0
grade_credits = 0
pass_credits = 0
total_grades = 0
for semester, grades in semester_grades.items():
    for _, credits, letter_grade in grades:
        if re.match(r"W|EX|TR|NG|IP", letter_grade):
            continue
        if re.match(r"PASS", letter_grade):
            pass_credits += int(credits)
            continue
        if letter_grade not in grade_to_points:
            raise ValueError("Extracted Grade not found!")

        grade_credits += int(credits)
        total_grades += grade_to_points[letter_grade] * int(credits)

total_credits = grade_credits + pass_credits
LOGGER.info(f"overall credits: {total_credits}")
LOGGER.info(f"overall GPA: {total_grades / grade_credits}")

# calculate two year GPA
total_credits = 0
grade_credits = 0
pass_credits = 0
total_grades = 0
cnt = 0
for semester, grades in reversed(semester_grades.items()):
    if re.match(semester_title_pattern, semester):
        cnt += 1
    for _, credits, letter_grade in grades:
        if re.match(r"W|EX|TR|NG|IP", letter_grade):
            continue
        if re.match(r"PASS", letter_grade):
            pass_credits += int(credits)
            continue
        if letter_grade not in grade_to_points:
            raise ValueError("Extracted Grade not found!")

        grade_credits += int(credits)
        total_grades += grade_to_points[letter_grade] * int(credits)
    if cnt >= 4:
        break

total_credits = grade_credits + pass_credits
LOGGER.info(f"last 2 year credits: {total_credits}")
LOGGER.info(f"last 2 year GPA: {total_grades / grade_credits}")

# calculate last year GPA
total_credits = 0
grade_credits = 0
pass_credits = 0
total_grades = 0
cnt = 0
for semester, grades in reversed(semester_grades.items()):
    if re.match(semester_title_pattern, semester):
        cnt += 1
    for _, credits, letter_grade in grades:
        if re.match(r"W|EX|TR|NG|IP", letter_grade):
            continue
        if re.match(r"PASS", letter_grade):
            pass_credits += int(credits)
            continue
        if letter_grade not in grade_to_points:
            raise ValueError("Extracted Grade not found!")

        grade_credits += int(credits)
        total_grades += grade_to_points[letter_grade] * int(credits)
    if cnt >= 2:
        break

total_credits = grade_credits + pass_credits
LOGGER.info(f"last year credits: {total_credits}")
LOGGER.info(f"last year GPA: {total_grades / grade_credits}")

# calculate last-60 GPA
total_credits = 0
grade_credits = 0
pass_credits = 0
total_grades = 0
cnt = 0
for semester, grades in reversed(semester_grades.items()):
    LOGGER.debug(f"{semester} {cnt}")
    grades = [x for x in grades if re.match(r"[A-C][+-]?|[FX]", x[2])]
    LOGGER.debug(grades)
    if cnt + sum(int(x[1]) for x in grades) > 60:
        grades = sorted(grades, key=lambda x: grade_to_points[x[2]], reverse=True)
        index = 0
        for x in grades:
            cnt += int(x[1])
            index += 1
            if cnt >= 60:
                break
        grades = grades[:index]
    else:
        cnt += sum(int(x[1]) for x in grades)
    for _, credits, letter_grade in grades:
        if re.match(r"W|EX|TR|NG|IP", letter_grade):
            continue
        if re.match(r"PASS", letter_grade):
            pass_credits += int(credits)
            continue
        if letter_grade not in grade_to_points:
            raise ValueError("Extracted Grade not found!")

        grade_credits += int(credits)
        total_grades += grade_to_points[letter_grade] * int(credits)
    if cnt >= 60:
        break
total_credits = grade_credits + pass_credits
LOGGER.info(f"last-60 credits: {total_credits}")
LOGGER.info(f"last-60 GPA: {total_grades / grade_credits}")
