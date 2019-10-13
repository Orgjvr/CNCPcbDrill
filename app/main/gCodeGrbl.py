""" This contains the GRBL specific command translations
"""

import logging
import time
from . import serialFunctions 

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
    statuses = status.split('|')
    for state in statuses:
        print("State <"+state+">")
    return status

