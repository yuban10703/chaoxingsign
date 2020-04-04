import time,hashlib,requests,json
username=''#账号
passwd=''#密码
text='text'
title='title'
id=30000 #笔记编号
D='b06d289b-b69a-44d8-a7ef-'#笔记编号
#如果提示非个人笔记就改上面这些值,貌似是随机的,随便改,但是格式不能变,
headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; HUAWEI ALE-CL00 Build/MOB31T) com.chaoxing.mobile/ChaoXingStudy_3_4.3.6_android_phone_496_27 (@Kalimdor)_57c3eb14b06a443db750026b3754a8ad',
           'Connection': 'Keep-Alive'}
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
def enc():
    m_time=str(int(time.time()*1000))
    m_token='4faa8662c59590c6f43ae9fe5b002b42'
    m_encrypt_str='token='+m_token+'&_time='+m_time+'&DESKey=Z(AfY@XS'
    md5=hashlib.md5()
    md5.update(m_encrypt_str.encode('utf-8'))
    m_inf_enc=md5.hexdigest()
    return m_time,m_inf_enc




for i in range(20000):
    id+=1
    a=enc()
    url='https://noteyd.chaoxing.com/apis/note_note/uploadNote'
    payload={'token':'4faa8662c59590c6f43ae9fe5b002b42',
            '_time':a[0],
            'inf_enc':a[1]
}
    cid = D + str(id)
    data = {'action': '1',
            'attachment': '',
            'cid': cid,
            'content': text,
            'delete': '0',
            'describes': 'Test3',
            'files_url': '',
            'isRtf': '1',
            'notebookCid': '0',
            'puid': cookie['_uid'],
            'rtf_content': '%3Cp%3ETest1%3C%2Fp%3E',
            'sort': '0.0',
            'tag': '',
            'title': title,
            'top': '0',
            'version': '0'}
    req=requests.post(url,params=payload,data=data,headers=headers,cookies=cookie)
    print(req.text)
    time.sleep(0.5)
