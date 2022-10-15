import bs4
from bs4 import BeautifulSoup
from constants.constants import my_constants


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
        for idx, table_row in enumerate(table_rows):
            if idx == 0:
                image_src = table_row.find("img").attrs["src"]
                img_url = my_constants[self.highschool_name]["root"] + image_src
            if idx == 2:
                try:
                    counselor_name = str(table_row.text).split(":")[1].strip()
                except IndexError:
                    counselor_name = None
            if idx == 3:
                age = str(table_row.text).split(":")[1].strip()
            if idx == 4:
                birthday = str(table_row.text).split(":")[1].strip()
            if idx == 5:
                locker = str(table_row.text).split(":")[1].strip()
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

        def get_course_and_id(row):
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

        main_table = self.find("table", role="main")
        main_row = main_table.find_all("tr")[1]
        table = main_row.find("table", class_="list")
        row_even = table.find_all("tr", class_="listroweven")
        for row in row_even:
            get_course_and_id(row)

        row_odd = table.find_all("tr", class_="listrowodd")
        for row in row_odd:
            get_course_and_id(row)

        return course_list

    def course_work(self, course_name, mode="coursework"):
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
        ) = (
            teacher
        ) = (
            category
        ) = (
            assignment
        ) = description = grade_percent = grade_num = comment = prev = docs = ""
        course_namee = course_name
        assignments = {
            course_namee: [],
        }
        if mode == "coursework":
            main_table = self.find("table", role="main")
            main_row = main_table.find_all("tr")[1]
            table = main_row.find("table", class_="list")
            dates = str(table.find("tr").find("span").text)

            year_begin = str(dates.split("/")[2].split()[0])
            year_end = str(dates.split("/")[4])
            rows = table.find_all("tr", recursive=False)

            for row in rows:
                try:
                    if row["class"] == ["listheading"]:
                        continue
                except KeyError:
                    continue
                data = row.find_all("td", class_="cellLeft")
                if len(data) != 9:
                    continue
                mp = str(data[0].text).strip()
                divs = data[1].find_all("div")
                try:
                    dayname = divs[0].text
                    full_dayname = day_classifier(dayname)

                    month = int(str(divs[1]).split("/")[0].strip("<div>"))
                    if 7 >= month > 0:
                        date = divs[1].text
                        full_date = divs[1].text + "/" + year_end
                    else:
                        date = divs[1].text
                        full_date = divs[1].text + "/" + year_begin
                except IndexError:
                    pass

                try:
                    teacher = data[2].text.strip()
                    category = (
                        data[3].text.strip().split("\n\n\n\n\n\n\n\r\n")[1].strip()
                    )
                    assignment = data[4].find("b").text.strip()
                    description = (
                        data[4]
                        .find("div")
                        .text.strip()
                        .replace("\r", " ")
                        .replace("\n", " ")
                    )

                    if ("Comment from" in description) and (
                        "Close" in description or "\nClose" in description
                    ):
                        description = ""
                    
                    try:
                        grade_percent = data[5].find("div").text.strip().replace("%", "")
                        grade_num = (
                            str(data[5].text)
                            .replace(grade_percent, "")
                            .replace("\r", "")
                            .replace("\n", "")
                            .replace(" ", "")
                            .replace("%", "")
                        )
                        if "x" in grade_percent:
                            grade_percent = data[5].find_all("div")[1].text.strip().replace("%", "")
                            
                        grade_num = grade_num.replace(grade_percent, "")
                        # print(grade_percent)
                        # print(grade_num)
                        # print("/" in grade_percent)
                        if grade_percent.lower()  == "missing":
                            grade_num = "Missing"
                            grade_percent = "-1.0"
                        elif grade_percent.lower() == "exempt":
                            grade_num = "Exempt"
                            grade_percent = "0.0"
                        elif grade_percent.lower() == "absent":
                            grade_num = "Absent"
                            grade_percent = "0.0"
                        elif grade_percent.lower()  == "incomplete":
                            grade_num = "Incomplete"
                            grade_percent = "-1.0"    
                        elif not "/"  in grade_num:
                            grade_num = grade_percent
                            grade_percent = "0.0"
                    except Exception as e:
                        print(e)
                        grade_percent = "0.0"
                        grade_num = "No grade"

                    comment = str(data[6].find("div").find("div").text).strip()
                    prev = data[7].text.strip()
                    docs = data[8].text.strip()
                except AttributeError:
                    pass

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

            # print(assignments)

            return assignments
        else:
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
                if len(data) != 10:
                    continue

                del data[len(data) - 1]
                del data[len(data) - 1]
                del data[len(data) - 1]
                del data[len(data) - 1]
                if len(data) != 6:
                    continue

                ifgraded = data[5].find_all("div")
                if len(ifgraded) == 1:
                    continue

                mp = str(data[0].text).strip()
                date = data[1].find_all("div")[1].text.strip()
                try:
                    category = (
                        data[3].text.strip().split("\n\n\n\n\n\n\n\r\n")[1].strip()
                    )
                    assignment = data[4].find("b").text.strip()
                    description = (
                        data[4]
                        .find("div")
                        .text.strip()
                        .replace("\r", " ")
                        .replace("\n", " ")
                    )

                    if ("Comment from" in description) and (
                        "Close" in description or "\nClose" in description
                    ):
                        description = ""

                    # print(data[5].text)
                    try:
                        
                        grade_points = (
                            data[5]
                            .find("div")
                            .find_all("div", recursive=False)[1]
                            .text.replace("Assignment Pts:", "")
                            .strip()
                        )
                    except IndexError:
                        grade_points = "0.0"
                        continue

                except AttributeError:
                    pass

                data = {
                    "course_name": course_namee,
                    "date": date,
                    "points": grade_points,
                    "category": category,
                    "assignment": assignment,
                    "description": description,
                }
                assignments[course_namee].append(data)

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
