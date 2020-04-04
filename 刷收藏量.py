import time,hashlib,requests,json,time

username=''#账号
passwd=''#密码
book='nmsl'#书名
writer='nmsl'#作者名字
folder='109687111'#文件夹ID随便填就行

picurl="https://i.loli.net/2020/04/03/kbzNxYAL7fstuoX.png"#图片链接


data = []
data.append('--bBtm2w4jqNNple2J0jfYCgGEwpfAgF2zTaZZqG6Q\r\n')
data.append('Content-Disposition: form-data; name="uid"\r\n')
data.append('Content-Type: text/plain; charset=UTF-8\r\n')
data.append('Content-Transfer-Encoding: 8bit\r\n')
data.append('\r\n')
data.append('117729841'+ '\r\n')
data.append('--bBtm2w4jqNNple2J0jfYCgGEwpfAgF2zTaZZqG6Q\r\n')
data.append('Content-Disposition: form-data; name="cfid"\r\n')
data.append('Content-Type: text/plain; charset=UTF-8\r\n')
data.append('Content-Transfer-Encoding: 8bit\r\n')
data.append('\r\n')
data.append(folder + '\r\n')
data.append('--bBtm2w4jqNNple2J0jfYCgGEwpfAgF2zTaZZqG6Q\r\n')
data.append('Content-Disposition: form-data; name="source"\r\n')
data.append('Content-Type: text/plain; charset=UTF-8\r\n')
data.append('Content-Transfer-Encoding: 8bit\r\n')
data.append('\r\n')
data.append('0\r\n')
data.append('--bBtm2w4jqNNple2J0jfYCgGEwpfAgF2zTaZZqG6Q\r\n')
data.append('Content-Disposition: form-data; name="resinfo"\r\n')
data.append('Content-Type: text/plain; charset=UTF-8\r\n')
data.append('Content-Transfer-Encoding: 8bit\r\n')
datas = ''
for i in data:
    datas += i
data2=[]
data2.append('\r\n')
data2.append('--bBtm2w4jqNNple2J0jfYCgGEwpfAgF2zTaZZqG6Q\r\n')
data2.append('Content-Disposition: form-data; name="version"\r\n')
data2.append('Content-Type: text/plain; charset=UTF-8\r\n')
data2.append('Content-Transfer-Encoding: 8bit\r\n')
data2.append('\r\n')
data2.append('8.6' + '\r\n')
data2.append('--bBtm2w4jqNNple2J0jfYCgGEwpfAgF2zTaZZqG6Q--\r\n')
datas2 = ''
for i in data2:
    datas2 += i
headers = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; HUAWEI ALE-CL00 Build/MOB31T) com.chaoxing.mobile/ChaoXingStudy_3_4.3.6_android_phone_496_27 (@Kalimdor)_57c3eb14b06a443db750026b3754a8ad',
           'Content-Type':'multipart/form-data; boundary=bBtm2w4jqNNple2J0jfYCgGEwpfAgF2zTaZZqG6Q',
           'Host':'apps.chaoxing.com',
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
a=enc()
print(a[0],a[1])

def favorite(time,enc):
    data1 = {"cataid": "100000001", "cataName": "专题", "key": 'mooc_'+id,
            "content": {"accountKey": "cx_fanya", "aid": "mooc_211237260", "appid": "024f788b762eefd3ea71e05d0c8e003f",
                        "appname": book, "appurl": "https://special.zhexuezj.cn/mobile/mooc/tocourse/211237260",
                        "available": 1, "bind": 1, "cataid": "100000001", "clientType": 127, "description": "",
                        "focus": 0, "id": -1, "isPrivate": 1, "isWebapp": 1, "loginId": 2, "loginUrl": "",
                        "logopath": picurl,
                        "logoshowtype": 1, "needLogin": 0, "needRegist": 0, "norder": 0,
                        "otherConfig": {"author": writer, "id": "mooc_211237260", "authorPuid": "126098093", "level": 1000},
                        "productId": 3, "properties": "", "rights": 1, "usable": "", "useClientTool": 2,
                        "res_src": "market"}, "collectionFolder": 0,}
    alldata = datas + '\r\n' + json.dumps(data1) + '\r\n' + datas2

    url='http://apps.chaoxing.com/apis/subscribe/addExternalSubscribe.jspx?token=4faa8662c59590c6f43ae9fe5b002b42'+'&_time='+time+'&inf_enc='+enc
    res = requests.post(url,data=alldata,cookies=cookie, headers=headers,allow_redirects=False)
    print(res.text)
    # print(url)
for x in range(1,600):
    id=str(x)
    a = enc()
    favorite(a[0],a[1])
    time.sleep(0.5)
    print(x)