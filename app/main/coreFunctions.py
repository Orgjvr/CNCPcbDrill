import json
#import time

#import serial
import sys
import _thread
import glob
import logging

#from . import gCodeGrbl
from . import propFunctions
from .classes import Job

from flask import current_app as app

# job holder 
global jj 
jj = Job.Job()

def setjj(job):
    jj = job

def getjj():
    return jj

def getUsedPorts():
    #print('getting Used Port from default.py')
    port = propFunctions.getProperty('personal', 'COM_DEFAULT_PORT', '')
    baud = propFunctions.getProperty('personal', 'COM_DEFAULT_BAUD', '115200')
    retVal = '{"port":"' + str(port) + '", "baud":"' + str(baud) + '"}'
    print('this is the used Port')
    print(retVal)
    return retVal 
