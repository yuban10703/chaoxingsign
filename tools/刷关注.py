import time,hashlib,requests,json
b=53551893#用户开始的ID,一般不用改
username=''#账号
passwd=''#密码

def enc():
    m_time=str(int(time.time()*1000))
    m_token='4faa8662c59590c6f43ae9fe5b002b42'
    m_encrypt_str='token='+m_token+'&_time='+m_time+'&DESKey=Z(AfY@XS'
    md5=hashlib.md5()
    md5.update(m_encrypt_str.encode('utf-8'))
    m_inf_enc=md5.hexdigest()
    return m_time,m_inf_enc
def login(username,passwd):
    payload={'uname':username,'code':passwd,'roleSelect':'true','loginType':'1'}
    # headers1 = {
    #     'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; HUAWEI ALE-CL00 Build/MOB31T) com.chaoxing.mobile/ChaoXingStudy_3_4.3.6_android_phone_496_27 (@Kalimdor)_57c3eb14b06a443db750026b3754a8ad',}

    s = requests.session()
    url='https://passport2-api.chaoxing.com/v11/loginregister'
    cookie_jar = s.post(url=url, params=payload, )

    url2='https://sso.chaoxing.com/apis/login/userLogin4Uname.do'
    cookie_jar2 = s.get(url=url2,).cookies
    cookie_full = requests.utils.dict_from_cookiejar(cookie_jar2)
    return cookie_full

cookie=login(username,passwd)
headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; HUAWEI ALE-CL00 Build/MOB31T) com.chaoxing.mobile/ChaoXingStudy_3_4.3.6_android_phone_496_27 (@Kalimdor)_57c3eb14b06a443db750026b3754a8ad',
           'Connection': 'Keep-Alive'}
url='http://learn.chaoxing.com/apis/friend/addUserFollow'


for i in range(50000):
    a = enc()
    payload = {'token': '4faa8662c59590c6f43ae9fe5b002b42',
               '_time': a[0],
               'uid': '42528010',
               'puid': b,
               'followedUid': cookie['_tid'],
               'followedPuid': cookie['_uid'],
               'inf_enc': a[1],
               }
    b+=1
    req=requests.get(url,params=payload,cookies=cookie,headers=headers,allow_redirects=False)
    print(req.text)
    print(b)
    time.sleep(0.2)
