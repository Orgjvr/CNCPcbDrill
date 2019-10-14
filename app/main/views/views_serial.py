from flask import session, redirect, url_for, render_template, request, Response
from .. import main
#from .forms import LoginForm
import json
import logging
from flask import current_app as app
#from .. import serial_rx_tx
from .. import serialFunctions

import time


@main.route('/getSerialDefault')
def getSerialDefault(): 
    logging.basicConfig(level=logging.DEBUG)

    logging.info("hello world")
    global baudRate
    baudRate = app.config['SERIALPORTBAUDRATE']
    logging.info("baudRate = " + str(baudRate))
    
    return Response("Baudrate = " + str(baudRate))

@main.route('/getSerialPorts')
def getSerialPorts():
    global sPorts
    sPorts = serialFunctions.getSerialPorts()
    return Response(json.dumps(sPorts))


@main.route('/getStatus')
def getStatus():
    status = serialFunctions.getStatus()
    return Response(str(status))


@main.route('/get3dPos')
def get3dPos():
    pos = serialFunctions.get3dPos()
    return Response(str(pos))

@main.route('/moveLeft/<dist>')
def moveLeft(dist):
    return Response(stripPos(serialFunctions.WriteToSerial("$J=G91 X-%3.3f F500"% (float(dist)))))

@main.route('/moveRight/<dist>')
def moveRight(dist):
    return Response(stripPos(serialFunctions.WriteToSerial("$J=G91 X%3.3f F500"% (float(dist)))))

def stripPos(pos):
    if pos[0] == "<":
        pos=pos[1:]
    if pos[-1] == ">":
        pos=pos[:-1]
    return str(pos)

@main.route('/moveXY10')
def moveXY10():
    pos = serialFunctions.WriteToSerial("$J=G91 X10 Y10 F300")
    #pos = serialFunctions.WriteToSerial("?")
    if pos[0] == "<":
        pos=pos[1:]
    if pos[-1] == ">":
        pos=pos[:-1]
    return Response(str(pos))


@main.route('/open_port/<portName>/<baud>')
def open_port(portName,baud):
    #global serialPort
    #serialPort = serial_rx_tx.SerialPort()
    portName = portName.replace("~","/")
    serialFunctions.openSerialPort(portName,baud)
    #print('in Open_Port  Name: %s and baud rate %s'% (portName, baud))
    #serialPort.Open(portName,baud)
    #print("Port opened")
    #serialPort.RegisterReceiveCallback(serialFunctions.OnReceiveSerialData)
    #print("Callback registered")
    #time.sleep(10)
    #serialPort.Send("?")
    #serialPort.Send("$J=G91 X10 Y10 F300")
    #serialPort.Send("?")

    #get_coms()
    return "nothing"


@main.route('/close_port')
def close_port():
    serialFunctions.closeSerialPort()
    return "nothing"



@main.route('/get_coms')
def get_coms():
    #global serialPort
    #serialPort = serial_rx_tx.SerialPort()
    #serialFunctions.serialPort.Send("?")
    #serialFunctions.serialPort.Send("$J=G91 X10 Y10 F300")
    serialFunctions.WriteToSerial("$")
    serialFunctions.WriteToSerial("?")

    return "nothing"

def OnReceiveSerialData(message):
    str_message = message.decode("utf-8")
    print("fokop:%s"%(str_message))