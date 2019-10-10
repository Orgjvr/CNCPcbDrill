from flask import session, redirect, url_for, render_template, request, Response
from .. import main
#from .forms import LoginForm
import json
import logging
from flask import current_app as app


#TODO: add send of json camera list from GetCameras
#TODO: add dynamic route to activate camera /c/2 

@main.route('/getSerialDefault')
def getSerialDefault(): 
    logging.basicConfig(level=logging.DEBUG)

    logging.info("hello world")
    global baudRate
    baudRate = app.config['SERIALPORTBAUDRATE']
    logging.info("baudRate = " + str(baudRate))
    
    return Response("Baudrate = " + str(baudRate))

@main.route('/getSerialPorts')
def getSerialPorst():
    global sPorts
    sPorts = serialPort.GetSerialPorts()
    return Response(json.dumps(sPorts))

    #return "Camera %d activated"% (camIndex)

