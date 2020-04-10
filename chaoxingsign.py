import requests
import json
import time
import datetime

# session = requests.session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}#这个头目前没什么用,留着备用...
allsubject = []
allname = []
allclassid = []
allcourseid = []
activates = []
allaid = []
cook = []
allobjectid = []
with open('conf.json', 'r', encoding='utf-8') as f:  # 读取配置文件
    conf = json.loads(f.read())
    print('获取配置成功')


class CxSign():  # 尝试写一下class.....结果发现写的乱七八糟......
    def __init__(self, num):  # 转换一下配置文件
        CxSign.username = conf['username'][num]  # 根据列表顺序来读取
        CxSign.passwd = conf['passwd'][num]

        if len(conf['SCKEY']) == 1:  # 如果只有一个参数
            CxSign.SCKEY = conf['SCKEY'][0]  # 那么所有的用户都用这一个参数
        else:
            CxSign.SCKEY = conf['SCKEY'][num]  # 如果不是一个参数,那就各用各的参数

        if len(conf['name']) == 1:
            CxSign.name = conf['name'][0]
        else:
            CxSign.name = conf['name'][num]

        if len(conf['address']) == 1:
            CxSign.address = conf['address'][0]
        else:
            CxSign.address = conf['address'][num]

        if len(conf['longitude']) == 1:
            CxSign.longitude = conf['longitude'][0]
        else:
            CxSign.longitude = conf['longitude'][num]

        if len(conf['latitude']) == 1:
            CxSign.latitude = conf['latitude'][0]
        else:
            CxSign.latitude = conf['latitude'][num]

        if len(conf['picname']) == 1:
            CxSign.picname = conf['picname'][0]
        else:
            CxSign.picname = conf['picname'][num]

    def login(num):  # 获取cookie,传入用户的列表位置,所有的参数都能对上...(应该能吧....)
        url = 'https://passport2-api.chaoxing.com/v11/loginregister'
        data = {'uname': CxSign(num).username, 'code': CxSign(num).passwd, }
        session = requests.session()
        cookie_jar = session.post(url=url, data=data, headers=headers).cookies
        cookie_t = requests.utils.dict_from_cookiejar(cookie_jar)
        cook.append(cookie_t)
        print('用户:', num, '获取cookie成功')
        # return cookie_t

    def subject(i):  # 获取课程
        url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata"
        res = requests.get(url, headers=headers, cookies=cook[i])
        cdata = json.loads(res.text)
        # coursedata=[]
        # dict_n = {}
        name = []
        classid = []
        courseid = []
        if (cdata['result'] != 1):
            print("课程列表获取失败")
        for item in cdata['channelList']:
            if ("course" not in item['content']):
                continue
            pushdata = {}
            # pushdata['user'] = str(i)  # 插入用户标记
            courseid.append(item['content']['course']['data'][0]['id'])
            name.append(item['content']['course']['data'][0]['name'])
            classid.append(item['content']['id'])
        allname.append(name)#套娃....
        allclassid.append(classid)
        allcourseid.append(courseid)
        # coursedata.append(pushdata)
        # allsubject.append(coursedata)
        # return coursedata

    def taskactivelist(i):  # 查找签到任务
        global a
        # aid = []
        url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
        for index in range(len(allname[i])):
            payload = {'courseId': str(allcourseid[i][index]), 'classId': str(allclassid[i][index]),
                       'uid': cook[i]['UID']}
            time.sleep(1.5)
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '用户:', i, '正在查询课程:', allname[i][index])
            res = requests.get(url, params=payload, headers=headers, cookies=cook[i])
            respon = res.status_code
            # print(index)
            if respon == 200:  # 网页状态码正常
                # print(res.text)
                data = json.loads(res.text)
                # print(data)
                activeList = data['activeList']  # 把所有任务提出来
                for item in activeList:  # 轮询所有的任务
                    if ("nameTwo" not in item):
                        continue
                    if (item['activeType'] == 2 and item['status'] == 1):  # 查找进行中的签到任务
                        # signurl = item['url']  # 提取activePrimaryId
                        aid = item['id']  # 提取activePrimaryId
                        if (aid not in activates):  # 查看是否签到过
                            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  '[签到]', allname[i][index], '查询到待签到活动 活动名称:%s 活动状态:%s 活动时间:%s aid:%s' % (
                                      item['nameOne'], item['nameTwo'], item['nameFour'], aid))
                            CxSign.sign(aid, i, index)  # 调用签到函数
            else:
                print('error', respon)  # 不知道为啥...

    def upload(i):  # 上传图片
        if len(CxSign(i).picname) == 0:
            return
        else:
            print('上传图片~~')
            tokenurl = 'https://pan-yz.chaoxing.com/api/token/uservalid'
            tokenres = requests.get(tokenurl, headers=headers, cookies=cook[0])  # 因为拍照签到的图片只需要一个ID,所以直接用第一个用户上传就行了,,,
            tokendict = json.loads(tokenres.text)
            token = tokendict['_token']
            uploadurl = 'https://pan-yz.chaoxing.com/upload'
            picname = CxSign(i).picname
            files = {'file': (picname, open(picname, 'rb'), 'image/webp,image/*',), }
            uploadres = requests.post(uploadurl, data={'puid': cook[0]['UID'], '_token': token}, files=files,
                                      headers=headers, cookies=cook[0])
            resdict = json.loads(uploadres.text)
            # allobjectid.append(resdict['objectId'])
            return (resdict['objectId'])

    def sign(aid, i, index):  # 签到,偷了个懒,所有的签到类型都用这个,我测试下来貌似都没问题
        url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"

        # try:
        #     name = CxSign(i).name
        # except:
        #     try:
        #         name = CxSign.name
        #     except:
        #         name = ''
        #
        # try:
        #     address = CxSign(i).address
        # except:
        #     try:
        #         address = CxSign.address
        #     except:
        #         address = ''
        #
        # try:
        #     longitude = CxSign(i).longitude
        # except:
        #     try:
        #         longitude = CxSign.longitude
        #     except:
        #         longitude = ''
        # try:
        #     latitude = CxSign(i).latitude
        # except:
        #     try:
        #         latitude = CxSign.latitude
        #     except:
        #         latitude = ''
        objectId = CxSign.upload(i)
        data = {'name': CxSign(i).name, 'address': CxSign(i).address, 'activeId': aid, 'uid': cook[i]['UID'],
                'longitude': CxSign(i).longitude, 'latitude': CxSign(i).latitude, 'objectId': objectId}
        # data = { 'activeId': aid, 'uid': cook[i]['UID'],}
        res = requests.post(url, data=data, headers=headers, cookies=cook[i])
        print("签到状态:", res.text)
        if res.text == 'success':
            CxSign.push(i, index, res.text)
        activates.append(aid)

    def push(i, index, msg):
        # try:
        #     E_SCKEY = CxSign(i).SCKEY
        # except:
        #     try:
        #         E_SCKEY = CxSign.SCKEY
        #     except:
        #         E_SCKEY = ''
        SCKEY = CxSign(i).SCKEY
        if SCKEY.isspace() or len(SCKEY) == 0:
            return
        else:
            api = 'https://sc.ftqq.com/' + SCKEY + '.send'
            title = u"签到辣!"
            content = '用户:' + str(i) + '\n\n课程: ' + allname[i][index] + '\n\n签到状态:' + msg
            data = {
                "text": title,
                "desp": content
            }
            requests.post(api, data=data)
            print('已推送~')


number = len(conf['username'])
if __name__ == "__main__":
    print("运行于普通模式")

    for n in range(number):
        CxSign.login(n)
        time.sleep(0.8)

    for m in range(number):
        CxSign.subject(m)
        time.sleep(0.8)
    while 1:
        for o in range(number):
            CxSign.taskactivelist(o)

else:
    print("运行于云函数模式")


    def main_handler(event, context):
        for n in range(number):
            CxSign.login(n)
            time.sleep(0.5)

        for m in range(number):
            CxSign.subject(m)
            time.sleep(0.5)

        for o in range(number):
            CxSign.taskactivelist(o)

if __name__ == "__main__":
    main_handler("", "")
