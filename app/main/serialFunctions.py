#from . import serial_rx_tx
import json
import time

import serial
import sys
import _thread
import glob
import logging
import traceback
#import atexit
from . import gCodeGrbl
from . import propFunctions

from flask import current_app as app
#from . import main

def setupSerial():
    sPorts = getSerialPorts()
    return sPorts

def getSerialPorts():
    portlist = GetSerialPorts()
    result ='"{'
    for port in portlist:
        result += "portname:'" + port +"',"
    result = result[:-1]+'}"'
    logging.debug("Portlist:"+result)
    return result

def printSerialPorts():
    logging.debug("Ports=")
    logging.debug(sPorts)

def closeSerialPort():
    try:
        global serialPort
        global serialIsOpen
        serialIsOpen = False
        serialPort.close()
    except:
        pass
    return True

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

    gcodeFlavor = propFunctions.getProperty('default','GCODE_FLAVOUR','G')
    if serialIsOpen:
        closeSerialPort()
    logging.debug('openSerialPort Name: %s and baud rate %s'% (portName, baud))
    serialPort = serial.Serial(portName,baud,timeout=10)
    propFunctions.setProperty('personal','COM_DEFAULT_PORT',portName)
    propFunctions.setProperty('personal','COM_DEFAULT_BAUD', baud)

    
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
    #logging.debug("in Write to Serial")

 

    starttime=time.time()
    logging.debug("serialFunctions.WriteToSerial : Trying to send:<%s> @ %s"%(message,str(starttime)))
    #logging.debug("Trying to send:<%s>"%(message))
    if serialIsOpen:
        try:
            logging.debug("serialFunctions.WriteToSerial : serial is open")
            gotMsg = False
            gotok = False
            l = message.strip() # Strip all EOL characters for consistency
            l = l.encode('utf-8')
            logging.debug("serialFunctions.WriteToSerial : Sending: <" + str(l) + '>' )
            l = l + '\r\n'.encode('utf-8')
            global serialPort
            logging.debug("serialFunctions.WriteToSerial : flushing ")
            serialPort.flushInput()  # Flush old unreceived responses
            logging.debug("serialFunctions.WriteToSerial : writing " + str(l))
            serialPort.write((l)) # Send g-code block to grbl
            #loop until ok
            retVal = ""
            grbl_out_str = ""
            logging.debug("serialFunctions.WriteToSerial : will read Line")
            #logging.debug("will read line")
            grbl_out = serialPort.readline() # Wait for grbl response with carriage return
            logging.debug("serialFunctions.WriteToSerial : grbl_out " + str(grbl_out))
            
            if grbl_out.decode('utf-8').strip() == 'ok':
                logging.debug("serialFunctions.WriteToSerial : got ok back ")
                gotok = True
                grbl_out_str = str("returned OK\r\n")
                #logging.debug(grbl_out_str)
            else:
                logging.debug("serialFunctions.WriteToSerial : got somthing else back - not ok")
                logging.debug("serialFunctions.WriteToSerial : Line read")
                while grbl_out.decode('utf-8').strip() != 'ok' and starttime+timeout > time.time():
                    gotMsg = True
                    grbl_out_str += str( grbl_out.decode('utf-8').strip() + '\n')
                    logging.debug("serialFunctions.WriteToSerial : got " + grbl_out_str)
                    grbl_out = serialPort.readline() # Wait for grbl response with carriage return
                    logging.debug('serialFunctions.WriteToSerial :  nextline: <' + str(grbl_out.decode('utf-8').strip()) +'>')
                    #logging.debug(' nextline: <' + str(grbl_out.decode('utf-8').strip()) +'>')
                if(starttime+timeout < time.time()):
                    logging.debug("serialFunctions.WriteToSerial : Timeout " + str(time.time()))
                    logging.debug("serialFunctions.WriteToSerial : Checking " + str(starttime+timeout) +  " > " + str(time.time()))
                    logging.debug("serialFunctions.WriteToSerial : manual Timeout Exceeded ")
                    return '{"grblState":"TIMEOUT"}'
            if not (gotMsg) and not (gotok):
                grbl_out_str = " "
            logging.debug('serialFunctions.WriteToSerial  !gotMsg && !gotok : ' + grbl_out_str)
            return grbl_out_str
        except Exception as e3:
            logging.debug("serialFunctions.WriteToSerial : Exception ==============================")
            logging.debug(repr(traceback.format_stack()))
            
            logging.debug("serialFunctions.WriteToSerial : Exception ==============================")
            
            logging.debug("serialFunctions.WriteToSerial : " + e3)
            return False
    else:
        logging.debug("serialFunctions.WriteToSerial : Not Sent - Port Is NOT open")
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
        #logging.debug("we are on a mac")
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
    if serialIsOpen:
        global gcodeFlavor
        if gcodeFlavor == 'G':
            result = gCodeGrbl.getStatus()
    else:
        logging.debug("No Status - Port Is NOT open")
        return "No Status - Port Is NOT open"    
    return result

def get3dPos():
 
    logging.debug(" in serialFunctions.get3dPos")
    result = ""
    if serialIsOpen:
        if gcodeFlavor == 'G':
            logging.debug("redirecting to : gCodeGrbl.get3dPos()")
            result = gCodeGrbl.get3dPos()
    else:
        logging.debug("No Status - Port Is NOT open")
        return "No Status - Port Is NOT open"    
    return result

def runCmd(cmd):

    logging.debug(" in serialFunctions.runCmd")
    #return stripPos(WriteToSerial(cmd)) 
    return WriteToSerial(cmd)


def jog(code,isShift,isFine):


    logging.debug("in serialFunctions.jog")

    if serialIsOpen:
        global gcodeFlavor
        if(gcodeFlavor == "G"):
            gCodeGrbl.jog(code, isShift, isFine)
        else:
            logging.debug("Error Gcode Flavour value is not valid")
        return True
    else:
        logging.debug("No Status - Port Is NOT open")
        return False





global serialPort
global sPorts
global serialIsOpen
global gcodeFlavor

serialIsOpen = False

#sPorts = GetSerialPorts()
#logging.debug("printSerialPorts")
#logging.debug(printSerialPorts())
    

