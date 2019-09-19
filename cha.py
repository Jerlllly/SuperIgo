#coding=utf-8
import requests
import time
import execjs
from bs4 import BeautifulSoup
import re
import json
from PIL import Image,ImageDraw
import pytesseract
from io import BytesIO
import base64
from sys import version_info

def base64_api(uname, pwd, softid, img):
    img = img.convert('RGB')
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    if version_info.major >= 3:
        b64 = str(base64.b64encode(buffered.getvalue()), encoding='utf-8')
    else:
        b64 = str(base64.b64encode(buffered.getvalue()))
    data = {"username": uname, "password": pwd, "softid": softid, "image": b64}
    result = json.loads(requests.post("http://api.ttshitu.com/base64", json=data).text)
    if result['success']:
        return result["data"]["result"]
    else:
        return result["message"]
    return ""

cookie={
            'FROM_TYPE':'weixin',
            # 'Hm_lvt_7ecd21a13263a714793f376c18038a87':'1567944549', 
            'wechatSESS_ID':'dc545c8451726d5d5ed6a182d719547eb0bd2ebe071f2b81', 
            # 'SERVERID':'d3936289adfff6c3874a2579058ac651|'+str(int(time.time()))+'|1568857324', 
            # 'Hm_lpvt_7ecd21a13263a714793f376c18038a87':str(int(time.time()))
        }
res=requests.get("https://wechat.v2.traceint.com/index.php/reserve/layout/libid=324.html",cookies=cookie)
res.encoding="utf-8"
soup=BeautifulSoup(res.text,"html.parser")
js=soup.find_all("script")[1:]
paser=requests.get(js[1].get("src"))
paser.encoding="gb18030"
paser=paser.text
encode=""
if paser[4]=="_":
    findres=paser.find(".dec(")
    # print(findres)
    i=findres
    while paser[i]!=")":
        i+=1
    code="return "+paser[findres-1:i+1]+"};"
    findres=paser.find("T.ajax_get")
    code=paser[:findres]+code
    trigger=execjs.compile(code)
    encode=trigger.call("reserve_seat")
else:
    findres=paser.find("+\"&\"+")
    i=findres+5
    while paser[i]!=")":
        i+=1
    code="return "+paser[findres+5:i+1]+"};"
    findres=paser.find("T.ajax_get")
    code=paser[:findres]+code
    trigger=execjs.compile(code)
    encode=trigger.call("reserve_seat")
while 1:
    t0=time.time()
    result=""
    while len(result)!=4:
        image=requests.get("https://wechat.v2.traceint.com/index.php/misc/verify.html",cookies=cookie)
        result=base64_api("a85853","zhanglei1210","8d2c53542c038e0941179ada6eb7bf6f",Image.open(BytesIO(image.content)))
    print(time.time()-t0)
    print(result)
    res=requests.get("https://wechat.v2.traceint.com/index.php/reserve/get/libid=324&"+encode+"=21,25&yzm="+result,cookies=cookie)

    res.encoding="gb18030"
    print(json.loads(res.text)["msg"])
