from distutils.log import info
import bs4
from bs4 import BeautifulSoup
from constants.constants import *
from utils.dataUtils import *


class DataExtractor(BeautifulSoup):
    def __init__(self, highschool_name, html, praser="html.parser", **kwargs):
        super().__init__(html, praser, **kwargs)
        self.highschool_name = highschool_name
        self.html = html
        self.praser = "html.praser"

    def currentMarkingPeriod(self):
        main_table = self.find("table", role="main")
        main_row = main_table.find_all("tr")[1]
        table = main_row.find("table", class_="list")
        tr = table.find("tr", class_="listheading")
        td = tr.find("td", class_="cellCenter")
        curr_mp = td.find_all("option", selected=True)[0]
        return str(curr_mp.attrs["value"])

    def allMarkingPeriod(self):
        vals = []
        main_table = self.find("table", role="main")
        main_row = main_table.find_all("tr")[1]
        table = main_row.find("table", class_="list")
        tr = table.find("tr", class_="listheading")
        td = tr.find("td", class_="cellCenter")
        mps = td.find_all("option")
        for mp in mps:
            vals.append(mp.attrs["value"])
        return vals

    def both_where_sche(self, user):
        main_tables = self.find_all("table", role="main")
        users = len(main_tables)
        main_table = main_tables[user]
        table_main_row = main_table.find_all("tr")[1]
        table_row = table_main_row.find("tr", valign="top")
        table_datas = table_row.find_all("td", valign="top")
        whereabouts = table_datas[0]
        schedule = table_datas[1]

        return users, whereabouts, schedule

    def whereabouts(self, whereabouts: bs4.element.Tag):
        table_rows = whereabouts.find_all("tr", class_="listroweven")
        img_url, counselor_name, age, locker, birthday = None, None, None, None, None
        image_src = table_rows[0].find("img").attrs["src"]
        img_url = my_constants[self.highschool_name]["root"] + image_src

        try:
            counselor_name = str(table_rows[2].text).split(":")[1].strip()
        except IndexError:
            counselor_name = None
        age = str(table_rows[-3].text).split(":")[1].strip()
        birthday = str(table_rows[-2].text).split(":")[1].strip()
        locker = str(table_rows[-1].text).split(":")[1].strip()
        return (img_url, counselor_name, age, birthday, locker)

    def schedule(self, schedule: bs4.element.Tag):
        name, grade, student_id, state_id = None, None, None, None

        table = schedule.find("table", style="margin: auto; min-width: 500px;")
        td_a = table.find_all("td", class_="cellLeft", style="border: 0;")[0].find("a")
        schedule_link = (
            my_constants[self.highschool_name]["root"]
            + "/genesis/"
            + str(td_a.attrs["href"])
        )

        table = schedule.find("table")
        rows = table.find_all("tr")
        for idx, row in enumerate(rows):
            if idx == 0:
                name_without_last = str(row.find("span").text).strip("\n")
                thing = str(row.text).split("Grade:")
                name_last = thing[0].strip("\n").strip(name_without_last).strip()
                name = name_without_last + " " + name_last
                grade = str(thing[1]).strip("0").strip()

            if idx == 1:
                merge = row.find_all("span")
                student_id = str(merge[0].text).strip()
                state_id = str(merge[1].text).strip()

        return (schedule_link, name, grade, student_id, state_id)

    def current_grades(self):
        curr_courses_grades = {"grades": []}

        def find_grade(row):
            teacher = grade = not_graded = email = "N/A"

            try:
                teacherr = row.find_all("td", recursive=False)

                email = str(teacherr[1].find("a")["href"]).split("mailto:")[1].strip()

                teacher = teacherr[1].text.split("Email:")[0].strip()
            except (AttributeError, TypeError) as error:
                # print(error)
                pass

            try:
                course_name = str(row.find("td").find("span").find("u").text).strip()
            except AttributeError:
                course_name = str(row.find("td", class_="cellLeft").text).strip()

            try:
                grade = (
                    str(row.find_all("td")[3].text)
                    .replace("\n", "")
                    .replace("\r", "")
                    .replace("%", "")
                    .replace("PROJECTED", "")
                    .replace("*", "")
                    .strip()
                )
            except AttributeError:
                try:
                    not_graded = str(row.find("td", class_="cellCenter").text).strip()
                except AttributeError:
                    pass

            curr_courses_grades["grades"].append(
                [course_name, teacher, email, grade, not_graded]
            )

        main_table = self.find("table", role="main")
        main_row = main_table.find_all("tr")[1]
        table = main_row.find("table", class_="list")
        row_even = table.find_all("tr", class_="listroweven", recursive=False)
        row_odd = table.find_all("tr", class_="listrowodd", recursive=False)

        rows = row_even + row_odd
        for row in rows:
            find_grade(row)
        return curr_courses_grades

    def courseIds(self):
        course_list = []
        main_table = self.find("table", role="main")
        main_row = main_table.find_all("tr")[1]
        table = main_row.find("table", class_="list")
        row_even = table.find_all("tr", class_="listroweven")
        for row in row_even:
            course_list += get_course_and_id(row)

        row_odd = table.find_all("tr", class_="listrowodd")
        for row in row_odd:
            course_list += get_course_and_id(row)

        return course_list

    def CourseWork(self, course_name: str, mode: str):
        course_namee = (
            mp
        ) = (
            dayname
        ) = (
            full_dayname
        ) = (
            date
        ) = (
            full_date
        ) = teacher = grade_percent = grade_num = comment = prev = docs = None
        course_namee = course_name
        assignments = {
            course_namee: [],
        }
        main_table = self.find_all("table", role="main")[1]
        main_row = main_table.find_all("tr")[1]
        table = main_row.find("table", class_="list")
        rows = table.find_all("tr", recursive=False)

        for row in rows:
            try:
                if row["class"] == ["listheading"]:
                    continue
            except KeyError:
                continue

            data = row.find_all("td", recursive=False)
            if len(data) != listAssignmentDataCellsNum:
                continue

            # point cell
            pointCell = data[gradeCellNum]
            pointCellDataInformation = str(pointCell.text).lower().strip().strip("\n")
            # date cell
            dateCell = data[dateCellNum].find_all("div")
            date = dateCell[dateCellNum].text.strip()
            #  a normal point cell
            # 5/5
            # 100%
            # or
            # Not Graded
            # Assignment Pts: 5

            # a unormal cell is as such
            # 0.5x
            # Not Graded
            # Assignment Pts: 5
            # or
            # 0.5 x
            # 5/5
            # 100%

            if (not "not graded" in pointCellDataInformation) and (
                mode == "coursework"
            ):
                # this means that it is a percent cell e.g.
                # 5/5
                # 100%

                mp = str(data[mpCellNum].text).strip()
                dayname = dateCell[0].text.strip()
                teacher = data[teacherCellNum].text.strip()
                full_dayname = day_classifier(dayname)
                full_date = date

                category, assignment, description = basicDataExtractorFromTDCell(data)

                # please reference utils/dataUtils.py
                gradesDictionary = gradesLogic(data)
                # grade num example: 5/5
                grade_num = gradesDictionary["grade_num"]
                # grade percent example: 100%
                grade_percent = gradesDictionary["grade_percent"]
                try:
                    # this is very interesting beacuse if you look at the actual box it will be two divs and then the text
                    # but just getting the text should be fine as well
                    # before: comment = str(data[commentCellNum].find("div").find("div").text).strip()
                    # after: comment = str(data[commentCellNum].text).strip()
                    comment = str(data[commentCellNum].text).strip()
                except Exception as e:
                    print(
                        f"error when fetching comment, it shoud be attribute error - ${e}"
                    )
                    pass
                prev = data[prevCellNum].text.strip()
                docs = data[docsCellNum].text.strip()

                data = {
                    "course_name": course_namee,
                    "mp": mp,
                    "dayname": dayname,
                    "full_dayname": full_dayname,
                    "date": date,
                    "full_date": full_date,
                    "teacher": teacher,
                    "category": category,
                    "assignment": assignment,
                    "description": description,
                    "grade_percent": grade_percent,
                    "grade_num": grade_num,
                    "comment": comment,
                    "prev": prev,
                    "docs": docs,
                }
                assignments[course_namee].append(data)

            elif ("not graded" in pointCellDataInformation) and (mode == "schedule"):
                # print(pointCellDataInformation)
                # this means that not graded is in here
                # Not Graded
                # Assignment Pts: 5
                category, assignment, description = basicDataExtractorFromTDCell(data)

                grade_points = scheduleGrades(data)

                # print(course_namee, grade_points, category, assignment, description, date)

                if (
                    (course_namee is None)
                    or (grade_points is None)
                    or (category is None)
                    or (assignment is None)
                    or (description is None)
                    or (date is None)
                ):
                    continue
                data = {
                    "course_name": course_namee,
                    "date": date,
                    "points": grade_points,
                    "category": category,
                    "assignment": assignment,
                    "description": description,
                }
                assignments[course_namee].append(data)

        # print(assignments)
        return assignments

    def findCourseWeight(self, grade: int = 10):

        weights = []

        def find_weights(tr, idx):
            if grade >= 9:
                tds = tr.find_all("td")
                courseName = str(tds[0].text).strip("\n").strip("\r").strip()
                weight = str(tds[idx].text).strip("\n").strip("\r").strip()
                return {"name": courseName, "weight": weight}
            elif grade < 9:
                tds = tr.find_all("td")
                courseName = str(tds[0].text).strip("\n").strip("\r").strip()
                return {"name": courseName, "weight": "5.00"}

        idx = 8
        main_table = self.find("table", role="main")
        main_row = main_table.find_all("tr")[1]
        table = main_row.find("table", class_="list")
        row_heading = table.find("tr")
        row_even = table.find_all("tr", class_="listroweven")
        row_odd = table.find_all("tr", class_="listrowodd")
        cells = row_heading.find_all("td")
        for idxx, cell in enumerate(cells):
            if str(cell.text).strip() == "Att.":
                idx = idxx

        rows = row_even + row_odd
        for row in rows:
            weights.append(find_weights(row, idx))

        return weights

    def getCourseHistoryData(self, grade: int):

        main_table = self.find("table", role="main")
        main_row = main_table.find_all("tr")[1]
        table = main_row.find("table", class_="list")
        rows = table.find_all("tr", recursive=False)

        GpaHistory = []
        CurrGradeTheLoopisOn = -1
        # gonna be like [{"grade":"9", "unweightedGPA":"asdfasd", "weightedGPA":"asdfasd", "schoolYear":"2021-22",}]
        totalCredits = 0
        UnweightedtotalFGSTimesCredits = 0
        WeightedtotalFGSTimesCredits = 0

        for row in rows:
            try:
                if row["class"] == ["listheading"]:
                    continue
            except KeyError:
                continue

            datas = row.find_all("td")
            Description = datas[DescriptionCell].text.strip()
            if int(grade) >= 9:
                if len(datas) < 7:
                    if len(datas) == 4:
                        if "totals" in datas[GradeCell].text.strip().lower():
                            idx = rows.index(row)
                            datas_before = rows[idx - 1].find_all("td")
                            SchoolYear = str(datas_before[SchoolYearCell].text).strip()
                            Grade = str(datas_before[GradeCell].text).strip()
                            GpaHistory.append(
                                genGradeHistoryGpaDict(
                                    Grade,
                                    UnweightedtotalFGSTimesCredits,
                                    WeightedtotalFGSTimesCredits,
                                    totalCredits,
                                    SchoolYear,
                                )
                            )
                            UnweightedtotalFGSTimesCredits = 0
                            WeightedtotalFGSTimesCredits = 0
                            totalCredits = 0
                else:
                    FG = datas[HighschoolFGCell].text.strip()
                    Credits = datas[HighschoolEarnedCreditsCell].text.strip()

                    try:
                        # sometimes students take courses like online, it will be marked as P
                        UnweightedtotalFGSTimesCredits += float(FG) * float(Credits)

                        if checkCourseName(Description):
                            WeightedtotalFGSTimesCredits += (float(FG) + 5) * float(
                                Credits
                            )

                        else:
                            WeightedtotalFGSTimesCredits += float(FG) * float(Credits)

                    except ValueError:
                        continue

                    totalCredits += float(Credits)

            else:
                if len(datas) < 5:
                    if len(datas) == 1:
                        idx = rows.index(row)
                        datas_before = rows[idx - 1].find_all("td")
                        SchoolYear = str(datas_before[SchoolYearCell].text).strip()
                        Grade = str(datas_before[GradeCell].text).strip()
                        GpaHistory.append(
                            genGradeHistoryGpaDict(
                                Grade,
                                UnweightedtotalFGSTimesCredits,
                                WeightedtotalFGSTimesCredits,
                                totalCredits,
                                SchoolYear,
                            )
                        )
                        UnweightedtotalFGSTimesCredits = 0
                        WeightedtotalFGSTimesCredits = 0
                        totalCredits = 0

                else:

                    FG = datas[LessThanHighSchoolFGCell].text.strip()

                    try:
                        # sometimes FG is weird like AP for middle schoolers
                        UnweightedtotalFGSTimesCredits += float(FG) * 5

                        if checkCourseName(Description):
                            WeightedtotalFGSTimesCredits += (float(FG) + 5) * float(
                                Credits
                            )
                        else:
                            WeightedtotalFGSTimesCredits += float(FG) * float(Credits)

                    except ValueError:
                        continue

                    totalCredits += 5

                    idx = rows.index(row)
                    if idx == len(rows) - 1:
                        datas_before = rows[idx - 1].find_all("td")
                        SchoolYear = str(datas_before[SchoolYearCell].text).strip()
                        Grade = str(datas_before[GradeCell].text).strip()
                        GpaHistory.append(
                            genGradeHistoryGpaDict(
                                Grade,
                                UnweightedtotalFGSTimesCredits,
                                WeightedtotalFGSTimesCredits,
                                totalCredits,
                                SchoolYear,
                            )
                        )
                        UnweightedtotalFGSTimesCredits = 0
                        WeightedtotalFGSTimesCredits = 0
                        totalCredits = 0

        return GpaHistory
