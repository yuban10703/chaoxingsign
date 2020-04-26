import aiohttp
import asyncio
import requests
import json


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.37'}
name = ''
address = ''
longitude = ''
latitude = ''
objectId = ''


class Objects:
    def __init__(self, item):
        self.courseid = item['content']['course']['data'][0]['id']
        self.name = item['content']['course']['data'][0]['name']
        self.classid = item['content']['id']


def login(username, passwd):  # 获取cookie
    url = 'https://passport2-api.chaoxing.com/v11/loginregister'
    data = {'uname': username, 'code': passwd, }
    session = requests.session()
    cookie_jar = session.post(url=url, data=data,).cookies
    cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
    return cookie_t


cookies = login('', '')
uid = cookies['UID']

tasks1 = []

async def taskactivelist(courseId, classId, session):
    url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
    payload = {'courseId': str(courseId), 'classId': str(classId), 'uid': uid}
    async with session.get(url, headers=headers, params=payload) as resp:
        if resp.status == 200:
            # print(await resp.text())
            cdata = json.loads(await resp.text())
            # activeList = cdata['activeList']
            for item in cdata['activeList']:  # 轮询所有的任务
                # print('>>>',item)
                if ("nameTwo" not in item):
                    continue
                if (item['activeType'] == 2 and item['status'] == 1):  # 查找进行中的签到任务
                    aid = item['id']  # 提取activePrimaryId
                    # print(item)
                    print('>>>',aid)
                    tasks1.append(asyncio.create_task(sign(aid, session)))
        await asyncio.gather(*tasks1)
                    # sign(aid)

async def sign(aid, session):  # 签到,偷了个懒,所有的签到类型都用这个,我测试下来貌似都没问题
    await asyncio.sleep(2)
    url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
    data = { 'activeId': aid, 'uid': uid,}
    print(data)
    async with session.post(url, data=data) as resp:
        print(resp.status)
        # print(await resp.text())

# def sign(aid,):  # 签到,偷了个懒,所有的签到类型都用这个,我测试下来貌似都没问题
#     url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
#     data = {'name': name, 'address': address, 'activeId': str(aid), 'uid': uid,
#             'longitude': longitude, 'latitude': latitude, 'objectId': objectId}
#     res = requests.post(url, data=data, headers=headers, cookies=cookies)
#     print("签到状态:", res.text)

async def subject():  # 获取课程
    url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata"
    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get(url) as resp:
            cdata = json.loads(await resp.text())
            print(cdata)
        tasks = []
        for item in cdata['channelList']:
            if ("course" not in item['content']):
                continue
            a = Objects(item)
            tasks.append(asyncio.create_task(taskactivelist(a.courseid, a.classid, session)))
        await asyncio.gather(*tasks)


async def main():
    await asyncio.create_task(subject())


asyncio.run(main())
