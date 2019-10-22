""" This contains the GRBL specific command translations
"""

import logging
import time
from . import serialFunctions 
import json
from flask import current_app as app

def Wakeup():
    # Wake up grbl
    serialFunctions.WriteToSerial('\r\n\r\n',0)
    time.sleep(2)   # Wait for grbl to initialize 
    serialFunctions.flushInput()
    

def getStatus():
    status = serialFunctions.WriteToSerial("?")
    if status[0] == "<":
        status=status[1:]
    if status[-1] == ">":
        status=status[:-1]
    statuses = str("state:"+status).split('|')
    result = "{"
    for state in statuses:
        print("State <"+state+">")
        result += '"'+state.split(':')[0]+'":"'+state.split(':')[1]+'",'
    return result[:-1]+"}"

def get3dPos():
    status = getStatus()
    print("Status <"+status+">")
    jstatus = json.loads(status)
    print("MPos=<"+jstatus['MPos']+">")
    pos =  jstatus['MPos'].split(",")
    gStatus = '"grblState":"' + jstatus['state'] + '", '
    xyzpos = '"X":'+pos[0]+","+'"Y":'+pos[1]+","+'"Z":'+pos[2]
    print("xyz=<"+xyzpos+">")
    pos = "{" + gStatus + xyzpos+"}"
    return pos
    

def jog(code, isShift, isFine):
    moves = dict(app.config.get('CNC_MOVES'))
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

def stripPos(pos):
    if pos[0] == "<":
        pos=pos[1:]
    if pos[-1] == ">":
        pos=pos[:-1]
    return str(pos)
