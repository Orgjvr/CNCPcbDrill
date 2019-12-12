""" This contains the GRBL specific command translations
"""

import logging
import time
from . import serialFunctions 
from . import propFunctions
import json
import traceback
from flask import current_app as app
from .views import views_file

def Wakeup():
    # Wake up grbl
    serialFunctions.WriteToSerial('\r\n\r\n',0)
    time.sleep(2)   # Wait for grbl to initialize 
    serialFunctions.flushInput()
    
'''
gets status from GRBL and returns to get3dPos in a json format  
''' 

def getStatus():
    print("getting status, sending via serialFunctions.WriteToSerial('?') ")
    status = serialFunctions.WriteToSerial("?").strip()
    if(status != None):
        print("got back from WriteToSerial : "+ str(status))
        if(str(status).find("TIMEOUT") != -1):
            return status
        if status[0] == "<":
            status=status[1:]
        if status[-1] == ">":
            status=status[:-1]
        statuses = str("state:"+status).split('|')
        result = "{"
        for state in statuses:
            print("State inside [] ==> ["+state+"]")
            thisSeg = '"'+state.split(':')[0]+'":"'+state.split(':')[1]+'",'
            result += thisSeg
        return result[:-1]+"}"
    
'''
Added a check for the streaming state - if streaming, return an additional status which is the list of completed lines & the current line 

{"streamStatus":{ "completed":[1,2,3,4,5,6,7], "currentLine":8}}

'''
def get3dPos():
    print("gCodeGrbl.get3dPos : running getStatus()")
    status = getStatus()
    print("gCodeGrbl.get3dPos : getStatus returned <"+status+">")
    try:
        jstatus = json.loads(status)
        print("gCodeGrbl.get3dPos : MPos=<"+jstatus['MPos']+">")
        pos =  jstatus['MPos'].split(",")
        gStatus = '"grblState":"' + jstatus['state'] + '", '
        xyzpos = '"X":'+pos[0]+","+'"Y":'+pos[1]+","+'"Z":'+pos[2]
        print("gCodeGrbl.get3dPos : xyz=<"+xyzpos+">")
        pos = "{" + gStatus + xyzpos+"}"
        return pos
    except Exception as e4:
        print("gCodeGrbl.get3dPos Exception ..................")
        print(e4) 
        return '{"grblState":"get3dPos EXCEPTION "}'

'''
n serialFunctions.get3dPos
redirecting to : gCodeGrbl.get3dPos()
writing b'?\r\n'
manual Timeout Exceeded 
Exception in gCodeGrbl.get3dPos
Expecting ',' delimiter: line 1 column 13 (char 12)
Emitting position
'''


def jog(code, isShift, isFine):
    moves = propFunctions.getDictionary('default', 'CNC_MOVES', '{"coarse":"10","normal":"1","fine":"0.1"}')

    #moves = dict( app.config.get('CNC_MOVES'))
    coarse = moves["coarse"]
    normal = moves["normal"]
    fine = moves["fine"]

    if (isFine and isShift):
        val = fine   # fine
    if( isFine and not isShift) or (not isFine and isShift):
        val = normal  # normal
    if( not isFine and not isShift):
        val = coarse   #coarse


    if code == 'ArrowLeft':
            return stripPos(serialFunctions.WriteToSerial("$J=G91 X-%2.2f F500"% (val)))
    if code == 'ArrowRight':
            return stripPos(serialFunctions.WriteToSerial("$J=G91 X%2.2f F500"% (val)))
    if code == 'ArrowUp':
            return stripPos(serialFunctions.WriteToSerial("$J=G91 Y%2.2f F500"% (val)))
    if code == 'ArrowDown':
            return stripPos(serialFunctions.WriteToSerial("$J=G91 Y-%2.2f F500"% (val)))
    if code == 'PageUp':
            return stripPos(serialFunctions.WriteToSerial("$J=G91 Z-%2.2f F500"% (val)))
    if code == 'PageDown':
            return stripPos(serialFunctions.WriteToSerial("$J=G91 Z%2.2f F500"% (val)))



def stripPos(pos):
    if pos[0] == "<":
        pos=pos[1:]
    if pos[-1] == ">":
        pos=pos[:-1]
    return str(pos)


def ConfigTranslation(data):
    retVal = ""
    titles = propFunctions.getDictionary('default','GRBL_SETTINGS','{"error":"Error getting Settings"}')
    #print(titles)
    lines = data.splitlines(False)
    for line in lines:
        print(line)
        tmp = line[1:]   # remove $
        #print(" after removing $ ==> " + tmp)
        parts = tmp.split("=")
        prefix = ("   " + parts[0])[-3:]
        #print("prefix = [" + prefix + "]")
        mid = (parts[1] + "            ")[0:10]
        lne= "\n[" + prefix + "] " + mid + " " + titles[parts[0]] 
        #print(lne)
        retVal += lne
        #print
    return retVal

def getDollarGMeanings(code):

    if(code[0] == "T"):
        return "Selected Tool"
    if(code[0] == "F"):
        return "Current Feed Rate"
    if(code[0] == "S"):
        return "Current Spindle Speed"

    switcher = {
        "G0": "Motion Mode",
        "G1": "Motion Mode",
        "G2": "Motion Mode",
        "G3": "Motion Mode",
        "G38.2": "Motion Mode",
        "G38.3": "Motion Mode",
        "G38.4": "Motion Mode",
        "G80": "Motion Mode",
        "G54": "Coordinate System Selected",
        "G55": "Coordinate System Selected",
        "G56": "Coordinate System Selected",
        "G57": "Coordinate System Selected",
        "G58": "Coordinate System Selected",
        "G59": "Coordinate System Selected",
        "G17": "XY Plane",
        "G18": "XZ Plane",
        "G19": "YZ Plane",
        "G20": "Units : Inches",
        "G21": "Units : Millimeters",
        "G90": "Distance Mode : Absolute",
        "G91": "Distance Mode : Relative",
        "G91.1": "Arc Mode : IJK ",
        "G93": "Feed Rate Mode",
        "G94": "Feed Rate Mode",
        "M0": "Program Mode : Pause",
        "M1": "Program Mode : Pause if Switch",
        "M2": "Program Mode : End Program",
        "M30": "Program Mode : Exchange Shuttle, End Program",
        "M3": "Spindle Control : Clockwise Rotation, [S] Speed",
        "M4": "Spindle Control : Anti-Clockwise Rotation, [S] Speed",
        "M5": "Spindle Control : Stop Spindle",
        "M7": "Coolant Control : Mist On",
        "M8": "Coolant Control : Flood On",
        "M9": "Coolant Control : Off",
    }
    return switcher.get(code, "Invalid Code")


def getDollarHashMeanings(code):

    switcher = {

        "G54": "Coordinate System Selected",
        "G55": "Coordinate System Selected",
        "G56": "Coordinate System Selected",
        "G57": "Coordinate System Selected",
        "G58": "Coordinate System Selected",
        "G59": "Coordinate System Selected",
        "G28": "Pre - Defined Positions",
        "G30": "Pre - Defined Positions",
        "G92": "Coordinate Offset",
        "TLO": "Tool Length Offsets",
        "PRB": "Probing"
    }
    return switcher.get(code, " ?? Unknown Value ?? ")

  