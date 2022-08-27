import aiohttp
from constants.constants import my_constants
from urllib.parse import urlparse
from urllib.parse import parse_qs
from scripts.data import DataExtractor
import pprint
import os

class GenesisInformation():
    def __init__(self):
        pass

    async def get_cookie(self, email, password, session: aiohttp.ClientSession, highschool_name):
        data = my_constants[highschool_name]["data"]
        data["j_username"] = email
        data["j_password"] = password
        async with session as my_session:
            async with my_session.post(url=my_constants[highschool_name]['j_check'], data=data,  headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}) as response:
                cookie = my_session.cookie_jar.filter_cookies(my_constants[highschool_name]['j_check'])
                j_id = str(cookie["JSESSIONID"]).split("=")[1]

                url = str(response.url)
                parsed_url = urlparse(url)
                captured_data = parse_qs(parsed_url.query)
                return j_id, captured_data, url

    async def main_info(self, highschool_name, j_session_id, url, user: int = 0):
        html = await self.get(j_session_id, url)
        soup = DataExtractor(highschool_name, html, "html.parser")
        users, whereabouts, schedule = soup.both_where_sche(user)
        schedule_link, name, grade, student_id, state_id = soup.schedule(schedule)
        return student_id, users, grade

    async def front_page_data(self, highschool_name, j_session_id, url, user: int = 0):
        html = await self.get(j_session_id, url)
        soup = DataExtractor(highschool_name, html, "html.parser")
        users, whereabouts, schedule = soup.both_where_sche(user)
        img_url, counselor_name, age, birthday, locker = soup.whereabouts(whereabouts)
        schedule_link, name, grade, student_id, state_id = soup.schedule(schedule)
        return (users, img_url, counselor_name, age, birthday, locker, schedule_link, name, grade, student_id, state_id)

    async def course_data(self, highschool_name, j_session_id, url, mp: str, student_id: int, courseid: str, coursection: str, course_name: str):
        data = {
            "tab1": "studentdata",
            "tab2": "gradebook",
            "tab3": "coursesummary",
            "studentid": student_id,
            "mp": mp,
            "action": "form",
            "courseCode": courseid,
            "courseSection": coursection
        }

        html = await self.get(j_session_id, url, data)
        soup = DataExtractor(highschool_name, html, "html.parser")
        assignments = soup.course_work(course_name)
        return assignments

    async def allMarkingPeriods(self, highschool_name, j_session_id, student_id: int):
        data = {
            "tab1": "studentdata",
            "tab2": "gradebook",
            "tab3": "weeklysummary",
            "action": "form",
            "studentid": student_id
            }

        url = my_constants[highschool_name]['root']+"/genesis/parents"
        html = await self.get(j_session_id, url, data)
        soup = DataExtractor(highschool_name, html, "html.parser")
        mps = soup.allMarkingPeriod()
        currmp = soup.currentMarkingPeriod()
        return {'mps':mps, 'curr_mp': currmp}



    async def grade_page_data(self, highschool_name, j_session_id, student_id: int, mp: str = None):

        def Merge(dict1, dict2):
            dict2.update(dict1)
            return dict2

        data = {
            "tab1": "studentdata",
            "tab2": "gradebook",
            "tab3": "weeklysummary",
            "action": "form",
            "studentid": student_id
        }

        course_data = {}

        url = my_constants[highschool_name]['root']+"/genesis/parents"
        html = await self.get(j_session_id, url, data)
        soup = DataExtractor(highschool_name, html, "html.parser")

        course_list = soup.courseIds()
        if mp is None:
            currmp = soup.currentMarkingPeriod()
        else:
            currmp = mp

        for course_dict in course_list:
            for course_name, val in course_dict.items():
                course_id = val[0]
                section = val[1]
                assignments = await self.course_data(highschool_name, j_session_id, url, currmp, student_id, course_id, section, course_name)
                course_data = Merge(course_data, assignments)

        return course_data

    async def current_grades(self, highschool_name, j_session_id, student_id: int, mp: str, grade: int=10):
        data = {
                "tab1": "studentdata",
                "tab2": "gradebook",
                "tab3": "weeklysummary",
                "action": "form",
                "studentid": student_id,
                "mpToView":mp
            }
        url = my_constants[highschool_name]['root'] + "/genesis/parents"
        html = await self.get(j_session_id, url, data)
        soup = DataExtractor(highschool_name, html, "html.parser")
        curr_courses_grades  = soup.current_grades()
        return curr_courses_grades 
        # else:
        #     data = {
        #         "tab1": "studentdata",
        #         "tab2": "gradebook",
        #         "tab3": "weeklysummary",
        #         "action": "form",
        #         "studentid": student_id,
        #         "mpToView":mp
        #     }
        #     url = my_constants[highschool_name]['root'] + "/genesis/parents"
        #     html = await self.get(j_session_id, url, data)
        #     soup = DataExtractor(highschool_name, html, "html.parser")
        #     curr_courses_grades  = soup.current_grades()
        #     return curr_courses_grades 

    async def get(self, j_session_id: str, url: str, headers=None):
        async with aiohttp.ClientSession(cookies={"JSESSIONID": j_session_id},  headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}) as session:
            response = await session.get(url=url, params=headers)
            html = await response.text()
            return html

    async def get_image(self, j_session_id: str, url: str, headers=None):
        async with aiohttp.ClientSession(cookies={"JSESSIONID": j_session_id},  headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}) as session:
            response = await session.get(url=url, params=headers)
            return response