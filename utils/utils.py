from flask import request
from scripts.genesis_info import GenesisInformation
import json
from flask_cors import CORS
import base64
import aiohttp

myInfo = GenesisInformation()


async def getImage64(j_session_id: str, url: str, headers=None):
    async with aiohttp.ClientSession(
        cookies={"JSESSIONID": j_session_id},
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        },
    ) as session:
        response = await session.get(url=url, params=headers)
        test = await response.read()
        encoded_string = base64.b64encode(test)
        return encoded_string


def parse_request_data():
    request_data = request.data
    request_data = json.loads(request_data.decode("utf-8"))
    email = request_data["email"]
    password = request_data["password"]
    highschool = request_data["highschool"]
    user = request_data["user"]
    return email, password, highschool, user


async def info(session, email, password, highschool, user: int, mode="normal"):
    j_session_id, parameter_data, url = await myInfo.get_cookie(
        email, password, session, highschool
    )

    (
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

    if mode != "normal":
        # print("hi")
        image64 = await getImage64(j_session_id, img_url)
        # print("hi")
        return (
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
        )
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
    try:
        grade = float(grade)
    except SyntaxError:
        grade = float(grade[1])
    return j_session_id, student_id, users, grade, name
