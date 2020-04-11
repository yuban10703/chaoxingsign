import requests
import json
import time
import datetime
import numpy as np

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}#这个头目前没什么用,留着备用...
with open('conf.json', 'r', encoding='utf-8') as f:  # 读取配置文件
    conf = json.loads(f.read())
    print('获取配置成功')

class CxSign():
    def __init__(self,conf_user):  # 转换一下配置文件
        self.username = conf_user['username']
        self.passwd = conf_user['passwd']
        self.SCKEY = conf_user['SCKEY']
        self.name = conf_user['name']
        self.address = conf_user['address']
        self.longitude = conf_user['longitude']
        self.latitude = conf_user['latitude']
        self.picname = conf_user['picname']
        self.item_all=[]
        self.aid_all=[]
        try:
            self.activates=np.load('activates.npy').tolist()
        except IOError as e:    #文件不存在
            self.activates=[]

    def login(self):  # 获取cookie
        url = 'https://passport2-api.chaoxing.com/v11/loginregister'
        data = {'uname': self.username, 'code': self.passwd }
        session = requests.session()
        cookie_jar = session.post(url=url, data=data, headers=headers).cookies
        self.cookie = requests.utils.dict_from_cookiejar(cookie_jar)
        print('获取cookie成功')

    def subject(self):  # 获取课程
        url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata"
        res = requests.get(url, headers=headers, cookies=self.cookie)
        cdata = json.loads(res.text)
        if (cdata['result'] != 1):
            print("课程列表获取失败")
        for item in cdata['channelList']:
            if ("course" in item['content']):
                self.item_all.append(item['content'])
            # # pushdata['user'] = str(i)  # 插入用户标记
            # courseid.append(item['content']['course']['data'][0]['id'])
            # name.append(item['content']['course']['data'][0]['name'])
            # classid.append(item['content']['id'])
        #print(self.item_all)


    def taskactivelist(self):  # 查找签到任务
        url = "https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist"
        for i in self.item_all:
            payload={'courseId': str(i['course']['data'][0]['id']), 'classId': str(i['id']),'uid': self.cookie['UID']}
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'正在查询课程:', i['course']['data'][0]['name'])
            res = requests.get(url, params=payload, headers=headers, cookies=self.cookie)
            if res.status_code==200:    #状态码正常
                data = json.loads(res.text)
                for item in data['activeList']:     #轮询签到任务
                    if ("nameTwo" in item):
                        if (item['activeType'] == 2 and item['status'] == 1):  # 查找进行中的签到任务
                            aid = item['id']  # 提取activePrimaryId
                            if (aid not in self.activates):  # 查看是否签到过
                                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    '[签到]', i['course']['data'][0]['name'], '查询到待签到活动 活动名称:%s 活动状态:%s 活动时间:%s aid:%s' % (
                                        item['nameOne'], item['nameTwo'], item['nameFour'], aid))
                                self.aid_all.append(aid)    #所有进行中的签到任务
                                self.sign(i['course']['data'][0]['name'],aid)  # 调用签到函数

    def upload(self):  # 上传图片
        if self.picname == '':
            return
        else:
            print('上传图片~~')
            tokenurl = 'https://pan-yz.chaoxing.com/api/token/uservalid'
            tokenres = requests.get(tokenurl, headers=headers, cookies=self.cookie)
            tokendict = json.loads(tokenres.text)
            token = tokendict['_token']
            uploadurl = 'https://pan-yz.chaoxing.com/upload'
            picname = self.picname
            try:
                files = {'file': (picname, open(picname, 'rb'), 'image/webp,image/*')}
            except FileNotFoundError as e:
                print('图片不存在 不上传图片')
                return
            uploadres = requests.post(uploadurl, data={'puid': self.cookie['UID'], '_token': token}, files=files,headers=headers, cookies=self.cookie)
            resdict = json.loads(uploadres.text)
            return (resdict['objectId'])

    def sign(self,course_name,aid):  # 签到,偷了个懒,所有的签到类型都用这个,我测试下来貌似都没问题
        url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
        objectId = self.upload()
        data = {'name': self.name, 'address': self.address, 'activeId': aid, 'uid': self.cookie['UID'],'longitude': self.longitude, 'latitude': self.latitude, 'objectId': objectId}
        res = requests.post(url, data=data, headers=headers, cookies=self.cookie)
        print("签到状态:", res.text)
        #这边不直接append的原因是长时间运行后这个列表肯定会越来越大
        #然后这边直接等于aid_all的话好像逻辑又有点奇怪 感觉好像activates是多余的
        self.activates=self.aid_all
        #存入所有正在进行中的且签到过的任务 这边的aid_all逻辑有点绕 但是试下来是可行的
        #如果是存入activates的话这个文件会越来越大
        try:
            np.save('activates.npy',np.array(self.aid_all))
        except OSError as e:
            pass
        if (not self.SCKEY.isspace()) and res.text=='success':
            self.push(course_name,res.text)

    def push(self,course_name,status):
        api = 'https://sc.ftqq.com/' + self.SCKEY + '.send'
        title = u"签到辣!"
        content = '课程: '+ course_name+'\n\n签到状态:' + status
        data = {
            "text": title,
            "desp": content
        }
        requests.post(api, data=data)
        print('已推送~')


if __name__ == "__main__":
    print("运行于普通模式")
    all_user=[]
    for user_conf in conf:
        user=CxSign(user_conf)
        all_user.append(user)
        user.login()
        user.subject()
    while(1):
        for user in all_user:
            user.taskactivelist()
            user.aid_all=[]
else:
    print("运行于云函数模式")
    def main_handler(event, context):
        for user_conf in conf:
            user=CxSign(user_conf)
            user.login()
            user.subject()
            user.taskactivelist()
