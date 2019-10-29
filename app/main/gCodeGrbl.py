""" This contains the GRBL specific command translations
"""

import logging
import time
from . import serialFunctions 
from . import propFunctions
import json
from flask import current_app as app

def Wakeup():
    # Wake up grbl
    serialFunctions.WriteToSerial('\r\n\r\n',0)
    time.sleep(2)   # Wait for grbl to initialize 
    serialFunctions.flushInput()
    

def getStatus():
    logging.debug("getting status, sending '?'")
    status = serialFunctions.WriteToSerial("?").strip()
    logging.debug("got back from WriteToSerial : "+ str(status))
    
    if status[0] == "<":
        status=status[1:]
    if status[-1] == ">":
        status=status[:-1]
    statuses = str("state:"+status).split('|')
    result = "{"
    for state in statuses:
        logging.debug("State inside [] ==> ["+state+"]")
        thisSeg = '"'+state.split(':')[0]+'":"'+state.split(':')[1]+'",'
        result += thisSeg
    return result[:-1]+"}"

def get3dPos():
    status = getStatus()
    logging.debug("get 3dPos Status <"+status+">")
    jstatus = json.loads(status)
    logging.debug("MPos=<"+jstatus['MPos']+">")
    pos =  jstatus['MPos'].split(",")
    gStatus = '"grblState":"' + jstatus['state'] + '", '
    xyzpos = '"X":'+pos[0]+","+'"Y":'+pos[1]+","+'"Z":'+pos[2]
    logging.debug("xyz=<"+xyzpos+">")
    pos = "{" + gStatus + xyzpos+"}"
    return pos
    

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



        