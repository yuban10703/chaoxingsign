import requests
import json
import time
import datetime

username = ''  # 账号
passwd = ''  # 密码
# server酱推送
SCKEY = ''
name = ''  # 签到后老师那里显示的名字,空着的话就是默认
address = '火星'  # 地址
latitude = '32.2829260000'  # 纬度
longitude = '43.9237990000'  # 经度
picname = 'a.png'  # 同目录下的照片名字,如果不用就留空 picname='',不然会报错...
# 设置轮询间隔(单位:秒,建议不低于5)
speed = 1

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}
coursedata = []
activeList = []
course_index = 0
status = 0
activates = []
a = 1
index = 0


def login(username, passwd):  # 获取cookie
    url = 'https://passport2-api.chaoxing.com/v11/loginregister'
    data = {'uname': username, 'code': passwd, }
    session = requests.session()
    cookie_jar = session.post(url=url, data=data, headers=headers).cookies
    cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
    return cookie_t


cookie = login(username, passwd)
uid = cookie['UID']


def token():  # 获取上传图片用的token
    url = 'https://pan-yz.chaoxing.com/api/token/uservalid'
    res = requests.get(url, headers=headers, cookies=cookie)
    tokendict = json.loads(res.text)
    return (tokendict['_token'])


def upload():  # 上传图片
    if picname.isspace() or len(picname) == 0:
        return
    else:
        url = 'https://pan-yz.chaoxing.com/upload'
        files = {'file': (picname, open(picname, 'rb'),
                          'image/webp,image/*',), }
        res = requests.post(url, data={'puid': uid, '_token': token(
        )}, files=files, headers=headers, cookies=cookie)
        resdict = json.loads(res.text)
        return (resdict['objectId'])


def taskactivelist(courseId, classId):  # 查找签到任务
    global a
    url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
    payload = {'courseId': str(courseId), 'classId': str(classId), 'uid': uid}
    res = requests.get(url, params=payload, headers=headers, cookies=cookie)
    respon = res.status_code
    if respon == 200:  # 网页状态码正常
        data = json.loads(res.text)
        activeList = data['activeList']  # 把所有任务提出来
        for item in activeList:
            if ("nameTwo" not in item):
                continue
            if (item['activeType'] == 2 and item['status'] == 1):  # 查找进行中的签到任务
                # signurl = item['url']  # 提取activePrimaryId
                aid = item['id']  # 提取activePrimaryId
                if (aid not in activates):  # 查看是否签到过
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          '[签到]', coursedata[i]['name'], '查询到待签到活动 活动名称:%s 活动状态:%s 活动时间:%s aid:%s' % (
                          item['nameOne'], item['nameTwo'], item['nameFour'], aid))
                    sign(aid, uid)  # 调用签到函数
                    a = 2
    else:
        print('error', respon)  # 不知道为啥...


def sign(aid, uid):  # 签到,偷了个懒,所有的签到类型都用这个,我测试下来貌似都没问题
    global status, activates
    url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
    objectId = upload()
    data = {'name': name, 'address': address, 'activeId': aid, 'uid': uid,
            'longitude': longitude, 'latitude': latitude, 'objectId': objectId}
    res = requests.post(url, data=data, headers=headers, cookies=cookie)
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


url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1"
res = requests.get(url, headers=headers, cookies=cookie)
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
    coursedata.append(pushdata)
print("获取成功:")

for item in coursedata:  # 打印课程
    print(str(index) + ".课程名称:" + item['name'])
    index += 1

while 1:
    for i in range(index):
        time.sleep(speed)  # 休眠
        taskactivelist(coursedata[i]['courseid'], coursedata[i]['classid'])
        if a == 2:
            a = 0
        else:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  '[监控运行中]课程:', coursedata[i]['name'], '未查询到签到活动')
