# coding=UTF-8
import requests
import time
import execjs
from bs4 import BeautifulSoup
import re
import json
from PIL import Image, ImageDraw
import pytesseract
from io import BytesIO
import base64
from sys import version_info
import sys
import io
import multiprocessing

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

def book(lid, key):
    header = {
        "Host": "wechat.v2.traceint.com",
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age = 0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux Android 9 MIX2Build/PKQ1.190118.001wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044904 Mobile Safari/537.36 MMWEBID/1529 MicroMessenger/7.0.4.1420(0x27000437) Process/tools NetType/WIFI Language/zh_CN',
        'Accept': 'text/html, application/xhtml+xml, application/xml',
        'Referer': 'https: // wechat.v2.traceint.com/index.php/reserve/index.html?f = wechat',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN, en-US',
    }
    cookie = {

        }
    while True:
        res = requests.get("https://wechat.v2.traceint.com/index.php/prereserve/index.html",cookies=cookie,headers=header)
        res.encoding = "utf-8"
        # print(res.text)
        soup = BeautifulSoup(res.text, "html.parser")
        js = soup.find_all("script")[3:-1]
        if len(js)==0:
            print(key+":还没到预定时间呦")
            continue
        # print(js)
        paser = requests.get(js[1].get("src"))
        paser.encoding = "gbk"
        paser = paser.text
        # print(paser)
        if paser[4] == "_":
            findres = paser.find(".dec(")
            i = findres
            while paser[i] != ")":
                i += 1
            code = "return "+paser[findres-1:i+1]+"};"
            findres = paser.find("T.ajax_get")
            code = paser[:findres]+code
            # print(code)
            trigger = execjs.compile(code)
            encode = trigger.call("reserve_seat")
            # print(encode)
            res = "请输入验证码"
            while res == "请输入验证码":
                result=""
                while len(result)!=4:
                    image=requests.get("https://wechat.v2.traceint.com/index.php/misc/verify.html",cookies=cookie)
                    result=base64_api(Image.open(BytesIO(image.content)))
                res = requests.get("https://wechat.v2.traceint.com/index.php/prereserve/save/libid=" +str(lid)+"&"+encode+"="+key+"&yzm="+result, cookies=cookie)
                res.encoding = "gb18030"
                res = json.loads(res.text)["msg"]
            if "已经被人预定" in res:
                print("Orz..又被人抢了")
            if "成功" in res:
                    print("Bingo!!")
                    return
        else:
            findres = paser.find("+\"&\"+")
            i = findres+5
            while paser[i] != ")":
                i += 1
            code = "return "+paser[findres+5:i+1]+"};"
            findres = paser.find("T.ajax_get")
            code = paser[:findres]+code
            # print(code)
            trigger = execjs.compile(code)
            encode = trigger.call("reserve_seat")
            # print(encode)
            res = "请输入验证码"
            while res == "请输入验证码":
                image = requests.get(
                    "https://wechat.v2.traceint.com/index.php/misc/verify.html", cookies=cookie)
                result = base64_api( Image.open(BytesIO(image.content)))
                res = requests.get("https://wechat.v2.traceint.com/index.php/prereserve/save/libid=" +str(lid)+"&"+encode+"="+key+"&yzm="+result, cookies=cookie)
                res.encoding = "gb18030"
                res = json.loads(res.text)["msg"]
            if "已经被人预定" in res:
                print("Orz..又被人抢了")
            if "成功" in res:
                    print("Bingo!!")
                    return


def getmap(lname, num):
    alibid = 323
    blibid = 324
    # afile=open("./Aaera.html")
    # bfile=open("./Baera.html",encoding="UTF-8")

    # soup=BeautifulSoup(afile,"html.parser")
    # divs=soup.find_all("div")
    # Amap={}
    # for i in divs:
    #     if i.em.string != None:
    #         Amap[int(i.em.string)]=i.get("data-key")
    # outfile=open("./Amap.json","w")
    # json.dump(Amap,outfile)
    # soup=BeautifulSoup(bfile,"html.parser")
    # divs=soup.find_all("div")
    # Bmap={}
    # for i in divs:
    #     if i.em.string != None and i.em.string != "柱":
    #         Bmap[int(i.em.string)]=i.get("data-key")
    # outfile=open("./Bmap.json","w")
    # json.dump(Bmap,outfile)
    Amap = json.load(open("Amap.json"))
    Bmap = json.load(open("Bmap.json"))
    if lname == "A" or lname == "a":
        return alibid, Amap[str(num)]
    elif lname == "B" or lname == "b":
        return blibid, Bmap[str(num)]


def bingo():
    cookie = {
        }
    while True:
        res = requests.get(
            "https://wechat.v2.traceint.com/index.php/reserve/layout/libid=324.html", cookies=cookie)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        js = soup.find_all("script")[1:]
        if js[1].get("src")==None:
            print("你已经有座位了！")
            return 0
        paser = requests.get(js[1].get("src"))
        paser.encoding = "gb18030"
        paser = paser.text
        encode = ""
        if paser[4] == "_":
            findres = paser.find(".dec(")
            # print(findres)
            i = findres
            while paser[i] != ")":
                i += 1
            code = "return "+paser[findres-1:i+1]+"};"
            findres = paser.find("T.ajax_get")
            code = paser[:findres]+code
            trigger = execjs.compile(code)
            encode = trigger.call("reserve_seat")
        else:
            findres = paser.find("+\"&\"+")
            i = findres+5
            while paser[i] != ")":
                i += 1
            code = "return "+paser[findres+5:i+1]+"};"
            findres = paser.find("T.ajax_get")
            code = paser[:findres]+code
            trigger = execjs.compile(code)
            encode = trigger.call("reserve_seat")
        seats = soup.find_all(class_='grid_1')
        # image=requests.get("https://wechat.v2.traceint.com/index.php/misc/verify.html",cookies=cookie)
        # image.encoding="gb18030"
        # with open("temp.jpg","wb") as f:
        #     f.write(image.content)
        for i in seats:
            res = "请输入验证码"
            while res == "请输入验证码":
                image = requests.get(
                    "https://wechat.v2.traceint.com/index.php/misc/verify.html", cookies=cookie)
                result = base64_api( Image.open(BytesIO(image.content)))
                res = requests.get("https://wechat.v2.traceint.com/index.php/reserve/get/libid=324&" +
                                   encode+"="+i.get("data-key")+"&yzm="+result, cookies=cookie)
                res.encoding = "gb18030"
                res = json.loads(res.text)["msg"]
            if "不可选座" in res:
                print("触发滥用检测！")
                return
            if "已经被人预定" in res:
                print("Orz..又被人抢了")
            if "成功" in res:
                print("Bingo!!")
                return
        print("无余座")
if __name__ == '__main__':
    lib,key=getmap("B", 44)
    book(lib,key)
    # bingo()