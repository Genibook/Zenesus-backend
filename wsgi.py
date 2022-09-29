
from flask import Flask, jsonify, request, render_template
import aiohttp
import os
from scripts.genesis_info import GenesisInformation
import json
from flask_cors import CORS
from scripts.utils import info, initialize, parse_request_data


class Storage:
    def __init__(self):
        pass


myInfo = GenesisInformation()
app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = f"{os.urandom(24).hex()}"
CORS(app, support_credentials=True)


@app.route("/")
async def home():
    return render_template("index.html")


@app.route("/api/getusers", methods=["POST"])
async def getUsers():
    if request.method == "POST":
        async with aiohttp.ClientSession() as session:
            email, password, highschool, user = parse_request_data()

        try:
            j_session_id, student_id, users, grade, name = await initialize(
                session, email, password, highschool, user
            )
            return jsonify({"users": users})
        except Exception as e:
            print(e)
            return jsonify({"users": "0"})


@app.route("/api/login", methods=["POST"])
async def login():
    if request.method == "POST":
        data = {}
        async with aiohttp.ClientSession() as session:

            email, password, highschool, user = parse_request_data()

            try:
                (
                    image64,
                    j_session_id,
                    users,
                    img_url,
                    counselor_name,
                    age,
                    birthday,
                    locker,
                    schedule_link,
                    name,
                    grade,
                    student_id,
                    state_id,
                ) = await info(session, email, password, highschool, user, "image")

                data["img_url"] = img_url
                data["counselor_name"] = counselor_name
                data["age"] = age
                data["birthday"] = birthday
                data["locker"] = locker
                data["schedule_link"] = schedule_link
                data["name"] = name
                data["grade"] = grade
                data["student_id"] = student_id
                data["state_id"] = state_id
                data["image64"] = image64.decode("utf-8")

                return jsonify(data)
            except Exception as e:
                print(e)
                return jsonify(
                    {
                        "age": 15,
                        "img_url": "N/A",
                        "state_id": 123123112,
                        "birthday": "N/A",
                        "schedule_link": "N/A",
                        "name": "N/A",
                        "grade": 10,
                        "locker": "N/A",
                        "counselor_name": "N/A",
                        "id": 107600,
                        "image64": "N/A",
                    }
                )


@app.route("/api/courseinfos", methods=["POST"])
async def getcourseinfo():
    async with aiohttp.ClientSession() as session:
        email, password, highschool, user = parse_request_data()
        request_data = request.data
        request_data = json.loads(request_data.decode("utf-8"))
        mp = request_data["mp"]
        try:
            j_session_id, student_id, users, grade, name = await initialize(
                session, email, password, highschool, user
            )
        except Exception as e:
            print(e)
            return jsonify(
                {
                    "RANDOM COURSE NAME": [
                        {
                            "course_name": "N/A",
                            "mp": "N/A",
                            "dayname": "N/A",
                            "full_dayname": "N/A",
                            "date": "N/A",
                            "full_date": "N/A",
                            "teacher": "N/A",
                            "category": "N/A",
                            "assignment": "N/A",
                            "description": "N/A",
                            "grade_percent": "100",
                            "grade_num": "100/100",
                            "comment": "N/A",
                            "prev": "N/A",
                            "docs": "N/A",
                        }
                    ]
                }
            )

        grade_page_data = await myInfo.grade_page_data(
            highschool, j_session_id, student_id, mp
        )
       #  print(grade_page_data)
        return jsonify(grade_page_data)


@app.route("/api/currentgrades", methods=["POST"])
async def currentgrades():
    async with aiohttp.ClientSession() as session:

        email, password, highschool, user = parse_request_data()
        request_data = request.data
        request_data = json.loads(request_data.decode("utf-8"))
        mp = request_data["mp"]

        try:
            j_session_id, student_id, users, gradee, name = await initialize(
                session, email, password, highschool, user
            )
            grade = gradee
        except Exception as e:
            print(e)
            return jsonify({"grades": [["N/A", "N/A", "N/A", "100", "N/A"]]})

        curr_courses_grades = await myInfo.current_grades(
            highschool,
            j_session_id,
            student_id,
            mp,
        )
        return jsonify(curr_courses_grades)


@app.route("/api/availableMPs", methods=["POST"])
async def allMarkingPeriodsandCurrent():
    async with aiohttp.ClientSession() as session:

        email, password, highschool, user = parse_request_data()

        try:
            j_session_id, student_id, users, grade, name = await initialize(
                session, email, password, highschool, user
            )
        except Exception as e:
            print(e)
            return jsonify({"mps": ["MP1", "MP2"], "curr_mp": "MP1"})

        mps = await myInfo.allMarkingPeriods(highschool, j_session_id, student_id)
        return jsonify(mps)


@app.route("/api/loginConnection", methods=["POST"])
async def loginConnection():
    async with aiohttp.ClientSession() as session:
        email, password, highschool, user = parse_request_data()
        try:
            j_session_id, parameter_data, url = await myInfo.get_cookie(
                email, password, session, highschool
            )
            return jsonify({"code": 200, "message": "correct username/password"})
        except Exception as e:
            print(e)
            return jsonify({"code": 401, "message": "invalid username/password"})


@app.route("/api/gpas", methods=["POST"])
async def gpas():
    async with aiohttp.ClientSession() as session:
        email, password, highschool, user = parse_request_data()
        request_data = request.data
        request_data = json.loads(request_data.decode("utf-8"))
        mp = request_data["mp"]
        try:
            j_session_id, student_id, users, grade, name_of_student = await initialize(
                session, email, password, highschool, user
            )
        except Exception as e:
            print(e)
            return jsonify({"weighted gpa": 0.0, "unweighted gpa": 0.0})

        curr_courses_grades, courseWeights = await myInfo.getGpas(
            highschool, j_session_id, student_id, mp, grade
        )
        totalGrade = 0
        totalWeightedGrade = 0
        totalWeights = 0
        names_of_courses = []
        for course_weight in courseWeights:
            names_of_courses.append(course_weight["name"])
        for grade_data in curr_courses_grades["grades"]:
            if "n/a" in grade_data[3].replace("%", "").lower():
                continue
            elif "no grades" in grade_data[3].replace("%", "").lower():
                # assuming that if it is no grades, the entire thing is no grades
                return jsonify({"weighted gpa": 0.0, "unweighted gpa": 0.0})

            elif "not graded" in grade_data[3].replace("%", "").lower():
                continue
            else:
                name = grade_data[0]
                grade = float(grade_data[3].replace("%", ""))
            if grade == 0.0:
                continue
            try:
                idx = names_of_courses.index(name)
                weight = float(courseWeights[idx]["weight"])
                totalWeights += weight
                if (
                    "AP" in name
                    or "honors" in str(name).lower()
                    or str(name).startswith("H-")
                ) and (grade != 0.0):
                    totalWeightedGrade += (grade + 5) * weight
                    
                else:
                    totalWeightedGrade += grade * weight
                totalGrade += grade * weight
            except IndexError:
                # something went wrong --- maybe the course is not existing
                pass
            # print(totalWeights, totalWeightedGrade, totalGrade)
        # print(totalWeightedGrade, totalGrade, totalWeights)
        weightedGpa = round(totalWeightedGrade / totalWeights, 2)
        unweightedGpa = round(totalGrade / totalWeights, 2)

        return jsonify({"weighted gpa": weightedGpa, "unweighted gpa": unweightedGpa})


@app.route("/api/studentNameandIds", methods=["POST"])
async def studentNamesandIds():
    email, password, highschool,users = parse_request_data()
    async with aiohttp.ClientSession() as session:
        try:
            j_session_id, parameter_data, url = await myInfo.get_cookie(
                email, password, session, highschool
            )
        except Exception as e:
            print(e)
            return jsonify({"ids": ["N/A"], "names": ["N/A"]})

        names, ids = await myInfo.getNamesandIds(highschool, j_session_id, url)

        return jsonify({"names": names, "ids": ids})

@app.route("/api/monthSchedule", methods=["GET", "POST"])
async def getPastandNowAssignements():
    if request.method == "POST":
        email, password, highschool, user = parse_request_data()
    elif request.method == "GET":
        email = request.args.get("email")
        password = request.args.get("password")
        highschool = request.args.get("highschool")
        user = int(request.args.get("user"))
    async with aiohttp.ClientSession() as session:
        try:
            j_session_id, student_id, users, grade, name_of_student = await initialize(
                session, email, password, highschool, user
            )
        except Exception as e:
            print(e)
            return jsonify(
                {
                    "RANDOM COUSE NAME": [
                        {
                            "course_name": "N/A",
                            "date": "N/A",
                            "points": "25",
                            "category": "N/A",
                            "assignment": "N/A",
                            "description": "",
                            
                        }
                        
                    ]
                }
            )
        
        schedule = await myInfo.grade_page_data(
            highschool, j_session_id, student_id, None, "schedule"
        )
       #  print(grade_page_data)
        return jsonify(schedule)

@app.route("/pp")
def privacyPolicy():
    return render_template("pp.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
