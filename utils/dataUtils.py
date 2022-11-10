from constants.constants import *


def day_classifier(day: str):
    if day == "Mon":
        return "Monday"
    elif day == "Tue":
        return "Tuesday"
    elif day == "Wed":
        return "Wednesday"
    elif day == "Thu":
        return "Thursday"
    elif day == "Fri":
        return "Friday"
    elif day == "Sat":
        return "Saturday"
    elif day == "Sun":
        return "Sunday"
    else:
        return ""


def basicDataExtractorFromTDCell(data):
    try:
        category = (
            data[categoryCellNum].text.strip().split("\n\n\n\n\n\n\n\r\n")[1].strip()
        )
        assignment = data[assignmentCellNum].find("b").text.strip()
        description = (
            data[assignmentCellNum]
            .find("div")
            .text.strip()
            .replace("\r", " ")
            .replace("\n", " ")
        )
        if ("Comment from" in description) and (
            "Close" in description or "\nClose" in description
        ):
            description = ""
    except Exception as e:
        print(
            f"Basic Data Extractor from TDCell (including category assignment and description) - {e}"
        )
        category = assignment = description = ""
    return (category, assignment, description)


def gradesLogic(data):
    try:
        grade_percent = data[gradeCellNum].find("div").text.strip().replace("%", "")
        grade_num = (
            str(data[5].text)
            .replace(grade_percent, "")
            .replace("\r", "")
            .replace("\n", "")
            .replace(" ", "")
            .replace("%", "")
        )
        if "x" in grade_percent:
            grade_percent = (
                data[gradeCellNum].find_all("div")[1].text.strip().replace("%", "")
            )
            grade_num = grade_num.replace(grade_percent, "")

        lowered_grade_percent = grade_percent.lower()
        if grade_percent.lower() == "missing":
            grade_num = "Missing"
            grade_percent = "-1.0"
        elif grade_percent.lower() == "exempt":
            grade_num = "Exempt"
            grade_percent = "0.0"
        elif grade_percent.lower() == "absent":
            grade_num = "Absent"
            grade_percent = "0.0"
        elif grade_percent.lower() == "incomplete":
            grade_num = "Incomplete"
            grade_percent = "-1.0"
        elif not "/" in grade_num:
            grade_num = grade_percent
            grade_percent = "0.0"
    except Exception as e:
        print(f"Grades Logic Error - {e}")
        grade_percent = "0.0"
        grade_num = "No grade"

    return {"grade_num": grade_num, "grade_percent": grade_percent}


def scheduleGrades(data):
    grade_points = "N/A"
    try:

        grade_points = (
            data[gradeCellNum]
            .find("div")
            .find_all("div", recursive=False)[1]
            .text.replace("Assignment Pts:", "")
            .strip()
        )

        if "not" in grade_points.lower():
            grade_points = (
                data[gradeCellNum]
                .find("div")
                .find_all("div", recursive=False)[2]
                .text.replace("Assignment Pts:", "")
                .strip()
            )
    except Exception as e:
        print(f"Schedule Grades function error - {e}")
        grade_points = "0 - Error fetching points"

    return grade_points


def get_course_and_id(row):
    course_list = []
    try:
        row_data = (
            str(row.find("td").find("span").attrs["onclick"])
            .split("(")[1]
            .strip(";")
            .split(",")[1]
            .strip("'")
            .strip(")")
            .strip("'")
            .split(":")
        )
        row_course_id = row_data[0]
        row_course_section = row_data[1]

        course_name = str(row.find("td").find("span").find("u").text).strip()
        data = {f"{course_name}": [row_course_id, row_course_section]}

        course_list.append(data)
    except AttributeError:
        pass
    return course_list


def checkCourseName(name: str):

    if (
        str(name).startswith("AP")
        or "honors" in str(name).lower()
        or str(name).startswith("H-")
    ):
        return True
    else:
        return False


def genGradeHistoryGpaDict(
    grade,
    UnweightedtotalFGSTimesCredits,
    WeightedtotalFGSTimesCredits,
    totalCredits,
    SchoolYear,
):
    try:
        return {
            "grade": grade,
            "unweightedGPA": str(
                round(UnweightedtotalFGSTimesCredits / totalCredits, 2)
            ),
            "weightedGPA": str(round(WeightedtotalFGSTimesCredits / totalCredits, 2)),
            "schoolYear": SchoolYear,
        }
    except ZeroDivisionError:
        return {}
