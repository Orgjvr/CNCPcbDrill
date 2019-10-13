#from . import serial_rx_tx
import json
import time

import serial
import sys
import _thread
import glob
import logging
#import atexit
from . import gCodeGrbl
from flask import current_app as app
#from . import main

def setupSerial():
    sPorts = getSerialPorts()
    return sPorts

def getSerialPorts():
    GetSerialPorts()
    return sPorts

def printSerialPorts():
    print("Ports=")
    print(sPorts)

def closeSerialPort():
    try:
        global serialPort
        global serialIsOpen
        serialIsOpen = False
        serialPort.close()
    except:
        pass

def openSerialPort(portName,baud):
    """ Open a serial port at a specified baud rate.
        It will first close it if it was opened previously.

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            True or False on whether it could open
    """
    global serialPort
    global serialIsOpen
    global gcodeFlavor
    gcodeFlavor = app.config.get('GCODE_FLAVOUR')
    if serialIsOpen:
        closeSerialPort()
    logging.debug('openSerialPort Name: %s and baud rate %s'% (portName, baud))
    serialPort = serial.Serial(portName,baud,timeout=10)
    serialIsOpen = True
    logging.debug("Serial Port <%s> opened"%(portName))
    if gcodeFlavor == 'G':
        gCodeGrbl.Wakeup()
    return serialIsOpen

def flushInput():
    global serialPort
    if serialIsOpen:
        serialPort.flushInput()  # Flush startup text in serial input
        return "Serial Input flushed"    
    else:
        logging.debug("Not flushed - Port Is NOT open")
        return "Not flushed - Port Is NOT open"    


def WriteToSerial(message, timeout=10): #This will return the value which was returned from the serial port.
    #TODO: implement a timeout waiting for ok response
    #timeout = 10 #Max time in seconds to wait for result on serial port
    starttime=time.time()
    logging.debug("Trying to send:<%s>"%(message))
    if serialIsOpen:
        gotMsg = False
        l = message.strip() # Strip all EOL characters for consistency
        l = l.encode('utf-8')
        #print('Sending: <' + str(l) + '>' )
        l = l + '\r\n'.encode('utf-8')
        global serialPort
        serialPort.flushInput()  # Flush old unreceived responses
        serialPort.write((l)) # Send g-code block to grbl
        #loop until ok
        grbl_out_str = ""
        logging.debug("will read Line")
        grbl_out = serialPort.readline() # Wait for grbl response with carriage return
        logging.debug("Line read")
        while grbl_out.decode('utf-8').strip() != 'ok' and starttime+timeout > time.time():
            gotMsg = True
            grbl_out_str += str(grbl_out.decode('utf-8').strip())
            grbl_out = serialPort.readline() # Wait for grbl response with carriage return
            logging.debug(' nextline: <' + str(grbl_out.decode('utf-8').strip()) +'>')
        if not (gotMsg):
            grbl_out_str = " "
        logging.debug(' : ' + grbl_out_str)
        return grbl_out_str
    else:
        logging.debug("Not Sent - Port Is NOT open")
        return "Not Sent - Port Is NOT open"    



def GetSerialPorts():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        #print("we are on a mac")
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    #return ports
    
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    #global sPorts
    #sPorts = result
    return result

def getStatus():
    result = ""
    if gcodeFlavor == 'G':
        result = gCodeGrbl.getStatus()
    return result



global serialPort
global sPorts
global serialIsOpen
global gcodeFlavor

serialIsOpen = False
sPorts = GetSerialPorts()
logging.debug("printSerialPorts")
logging.debug(printSerialPorts())


