import requests
import json
import time
import datetime
# 用户写在同目录的json文件里
# server酱推送
SCKEY = ''
name = ''  # 签到后老师那里显示的名字,空着的话就是默认
address = '火星'  # 地址
latitude = '32.2829260000'  # 纬度
longitude = '43.9237990000'  # 经度
picname = ''  # 同目录下的照片名字,如果不用就留空 picname=''
speed = 5
with open('conf.json', 'r') as f:
    dict = json.load(f)
    print('获取配置成功')

username = list(dict.keys())
passwd = list(dict.values())  # 将字典变成列表,方便操作
session = requests.session()
coursedata = []
activeList = []
activates = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}


def login(username, password):  # 获取cookie
    url = 'https://passport2-api.chaoxing.com/v11/loginregister'
    data = {'uname': username, 'code': password, }
    session = requests.session()
    cookie_jar = session.post(url=url, data=data, headers=headers).cookies
    cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
    return cookie_t


def subject(i):  # 获取课程
    url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata"
    res = requests.get(url, headers=headers, cookies=cook[i])
    cdata = json.loads(res.text)

    dict_n = {}
    if (cdata['result'] != 1):
        print("课程列表获取失败")
    for item in cdata['channelList']:
        if ("course" not in item['content']):
            continue
        pushdata = {}
        pushdata['user'] = str(i)  # 插入用户标记
        pushdata['courseid'] = item['content']['course']['data'][0]['id']
        pushdata['name'] = item['content']['course']['data'][0]['name']
        pushdata['classid'] = item['content']['id']

        coursedata.append(pushdata)
    # return coursedata


def token():  # 获取上传图片用的token
    url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
    res = requests.get(url, headers=headers, cookies=cook[0])
    tokendict = json.loads(res.text)
    return (tokendict['_token'])


def upload():  # 上传图片
    if picname.isspace() or len(picname) == 0:
        return
    else:
        url = 'https://pan-yz.chaoxing.com/upload'
        files = {'file': (picname, open(picname, 'rb'),
                          'image/webp,image/*',), }
        res = requests.post(url, data={'puid': str(cook[0]['UID']), '_token': token(
        )}, files=files, headers=headers, cookies=cook[0])
        resdict = json.loads(res.text)
        return (resdict['objectId'])


def taskactivelist(user, courseId, classId):  # 查找签到任务
    global a
    url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId=" + \
          str(courseId) + "&classId=" + str(classId) + "&uid=" + str(cook[user]['UID'])
    res = requests.get(url, headers=headers, cookies=cook[user])
    respon = res.status_code
    if respon == 200:  # 网页状态码正常
        data = json.loads(res.text)
        activeList = data['activeList']
        for item in activeList:
            if ("nameTwo" not in item):
                continue
            if (item['activeType'] == 2 and item['status'] == 1):
                aid = item['id']  # 提取activePrimaryId
                if (aid not in activates):
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          '[签到]', coursedata[i]['name'], '查询到待签到活动 活动名称:%s 活动状态:%s 活动时间:%s aid:%s' % (
                              item['nameOne'], item['nameTwo'], item['nameFour'], aid))
                    sign(user, aid)  # print('调用签到函数')
                    a = 2
    else:
        print('error', respon)  # 不知道为啥...


def getvar(url):  # 查找activePrimaryId
    var1 = url.split("&")
    for var in var1:
        var2 = var.split("=")
        if (var2[0] == "activePrimaryId"):
            return var2[1]
    return "ccc"


def sign(user, aid):  # 签到,偷了个懒,所有的签到类型都用这个,我测试下来貌似都没问题
    global status, activates
    url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
    objectId = upload()
    res = requests.post(url, data={"name": name, "address": address, 'activeId': aid, 'uid': str(cook[user]['UID']),
                                   'longitude': longitude, 'latitude': latitude, 'objectId': objectId}, headers=headers,
                        cookies=cook[user])
    push(SCKEY, res.text)
    print("签到状态:", res.text)
    activates.append(aid)
    status = 2


def push(SCKEY, msg):
    if SCKEY.isspace() or len(SCKEY) == 0:
        return
    else:
        api = 'https://sc.ftqq.com/' + SCKEY + '.send'
        title = u"签到辣!"
        content = '课程: ' + coursedata[i]['name'] + '\n\n签到状态:' + msg
        data = {
            "text": title,
            "desp": content
        }
        req = requests.post(api, data=data)


cook = []
for i in range(len(dict)):
    a = login(username[i], passwd[i])
    cook.append(a)

for i in range(len(dict)):
    subject(i)
index = 1
for item in coursedata:  # 打印课程
    if item['user'] != a:
        index = 1
        print("-" * 40)
    print('用户:' + item['user'], '-', str(index) + ".课程名称:" + item['name'])

    index += 1
    a = item['user']

while 1:
    for i in range(len(coursedata)):
        time.sleep(speed)  # 休眠
        taskactivelist(eval(coursedata[i]['user']), coursedata[i]['courseid'], coursedata[i]['classid'])
        if a == 2:
            a = 0
        else:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '用户', coursedata[i]['user'], '[监控运行中]课程:',
                  coursedata[i]['name'], '未查询到签到活动')
