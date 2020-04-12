import requests
import json
import time
import datetime
import numpy as np
import re
import urllib3
#from retrying import retry

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36'}#这个头目前没什么用,留着备用...
try:
    with open('conf.json', 'r', encoding='utf-8') as f:  # 读取配置文件
        conf = json.loads(f.read())
        print('获取配置成功')
except FileNotFoundError:
    print('未找到配置文件')
    print('软件退出')
    exit()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# def retry_if_connection_error(exception):
#     return isinstance(exception, requests.exceptions.ConnectionError)
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
        except IOError:    #文件不存在
            self.activates=[]
#    @retry(retry_on_exception=retry_if_connection_error)
    def login(self):  # 获取cookie
        url = 'https://passport2-api.chaoxing.com/v11/loginregister'
        data = {'uname': self.username, 'code': self.passwd }
        self.session = requests.session()
        cookie_jar = self.session.post(url=url, data=data, headers=headers).cookies
        self.session.cookies=cookie_jar
        self.cookie = requests.utils.dict_from_cookiejar(cookie_jar)
        print('获取cookie成功')
        
#    @retry(retry_on_exception=retry_if_connection_error)
    def subject(self):  # 获取课程
        url = "http://mooc1-api.chaoxing.com/mycourse/backclazzdata"
        res = requests.get(url, headers=headers, cookies=self.cookie)
        cdata = json.loads(res.text)
        if (cdata['result'] != 1):
            print("课程列表获取失败\n重试中")
            raise(requests.exceptions.ConnectionError)
        for item in cdata['channelList']:
            if ("course" in item['content']):
                self.item_all.append(item['content'])
            # # pushdata['user'] = str(i)  # 插入用户标记
            # courseid.append(item['content']['course']['data'][0]['id'])
            # name.append(item['content']['course']['data'][0]['name'])
            # classid.append(item['content']['id'])
        #print(self.item_all)

#    @retry(retry_on_exception=retry_if_connection_error)
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
                                self.sign(item['nameOne'],i['course']['data'][0]['id'],i['id'],i['course']['data'][0]['name'],aid)  # 调用签到函数

#    @retry(retry_on_exception=retry_if_connection_error)
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
            except FileNotFoundError:
                print('图片不存在 不上传图片')
                return
            uploadres = requests.post(uploadurl, data={'puid': self.cookie['UID'], '_token': token}, files=files,headers=headers, cookies=self.cookie)
            resdict = json.loads(uploadres.text)
            return (resdict['objectId'])

#    @retry(retry_on_exception=retry_if_connection_error)
    def sign(self,sign_type,course_id,class_id,course_name,aid):  # 签到,偷了个懒,所有的签到类型都用这个,我测试下来貌似都没问题
        status=False    #一般签到就直接签完了 要加状态判断以用于决定后面的sever酱是否推送
        url = "https://mobilelearn.chaoxing.com/pptSign/stuSignajax"
        if '位置' in sign_type:
            data = {
                'name': self.name, 
                'address': self.address,
                'activeId': aid, 
                'uid': self.cookie['UID'],
                'longitude': self.longitude, 
                'latitude': self.latitude, 
                }
        elif '手势' in sign_type:
            data = {
                'name': self.name, 
                'activeId': aid, 
                'uid': self.cookie['UID'],
                'longitude': -1, 
                'latitude': -1, 
                }
        elif '二维码' in sign_type:
            data = {
                'name': self.name, 
                'activeId': aid, 
                'uid': self.cookie['UID'],
                'longitude': -1, 
                'latitude': -1, 
                }
        else:
            r = self.session.get('https://mobilelearn.chaoxing.com/widget/sign/pcStuSignController/preSign?activeId={}&classId={}&fid=39037&courseId={}'.format(aid,class_id,course_id),headers=headers,verify=False)
            title = re.findall('<title>(.*)</title>', r.text)[0]
            if "签到成功" not in title:
                objectId = self.upload()
                data = {
                    'name': self.name, 
                    'address': self.address, 
                    'activeId': aid, 
                    'uid': self.cookie['UID'],
                    'longitude': self.longitude, 
                    'latitude': self.latitude, 
                    'objectId': objectId
                    }
            else:
                status=True
        if not status:
            res = requests.post(url, data=data, headers=headers, cookies=self.cookie)
            text=res.text
        else:
            text="success"
        print("签到状态:", text)
        #这边不直接append的原因是长时间运行后这个列表肯定会越来越大
        #然后这边直接等于aid_all的话好像逻辑又有点奇怪 感觉好像activates是多余的
        self.activates=self.aid_all
        #存入所有正在进行中的且签到过的任务 这边的aid_all逻辑有点绕 但是试下来是可行的
        #如果是存入activates的话这个文件会越来越大
        try:
            np.save('activates.npy',np.array(self.aid_all))
        except OSError:
            pass
        if ((not self.SCKEY.isspace()) and (not self.SCKEY=='')) and text=='success':
            print('推送中')
            self.push(course_name,text)

#    @retry(retry_on_exception=retry_if_connection_error)
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
        print('用户'+user_conf['username']+'登陆中')
        user.login()
        print('拉取用户'+user_conf['username']+'课程中')
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
            print('用户'+user_conf['username']+'登陆中')
            user.login()
            print('拉取用户'+user_conf['username']+'课程中')
            user.subject()
            user.taskactivelist()
