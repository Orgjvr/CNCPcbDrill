""" This contains the GRBL specific command translations
"""

import logging
import time
from . import serialFunctions 
import json

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
    xyzpos = '"X":'+pos[0]+","+'"Y":'+pos[1]+","+'"Z":'+pos[2]
    print("xyz=<"+xyzpos+">")
    pos = "{"+xyzpos+"}"
    return pos
    