# -*- coding: UTF-8 -*-

import requests
import json
import time
import datetime


class CxSign:
    username = ''  # 账号
    passwd = ''  # 密码
    # server酱推送
    SCKEY = ''
    name = ''  # 签到后老师那里显示的名字,空着的话就是默认
    address = '火星'  # 地址
    latitude = '32.2829260000'  # 纬度
    longitude = '43.9237990000'  # 经度
    picname = 'a.png'  # 同目录下的照片名字,如果不用就留空 picname=''
    # 设置轮询间隔(单位:秒,建议不低于5)
    speed = 10

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'
    }
    coursedata = []
    activeList = []
    course_index = 0
    status = 0
    activates = []
    a = 1
    index = 0
    cookie = ''
    uid = 0

    def __init__(self, account):
        CxSign.username = account['username']  # 账号
        CxSign.passwd = account['passwd']  # 密码
        # server酱推送
        CxSign.SCKEY = account['SCKEY']
        CxSign.name = account['name']  # 签到后老师那里显示的名字,空着的话就是默认
        CxSign.address = account['address']  # 地址
        CxSign.latitude = account['latitude']  # 纬度
        CxSign.longitude = account['longitude']  # 经度
        CxSign.picname = account['picname']  # 同目录下的照片名字,如果不用就留空 picname=''
        # 设置轮询间隔(单位:秒,建议不低于5)
        CxSign.speed = account['speed']
        CxSign.login(self)

    def login(self):  # 获取cookie
        url = 'https://passport2-api.chaoxing.com/v11/loginregister'
        data = {'uname': CxSign.username, 'code': CxSign.passwd, }
        session = requests.session()
        cookie_jar = session.post(
            url=url, data=data, headers=CxSign.headers).cookies
        cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
        CxSign.cookie = cookie_t
        CxSign.uid = cookie_t['UID']
        # return cookie_t

    def token(self):  # 获取上传图片用的token
        url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
        res = requests.get(url, headers=CxSign.headers, cookies=CxSign.cookie)
        tokendict = json.loads(res.text)
        return (tokendict['_token'])

    def upload(self):  # 上传图片
        picname = CxSign.picname
        if picname.isspace() or len(picname) == 0:
            return
        else:
            url = 'https://pan-yz.chaoxing.com/upload'
            files = {
                'file': (picname, open(picname, 'rb'),
                         'image/webp,image/*',),
            }
            res = requests.post(url, data={
                'puid': CxSign.uid, '_token': CxSign.token(
                )
            }, files=files, headers=CxSign.headers, cookies=CxSign.cookie)
            resdict = json.loads(res.text)
            return (resdict['objectId'])

    def taskactivelist(self, courseId, classId):  # 查找签到任务
        CxSign.a
        url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId=" + \
              str(courseId) + "&classId=" + str(classId) + "&uid=" + CxSign.uid
        res = requests.get(url, headers=CxSign.headers, cookies=CxSign.cookie)
        respon = res.status_code
        if respon == 200:  # 网页状态码正常
            data = json.loads(res.text)
            activeList = data['activeList']
            # print(activeList)
            for item in activeList:
                if "nameTwo" not in item:
                    continue
                if item['activeType'] == 2 and item['status'] == 1:
                    signurl = item['url']  # 提取activePrimaryId
                    aid = CxSign.getvar(signurl)
                    if aid not in CxSign.activates:
                        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                              '[签到]', CxSign.coursedata[i]['name'], '查询到待签到活动 活动名称:%s 活动状态:%s 活动时间:%s aid:%s' % (
                                  item['nameOne'], item['nameTwo'], item['nameFour'], aid))
                        CxSign.sign(aid, CxSign.uid)  # print('调用签到函数')

                        CxSign.a = 2

        else:
            print('error', respon)  # 不知道为啥...

    def getvar(self, url):  # 查找activePrimaryId
        var1 = url.split("&")
        for var in var1:
            var2 = var.split("=")
            if (var2[0] == "activePrimaryId"):
                return var2[1]
        return "ccc"

    def sign(self, aid, uid):  # 签到,偷了个懒,所有的签到类型都用这个,我测试下来貌似都没问题
        CxSign.status, CxSign.activates
        url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
        objectId = CxSign.upload()
        res = requests.post(url, data={
            "name": CxSign.name, "address": CxSign.address, 'activeId': aid, 'uid': uid,
            'longitude': CxSign.longitude, 'latitude': CxSign.latitude, 'objectId': objectId
        }, headers=CxSign.headers, cookies=CxSign.cookie)
        CxSign.push(res.text)
        if (res.text == "success"):
            print("用户:" + uid + " 签到成功！")
            CxSign.activates.append(aid)
            status = 2
        else:
            print(res.text, '签到失败')
            CxSign.activates.append(aid)

    def push(self, msg):
        if CxSign.SCKEY.isspace() or len(CxSign.SCKEY) == 0:
            return
        else:
            api = 'https://sc.ftqq.com/' + CxSign.SCKEY + '.send'
            title = u"签到辣!"
            content = '课程: ' + CxSign.coursedata[i]['name'] + '\n\n签到状态:' + msg
            data = {
                "text": title,
                "desp": content
            }
            req = requests.post(api, data=data)

    def prepare(self):
        url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1"
        res = requests.get(url, headers=CxSign.headers, cookies=CxSign.cookie)
        cdata = json.loads(res.text)
        if (cdata['result'] != 1):
            print("课程列表获取失败")
        for item in cdata['channelList']:
            if ("course" not in item['content']):
                continue
            pushdata = {}
            pushdata['courseid'] = item['content']['course']['data'][0]['id']
            pushdata['name'] = item['content']['course']['data'][0]['name']
            # pushdata['imageurl']=item['content']['course']['data'][0]['imageurl']
            pushdata['classid'] = item['content']['id']
            CxSign.coursedata.append(pushdata)
        print("获取成功:")

        for item in CxSign.coursedata:  # 打印课程
            print(str(CxSign.index) + ".课程名称:" + item['name'])
            CxSign.index += 1

        while 1:
            for i in range(CxSign.index):
                time.sleep(CxSign.speed)  # 休眠
                CxSign.taskactivelist(self, CxSign.coursedata[i]['courseid'],
                                      CxSign.coursedata[i]['classid'])
                if CxSign.a == 2:
                    CxSign.a = 0
                else:
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          '[监控运行中]课程:', CxSign.coursedata[i]['name'], '未查询到签到活动')


def main_handler(event, context):
    # 此处读取json文件获取信息
    with open("account.json", 'r') as f:
        account = json.loads(f.read())
    sign = CxSign(account)
    sign.prepare()


if __name__ == "__main__":
    main_handler("", "")
