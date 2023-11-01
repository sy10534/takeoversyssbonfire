import asyncio
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

placeholder = st.empty()
container = st.container

routedata = requests.get("https://data.etabus.gov.hk/v1/transport/kmb/route/").json()[
    "data"
]
stoplist = requests.get("https://data.etabus.gov.hk/v1/transport/kmb/stop").json()[
    "data"
]
stoplistlength = len(stoplist)
# routeetadata = 'https://data.etabus.gov.hk/v1/transport/kmb/route-eta/{route}/{service_type}'

godownbusdata = []
godownbus = [
    "26",
    "27",
    "42",
    "88",
    "95",
    "14D",
    "214",
    "26M",
    "26X",
    "290",
    "29M",
    "91P",
    "96R",
    "213A",
    "213D",
    "214P",
    "290A",
    "290B",
    "290X",
    "291P",
    "N214",
    "N216",
    "N290",
]
goupbusdata = []
goupbus = [
    "10",
    "21",
    "26",
    "27",
    "3M",
    "42",
    "88",
    "91",
    "92",
    "95",
    "14D",
    "214",
    "26M",
    "26X",
    "290",
    "29M",
    "606",
    "91M",
    "91P",
    "96R",
    "213D",
    "290A",
    "290B",
    "290X",
    "606A",
    "N216",
    "N290",
]


def getserial(target):
    num = 0
    while routedata[num]["route"] != target:
        num += 1
    return num


def buildstopid(target):
    output = []
    for i in stoplist:
        if i["name_tc"] == target:
            output.append(i["stop"])
    return output


stopid = buildstopid("白虹樓")


def getorig(route, bound):
    for bus in routedata:
        if bus["route"] == route and bus["bound"] == bound:
            return bus["orig_tc"]


def getdest(route, bound):
    for bus in routedata:
        if bus["route"] == route and bus["bound"] == bound:
            return bus["dest_tc"]


def getservicetype(route, bound):
    for bus in routedata:
        if bus["route"] == route and bus["bound"] == bound:
            return bus["service_type"]


def getstopid(route, bound, target):
    getdata = requests.get(
        f"https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{bound}/{1}"
    )
    if getdata.status_code == 200:
        getdata = getdata.json()["data"]
        for stops in getdata:
            theid = stops["stop"]
            for allstops in stoplist:
                if allstops["stop"] == theid and allstops["name_tc"] == target:
                    return theid
    return "bomb"


def getstopseq(route, bound, servicetype, stopid):
    getdata = requests.get(
        f"https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{route}/{bound}/{servicetype}"
    )
    if getdata.status_code == 200:
        getdata = getdata.json()["data"]
        for data in getdata:
            if (data["stop"]) == (stopid):
                return data["seq"]
    return "bomb"


def geteta(route, bound, servicetype, seq):
    if bound == "Outbound":
        bound = "O"
    if bound == "Inbound":
        bound = "I"
    getdata = requests.get(
        f"https://data.etabus.gov.hk/v1/transport/kmb/route-eta/{route}/{servicetype}"
    )
    print(route, getdata.status_code)
    if getdata.status_code == 200:
        getdata = getdata.json()["data"]
        output = []
        for data in getdata:
            if data["dir"] == bound and str(data["seq"]) == str(seq):
                output.append(data["eta"])

        # if output[0] == None:
        # return []
        return output
    return "bomb"


uphillbus = []
downhillbus = []
downhillid = ["58611212645F0AB1", "942E95B4336BDFA7", "3BA9C90738A8600D"]
uphillid = ["29740CCBBD82FC33", "9A16E73DC0B9AF6C"]


def buildbusdata(dataset):
    # route,outbound,orig,dest,service type, stopid
    for bus in dataset:
        inid = getstopid(bus, "inbound", "白虹樓")
        outid = getstopid(bus, "outbound", "白虹樓")
        if outid in downhillid:
            orig = getorig(bus, "O")
            dest = getdest(bus, "O")
            servicetype = getservicetype(bus, "O")
            stopid = getstopid(bus, "outbound", "白虹樓")
            stopseq = getstopseq(bus, "outbound", servicetype, stopid)
            eta = geteta(bus, "O", servicetype, stopseq)
            downhillbus.append(
                [bus, "Outbound", orig, dest, servicetype, stopid, stopseq, []]
            )
        elif outid in uphillid:
            orig = getorig(bus, "O")
            dest = getdest(bus, "O")
            servicetype = getservicetype(bus, "O")
            stopid = getstopid(bus, "outbound", "白虹樓")
            stopseq = getstopseq(bus, "outbound", servicetype, stopid)
            eta = geteta(bus, "O", servicetype, stopseq)
            uphillbus.append(
                [bus, "Outbound", orig, dest, servicetype, stopid, stopseq, []]
            )

        if inid in downhillid:
            orig = getorig(bus, "I")
            dest = getdest(bus, "I")
            servicetype = getservicetype(bus, "I")
            stopid = getstopid(bus, "inbound", "白虹樓")
            stopseq = getstopseq(bus, "inbound", servicetype, stopid)
            eta = geteta(bus, "I", servicetype, stopseq)
            downhillbus.append(
                [bus, "Inbound", orig, dest, servicetype, stopid, stopseq, []]
            )

        elif inid in uphillid:
            orig = getorig(bus, "I")
            dest = getdest(bus, "I")
            servicetype = getservicetype(bus, "I")
            stopid = getstopid(bus, "inbound", "白虹樓")
            stopseq = getstopseq(bus, "inbound", servicetype, stopid)
            eta = geteta(bus, "I", servicetype, stopseq)
            uphillbus.append(
                [bus, "Inbound", orig, dest, servicetype, stopid, stopseq, []]
            )


def turnintominutes(s):
    # first = (str)(s).find(":")
    firsty = -1
    for i in range(0, len(s)):
        if s[i] == ":":
            firsty = i
            break
    if firsty != -1:
        hour = (int)(s[firsty - 2]) * 10 + (int)(s[firsty - 1])
        minute = (int)(s[firsty + 1]) * 10 + (int)(s[firsty + 2])

        return hour * 60 + minute
    return 0


timenow = datetime.now()
stringnow = timenow.strftime("%H:%M:%S")
currenttime = turnintominutes(stringnow)
print(currenttime)


def extractcolumn(arr, col):
    output = []
    for i in arr:
        output.append(i[col])
    return output


def timetostring(arr):
    output = ""
    if len(arr) != 0:
        for i in range(0, (len(arr) - 1)):
            output = output + str(max(0, (int)(arr[i])))
            output = output + "m|"
        output = output + str(arr[len(arr) - 1])
        output = output + "m"
    else:
        output = "No bus"
    return output


def extracttime(arr, col):
    output = []
    for i in arr:
        holder = []
        for y in i[col]:
            if y != None:
                holder.append(turnintominutes(y) - currenttime)
        output.append(timetostring(holder))

    return output


def erasedup():
    global downhillbus
    global uphillbus
    downhillbus.sort()
    uphillbus.sort()
    i = 0
    while i < len(downhillbus) - 1:
        if downhillbus[i][0] == downhillbus[i + 1][0]:
            print("REPEATING:", downhillbus[i][0])
            downhillbus.pop(i)
            i = 0
        else:
            i += 1
    while i < len(uphillbus) - 1:
        if uphillbus[i][0] == uphillbus[i + 1][0]:
            print("REPEATING:", uphillbus[i][0])
            uphillbus.pop(i)
            i = 0
        else:
            i += 1


############build fun table region
############build fun table region
############build fun table region
############build fun table region
############build fun table region
############build fun table region

# buildbusdata(godownbus)
# buildbusdata(goupbus)
# erasedup()
# godownbustable = pd.DataFrame(
#     {
#         "route": extractcolumn(downhillbus, 0),
#         "bound": extractcolumn(downhillbus, 1),
#         "orig": extractcolumn(downhillbus, 2),
#         "destination": extractcolumn(downhillbus, 3),
#         "st": extractcolumn(downhillbus, 4),
#         "stopid": extractcolumn(downhillbus, 5),
#         "seq": extractcolumn(downhillbus, 6),
#         "eta": extracttime(downhillbus, 7),
#     }
# )
# goupbustable = pd.DataFrame(
#     {
#         "route": extractcolumn(uphillbus, 0),
#         "bound": extractcolumn(uphillbus, 1),
#         "orig": extractcolumn(uphillbus, 2),
#         "destination": extractcolumn(uphillbus, 3),
#         "st": extractcolumn(uphillbus, 4),
#         "stopid": extractcolumn(uphillbus, 5),
#         "seq": extractcolumn(uphillbus, 6),
#         "eta": extracttime(uphillbus, 7),
#     }
# )
# godownbustable.index = extractcolumn(downhillbus, 0)
# goupbustable.index = extractcolumn(uphillbus, 0)

############build fun table region
############build fun table region
############build fun table region
############build fun table region
############build fun table region
############build fun table region

print(downhillbus)
print(uphillbus)
print(stopid)
print("OK")
print(extracttime(uphillbus, 7))

st.title("SYSS Bus Arrival Estimation")


# st.header("go up")
# uphilltable = st.table(goupbustable)
# st.header("go down")
# downhilltable = st.table(godownbustable)
######################################################################################################
######################################################################################################
######################################################################################################
####################debug region######################################################################
######################################################################################################
######################################################################################################
######################################################################################################

uphillbus = [
    ["10", "Outbound", "彩雲", "大角咀(循環線)", "1", "942E95B4336BDFA7", "46", []],
    ["14D", "Outbound", "油塘", "彩虹", "1", "3BA9C90738A8600D", "20", []],
    ["21", "Inbound", "紅磡站", "彩雲", "1", "942E95B4336BDFA7", "20", []],
    ["213A", "Outbound", "安達", "坪石 / 彩虹站", "1", "3BA9C90738A8600D", "5", []],
    ["213D", "Outbound", "中秀茂坪", "旺角(循環線)", "1", "3BA9C90738A8600D", "10", []],
    ["214", "Outbound", "油塘", "長沙灣(甘泉街)", "1", "58611212645F0AB1", "17", []],
    ["214P", "Outbound", "安秀道", "長沙灣(甘泉街)", "1", "58611212645F0AB1", "6", []],
    ["26", "Outbound", "順天", "尖沙咀東", "1", "3BA9C90738A8600D", "6", []],
    ["26X", "Outbound", "順天", "尖沙咀東", "1", "3BA9C90738A8600D", "6", []],
    ["27", "Outbound", "順天", "旺角(循環線)", "1", "3BA9C90738A8600D", "6", []],
    ["290", "Outbound", "將軍澳(彩明)", "荃灣西站", "1", "58611212645F0AB1", "15", []],
    ["290A", "Outbound", "將軍澳(彩明)", "荃灣西站", "1", "58611212645F0AB1", "25", []],
    ["290B", "Outbound", "將軍澳工業邨", "荃灣西站", "1", "58611212645F0AB1", "20", []],
    ["290X", "Outbound", "康城站", "荃灣西站", "1", "58611212645F0AB1", "20", []],
    ["291P", "Outbound", "香港科技大學(南)", "旺角", "1", "3BA9C90738A8600D", "10", []],
    ["29M", "Outbound", "順利", "新蒲崗(循環線)", "1", "3BA9C90738A8600D", "4", []],
    ["3M", "Outbound", "慈雲山(北)", "彩雲", "1", "942E95B4336BDFA7", "11", []],
    ["42", "Inbound", "順利", "青衣(長康邨)", "1", "3BA9C90738A8600D", "4", []],
    ["606", "Inbound", "小西灣(藍灣半島)", "彩雲(豐盛街)", "1", "942E95B4336BDFA7", "33", []],
    ["606A", "Inbound", "筲箕灣(耀東邨)", "彩雲(豐盛街)", "1", "942E95B4336BDFA7", "21", []],
    ["88", "Outbound", "中秀茂坪", "大圍站", "1", "58611212645F0AB1", "11", []],
    ["91P", "Inbound", "香港科技大學(南)", "坪石 / 彩虹站", "1", "3BA9C90738A8600D", "10", []],
    ["92", "Inbound", "鑽石山站", "西貢", "1", "942E95B4336BDFA7", "5", []],
    ["95", "Outbound", "翠林", "九龍站", "1", "3BA9C90738A8600D", "13", []],
    ["96R", "Outbound", "鑽石山站", "黃石碼頭", "1", "942E95B4336BDFA7", "5", []],
    ["N214", "Outbound", "油塘", "美孚", "1", "58611212645F0AB1", "17", []],
    ["N216", "Outbound", "油塘", "紅磡站", "1", "3BA9C90738A8600D", "20", []],
    ["N290", "Inbound", "康城站", "荃灣西站", "1", "58611212645F0AB1", "35", []],
]
downhillbus = [
    ["14D", "Inbound", "彩虹", "油塘", "1", "9A16E73DC0B9AF6C", "3", []],
    ["214", "Inbound", "長沙灣(甘泉街)", "油塘", "1", "29740CCBBD82FC33", "21", []],
    ["26", "Inbound", "尖沙咀東", "順天", "1", "9A16E73DC0B9AF6C", "22", []],
    ["26M", "Outbound", "彩虹", "觀塘(循環線)", "1", "9A16E73DC0B9AF6C", "4", []],
    ["26X", "Inbound", "尖沙咀東", "順天", "1", "9A16E73DC0B9AF6C", "14", []],
    ["290", "Inbound", "荃灣西站", "將軍澳(彩明)", "1", "29740CCBBD82FC33", "14", []],
    ["290A", "Inbound", "荃灣西站", "將軍澳(彩明)", "1", "29740CCBBD82FC33", "15", []],
    ["290B", "Inbound", "荃灣西站", "將軍澳工業邨", "1", "29740CCBBD82FC33", "14", []],
    ["290X", "Inbound", "荃灣西站", "康城站", "1", "29740CCBBD82FC33", "14", []],
    ["42", "Outbound", "青 衣(長康邨)", "順利", "1", "9A16E73DC0B9AF6C", "41", []],
    ["88", "Inbound", "大圍站", "中秀茂坪", "1", "29740CCBBD82FC33", "12", []],
    ["91", "Inbound", "鑽石山站", "清水灣", "1", "29740CCBBD82FC33", "5", []],
    ["91M", "Inbound", "鑽石山站", "寶林", "1", "29740CCBBD82FC33", "6", []],
    ["91P", "Outbound", "鑽石山站", "香港科技大學(北)", "1", "29740CCBBD82FC33", "3", []],
    ["95", "Inbound", "九龍站", "翠林", "1", "29740CCBBD82FC33", "20", []],
    ["N290", "Outbound", "荃灣西站", "康城站", "1", "29740CCBBD82FC33", "15", []],
]


######################################################################################################
######################################################################################################
######################################################################################################
##############################ENDING PRELOAD REGION###################################################
######################################################################################################
######################################################################################################
async def watch(empty1, empty2, empty3, empty4):
    global currenttime
    while True:
        empty1.header("go up hill")
        for i in range(len(extractcolumn(downhillbus, 0))):
            timenow = datetime.now()
            stringnow = timenow.strftime("%H:%M:%S")
            currenttime = turnintominutes(stringnow)
            godownbustable = pd.DataFrame(
                {
                    "dest": extractcolumn(downhillbus, 3),
                    "eta": extracttime(downhillbus, 7),
                }
            )
            godownbustable["eta"][i] = """updating ready boom anytime"""
            godownbustable.index = extractcolumn(downhillbus, 0)
            empty2.table(godownbustable)
            r = await asyncio.sleep(0.3)

            downhillbus[i][7] = geteta(
                downhillbus[i][0],
                downhillbus[i][1],
                downhillbus[i][4],
                downhillbus[i][6],
            )
            godownbustable = pd.DataFrame(
                {
                    "dest": extractcolumn(downhillbus, 3),
                    "eta": extracttime(downhillbus, 7),
                }
            )
            godownbustable.index = extractcolumn(downhillbus, 0)
            empty2.table(godownbustable)
        print("Currently down")
        # r = await asyncio.sleep(5)
        empty3.header("go down hill")
        for i in range(len(extractcolumn(uphillbus, 0))):
            timenow = datetime.now()
            stringnow = timenow.strftime("%H:%M:%S")
            currenttime = turnintominutes(stringnow)
            goupbustable = pd.DataFrame(
                {
                    "dest": extractcolumn(uphillbus, 3),
                    "eta": extracttime(uphillbus, 7),
                }
            )
            goupbustable["eta"][i] = """updating ready boom anytime"""
            goupbustable.index = extractcolumn(uphillbus, 0)
            empty4.table(goupbustable)
            r = await asyncio.sleep(0.3)

            uphillbus[i][7] = geteta(
                uphillbus[i][0],
                uphillbus[i][1],
                uphillbus[i][4],
                uphillbus[i][6],
            )
            goupbustable = pd.DataFrame(
                {
                    "dest": extractcolumn(uphillbus, 3),
                    "eta": extracttime(uphillbus, 7),
                }
            )
            goupbustable.index = extractcolumn(uphillbus, 0)
            empty4.table(goupbustable)
        print("Currently up")
        # r = await asyncio.sleep(5)


empty1 = st.empty()
empty2 = st.empty()
empty3 = st.empty()
empty4 = st.empty()
asyncio.run(watch(empty1, empty2, empty3, empty4))
