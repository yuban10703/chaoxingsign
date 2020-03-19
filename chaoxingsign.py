import requests,json,time

#填入Cookie
headers={
  "Cookie":"",
  "User-Agent": "Mozilla/5.0 (iPad; CPU OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ChaoXingStudy/ChaoXingStudy_3_4.3.2_ios_phone_201911291130_27 (@Kalimdor)_11391565702936108810"
}
#填入uid
uid=""
coursedata=[]
activeList=[]
course_index=0
speed=10
status=0
status2=0
activates=[]
quantity=0
a=1
def taskactivelist(courseId,classId):
    global activeList,a
    url="https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId="+str(courseId)+"&classId="+str(classId)+"&uid="+uid
    res=requests.get(url,headers=headers)
    respon = res.status_code
    if respon==200:
        data=json.loads(res.text)
        activeList=data['activeList']
        #print(activeList)
        for item in activeList:
            if("nameTwo" not in item):
                continue
                print('1')
            if(item['activeType']==2 and item['status']==1):
                signurl=item['url']
                aid = getvar(signurl)
                    #print('2')
                if(aid not in activates):
                    print('[签到]',coursedata[i]['name'],'查询到待签到活动 活动名称:%s 活动状态:%s 活动时间:%s aid:%s'%(item['nameOne'],item['nameTwo'],item['nameFour'],aid))
                    sign(aid,uid)
                    a=2
                    #print('调用签到函数')
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
    if(res.text=="success"):
        print("用户:"+uid+" 签到成功！")
        activates.append(aid)
        status=2
    else:
        print("签到失败")  
        activates.append(aid)

        
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
index=0
for item in coursedata:
        print(str(index)+".课程名称:"+item['name'])
        index+=1
        quantity+=1
while 1:
    for i in range(quantity):
        taskactivelist(coursedata[i]['courseid'],coursedata[i]['classid'])
        time.sleep(20)
        if a==2:
            a=0
        else:
            print('[签到]监控运行中,',coursedata[i]['name'],'未查询到签到活动')
            
                
