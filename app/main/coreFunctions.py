import json
#import time

#import serial
import sys
import _thread
import glob
import logging

#from . import gCodeGrbl
from . import propFunctions

from flask import current_app as app


def getCncMoves():
    #print('getting Moves from coreFunctions')
    retVal = propFunctions.getProperty('default', 'CNC_MOVES', '{"coarse":"10","normal":"1","fine":"0.1"}')
    #print("returned = " + retVal)
    retVal = dict(json.loads(retVal))
    #print('this is the moves')
    print(retVal)
    #print("this shhouold work")
    print(retVal['coarse'])
    #print("before this ")
    return retVal 


def getUsedPorts():
    #print('getting Used Port from default.py')
    port = propFunctions.getProperty('personal', 'COM_DEFAULT_PORT', '')
    baud = propFunctions.getProperty('personal', 'COM_DEFAULT_BAUD', '115200')
    retVal = '{"port":"' + str(port) + '", "baud":"' + str(baud) + '"}'
    print('this is the used Port')
    print(retVal)
    return retVal 
