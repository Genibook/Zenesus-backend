from flask import request
from scripts.genesis_info import GenesisInformation
import json
from flask_cors import CORS

myInfo = GenesisInformation()


def parse_request_data():
    request_data = request.data
    request_data = json.loads(request_data.decode("utf-8"))
    email = request_data["email"]
    password = request_data["password"]
    highschool = request_data["highschool"]
    user = request_data["user"]
    return email, password, highschool, user


async def info(session, email, password, highschool, user: int):
    j_session_id, parameter_data, url = await myInfo.get_cookie(
        email, password, session, highschool
    )
    (
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
    ) = await myInfo.front_page_data(highschool, j_session_id, url, user)

    return (
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
    )


async def initialize(session, email: str, password: str, highschool: str, user: int):
    j_session_id, parameter_data, url = await myInfo.get_cookie(
        email, password, session, highschool
    )
    student_id, users, grade, name = await myInfo.main_info(
        highschool, j_session_id, url, user
    )
    grade = float(grade)
    return j_session_id, student_id, users, grade
