#import json
#import time

#import serial
import sys
import _thread
import glob
import logging

#from . import gCodeGrbl

from flask import current_app as app


def getCncMoves():
    print('getting Moves from coreFunctions')
    retVal = dict(app.config.get('CNC_MOVES'))
    print('this is the moves')
    print(retVal)
    print(retVal['coarse'])
    return retVal 
