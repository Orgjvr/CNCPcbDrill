#from . import serial_rx_tx
import json
import time

import serial
import sys
import _thread
import glob
import logging
#import atexit

def setupSerial():
    #global serialPort
    #serialPort = serial_rx_tx.SerialPort()
    sPorts = getSerialPorts()
    #printSerialPorts()
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
    if serialIsOpen:
        closeSerialPort()
    logging.debug('openSerialPort Name: %s and baud rate %s'% (portName, baud))
    serialPort = serial.Serial(portName,baud,timeout=10)
    serialIsOpen = True
    logging.debug("Serial Port <%s> opened"%(portName))
    WakeupGrbl()
    return serialIsOpen


def WriteToSerial(message): #This will return the value which was returned from the serial port.
    #TODO: implement a timeout waiting for ok response
    timeout = 10
    starttime=time.time()
    print("Trying to send:<%s>"%(message))
    if serialIsOpen:
        gotMsg = False
        l = message.strip() # Strip all EOL characters for consistency
        print('Sending: ' + l)
        l = l + '\r\n'
        global serialPort
        serialPort.flushInput()  # Flush old unreceived responses
        serialPort.write((l).encode('utf-8')) # Send g-code block to grbl
        #loop until ok
        grbl_out_str = ""
        print("will read Line")
        grbl_out = serialPort.readline() # Wait for grbl response with carriage return
        print("Line read")
        while grbl_out.decode('utf-8').strip() != 'ok' and starttime+timeout > time.time():
            gotMsg = True
            grbl_out_str += str(grbl_out.decode('utf-8').strip())
            grbl_out = serialPort.readline() # Wait for grbl response with carriage return
            print(' nextline: <' + str(grbl_out.decode('utf-8').strip()) +'>')
        if not (gotMsg):
            grbl_out_str = " "
        print(' : ' + grbl_out_str)
        return grbl_out_str
    else:
        print("Not Sent - Port Is NOT open")
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


def WakeupGrbl():
    # Wake up grbl
    global serialPort
    serialPort.write("\r\n\r\n".encode('utf-8'))
    time.sleep(2)   # Wait for grbl to initialize 
    serialPort.flushInput()  # Flush startup text in serial input
    print("wakey wakey")
    WriteToSerial("?")


global serialPort
global sPorts
global serialIsOpen
serialIsOpen = False
sPorts = GetSerialPorts()
print("printSerialPorts")
printSerialPorts()


