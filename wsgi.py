from flask import Flask, jsonify, request, render_template
import aiohttp
import os
from dotenv import load_dotenv
from scripts.genesis_info import GenesisInformation
import json
from flask_cors import CORS, cross_origin

class Storage():
    def __init__(self):
        pass


load_dotenv()
myInfo = GenesisInformation()
app = Flask(__name__, template_folder='templates')
app.config["SECRET_KEY"] = f"{os.urandom(24).hex()}"
CORS(app, support_credentials=True)

def parse_request_data():
    request_data = request.data
    request_data = json.loads(request_data.decode('utf-8'))
    email = request_data['email']
    password = request_data['password']
    highschool = request_data['highschool']
    return email, password, highschool

async def info(session, email, password, highschool):
    j_session_id, parameter_data, url = await myInfo.get_cookie(email, password, session, highschool)
    front_page_data = await myInfo.front_page_data(highschool, j_session_id, url)
    users, img_url, counselor_name, age, birthday, locker, schedule_link, name, grade, student_id, state_id = front_page_data
    return j_session_id, users, img_url, counselor_name, age, birthday, locker, schedule_link, name, grade, student_id, state_id

async def initialize(session, email, password, highschool):
    j_session_id, parameter_data, url = await myInfo.get_cookie(email, password, session, highschool)
    student_id, users = await myInfo.main_info(highschool, j_session_id, url)
    return j_session_id, student_id, users

@app.route("/")
async def home():
    return render_template("index.html")

@app.route("/api/login", methods=["POST"])
@cross_origin(supports_credentials=True)
async def login():
    if request.method == "POST":
        data = {}
        async with aiohttp.ClientSession() as session:
            
            email, password, highschool = parse_request_data()

            try:
                j_session_id, users, img_url, counselor_name, age, birthday, locker, schedule_link, name, grade, student_id, state_id = await info(
                    session, email, password, highschool)

                data['users'] = users
                data['img_url'] = img_url
                data['counselor_name'] = counselor_name
                data['age'] = age
                data['birthday'] = birthday
                data['locker'] = locker
                data['schedule_link'] = schedule_link
                data['name'] = name
                data['grade'] = grade
                data['student_id'] = student_id
                data['state_id'] = state_id

                return jsonify(data)
            except Exception as e:
                print(e)
                return jsonify({"age":15, "img_url":"N/A", "state_id":123123112, "birthday":"N/A", "schedule_link": "N/A", "name":"N/A", "grade": 10, "locker":"N/A", "counselor_name": "N/A", "id": 107600})


@app.route("/api/courseinfos", methods=["POST"])
@cross_origin(supports_credentials=True)
async def getcourseinfo():
    async with aiohttp.ClientSession() as session:
        email, password, highschool = parse_request_data()
        request_data = request.data
        request_data = json.loads(request_data.decode('utf-8'))
        mp = request_data["mp"]
        try:
            j_session_id, student_id, users = await initialize(session, email, password, highschool)
        except Exception as e:
            print(e)
            return jsonify({'1': [{
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
                                "docs": "N/A"
                                }]})

        grade_page_data = await myInfo.grade_page_data(highschool, j_session_id, student_id, mp)

        return jsonify(grade_page_data)

# TODO finish a thing where you can fetch old mp grades (that were locked in)
@app.route("/api/currentgrades", methods=["POST"])
@cross_origin(supports_credentials=True)
async def currentgrades():
    async with aiohttp.ClientSession() as session:

        email, password, highschool = parse_request_data()
        
        try:
            j_session_id, student_id, users = await initialize(session, email, password, highschool)
        except Exception as e:
            print(e)
            return jsonify({'grades':[["N/A", "N/A", "N/A", "100", "N/A"]]})

        curr_courses_grades  = await myInfo.current_grades(highschool, j_session_id, student_id)

        return jsonify(curr_courses_grades)

@app.route("/api/availableMPs", methods=["POST"])
@cross_origin(supports_credentials=True)
async def allMarkingPeriodsandCurrent():
    async with aiohttp.ClientSession() as session:

        email, password, highschool = parse_request_data()
        
        try:
            j_session_id, student_id, users = await initialize(session, email, password, highschool)
        except Exception as e:
            print(e)
            return jsonify({'mps':["MP1", "MP2"], 'curr_mp': 'MP1'})
        
        mps = await myInfo.allMarkingPeriods(highschool, j_session_id, student_id)
        return jsonify(mps)
        
@app.route("/api/loginConnection", methods=["POST"])
@cross_origin(supports_credentials=True)
async def checkUsernameAndPassword():
    async with aiohttp.ClientSession() as session:
        email, password, highschool = parse_request_data()
        try:
            j_session_id, parameter_data, url = await myInfo.get_cookie(email, password, session, highschool)
            return jsonify({"code":200, "message": "correct username/password"})
        except Exception as e:
            print(e)
            return jsonify({"code":401, "message": "invalid username/password"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
