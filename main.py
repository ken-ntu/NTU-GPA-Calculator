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

grades = []
with pdfplumber.open(file_path) as pdf_file:
    for i, page in enumerate(pdf_file.pages):
        text = page.extract_text()
        if "NATIONAL TAIWAN UNIVERSITY\nTRANSCRIPTOF ACADEMIC RECORD" in text:
            pattern = r'([A-Za-z0-9\-\:\,\.\(\)\~\!\u2160-\u216F\u2606]+)\s(\d) ([A-CFX][+-]?|PASS|W|EX|TR|NG|IP)\s'
            grades.extend(re.findall(pattern, text))

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

total_credits = 0
grade_credits = 0
pass_credits = 0
total_grades = 0
for _, credits, letter_grade in grades:
    if re.match(r'W|EX|TR|NG|IP', letter_grade):
        continue
    if re.match(r'PASS', letter_grade):
        pass_credits += int(credits)
        continue
    if letter_grade not in grade_to_points:
        raise ValueError("Extracted Grade not found!")
    
    grade_credits += int(credits)
    total_grades += grade_to_points[letter_grade] * int(credits)

total_credits = grade_credits + pass_credits
LOGGER.info(f"overall credits: {total_credits}")
LOGGER.info(f"overall GPA: {total_grades / grade_credits}")
