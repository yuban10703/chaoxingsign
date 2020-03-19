import requests,json,time,datetime

#填入Cookie
headers={
  "Cookie":"",
  "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; HUAWEI ALE-CL00 Build/MOB31T) com.chaoxing.mobile/ChaoXingStudy_3_4.3.6_android_phone_496_27 (@Kalimdor)_57c3eb14b06a443db750026b3754a8ad"
}
#填入uid
uid=""
#设置速度(建议不低于5)
speed=10
#server酱推送
SCKEY=''
coursedata=[]
activeList=[]
course_index=0
status=0
activates=[]
a=1
index=0
def taskactivelist(courseId,classId):
    global a
    url="https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId="+str(courseId)+"&classId="+str(classId)+"&uid="+uid
    res=requests.get(url,headers=headers)
    respon = res.status_code
    if respon==200:#网页状态码正常
        data=json.loads(res.text)
        activeList=data['activeList']
        #print(activeList)
        for item in activeList:
            if("nameTwo" not in item):
                continue
            if(item['activeType']==2 and item['status']==1):
                signurl=item['url']#提取activePrimaryId
                aid = getvar(signurl)
                if(aid not in activates):
                    nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') #获取当前时间
                    print(nowtime,'[签到]',coursedata[i]['name'],'查询到待签到活动 活动名称:%s 活动状态:%s 活动时间:%s aid:%s'%(item['nameOne'],item['nameTwo'],item['nameFour'],aid))
                    sign(aid,uid)#print('调用签到函数')
                    
                    a=2

    else:
            print('error',respon)#不知道为啥...


def getvar(url):
    var1 = url.split("&")
    for var in var1:
        var2 = var.split("=")
        if(var2[0]=="activePrimaryId"):
            return var2[1]
    return "ccc"  


def sign(aid,uid):
    global status,activates
    url="https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId="+aid+"&uid="+uid+"&clientip=&latitude=-1&longitude=-1&appType=15&fid=0"
    res=requests.get(url,headers=headers)
    push(SCKEY,res.text)
    if(res.text=="success"):
        print("用户:"+uid+" 签到成功！")
        activates.append(aid)
        status=2
    else:
        print(res.text,'签到失败')  
        activates.append(aid)

def push(SCKEY,msg):
    if SCKEY.isspace() or len(SCKEY)==0:
        return
    else:
        api = 'https://sc.ftqq.com/'+SCKEY+'.send'
        title = u"签到辣!"
        content = '课程: '+coursedata[i]['name']+'\n\n签到状态:'+msg
        data = {
           "text":title,
           "desp":content
        }
        req = requests.post(api,data = data)        


url="http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1"
res=requests.get(url,headers=headers)
cdata=json.loads(res.text)
if(cdata['result']!=1):
    print("课程列表获取失败")
for item in cdata['channelList']:
    if("course" not in item['content']):
        continue
    pushdata={}
    pushdata['courseid']=item['content']['course']['data'][0]['id']
    pushdata['name']=item['content']['course']['data'][0]['name']
    #pushdata['imageurl']=item['content']['course']['data'][0]['imageurl']
    pushdata['classid']=item['content']['id']
    coursedata.append(pushdata)
print("获取成功:")

for item in coursedata:#打印课程
        print(str(index)+".课程名称:"+item['name'])
        index+=1
        
while 1:
    for i in range(index):
        time.sleep(speed)#休眠
        taskactivelist(coursedata[i]['courseid'],coursedata[i]['classid'])
        if a==2:
            a=0
        else:           
            nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(nowtime,'[监控运行中]课程:',coursedata[i]['name'],'未查询到签到活动')         
