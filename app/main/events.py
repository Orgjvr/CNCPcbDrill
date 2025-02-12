from flask import session, Response, g, send_file
from flask_socketio import emit, join_room, leave_room

#import jsonpickle
from .. import socketio
from . import serialFunctions 
from . import cameraFunctions 
from . import coreFunctions
from . import propFunctions
from . import gCodeGrbl
from . import processFile
from .classes import Job
from .views import views_camera
from .views import views_file
import json
import math
import logging



from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# ============ set up logging for events.py ==============
thisLogger = logging.getLogger(__name__)
# To override the default severity of logging
thisLogger.setLevel('DEBUG')

# Use FileHandler() to log to a file
#file_handler = logging.StreamHandler()

# Don't forget to add the file handler
#thisLogger.addHandler(file_handler)
thisLogger.info("I am a log from events.py")


@socketio.on('get3dPos', namespace='/sock')
def get3dPos(message):
    """Get the machine position and send it back to the browser"""
    pos = serialFunctions.get3dPos()
    print("Emitting position from get3dPos in events.py")
    emit('position', pos)
    return pos


@socketio.on('grblTranslateSettings' , namespace='/sock')
def grblTranslateSettings(settings):
    # get settings names
    response = gCodeGrbl.ConfigTranslation(settings)
    return response


@socketio.on('runCmd', namespace='/sock')
def runCmd(cmdText):
    #print('running cmd ' + cmdText)
    try:
        success = serialFunctions.runCmd(cmdText)
    except Exception as e:
        print(e)
    return cmdText, success

@socketio.on('jog', namespace='/sock')
def jog(code, isShift, isFine):
    print("jogging, code =" + code + "shift = " + str(isShift))
    success = serialFunctions.jog(code,isShift,isFine)
    return success


@socketio.on('openSerial', namespace='/sock')
def openSerial(portName,baud):
    """Open serial port to machine returning message to browser"""
    print("Opening serial")
    #portName = portName.replace("~","/")
    success = serialFunctions.openSerialPort(portName,baud)
    return success


@socketio.on('closeSerial', namespace='/sock')
def closeSerial():
    """Close the current serial port to machine returning message to browser"""
    print("Closing serial")
    #portName = portName.replace("~","/")
    success = serialFunctions.closeSerialPort()
    return success

@socketio.on('getCncMoves', namespace='/sock')
def getCncMoves():
    print('Events.getCNCMoves : gettting moves from default.ini')
    success = propFunctions.getDictionary('default', 'CNC_MOVES', '{"coarse":"10","normal":"1","fine":"0.1"}')
    return success

@socketio.on('getUsedPorts', namespace='/sock')
def getUsedPorts():
    print('getting used port & baud')
    success = coreFunctions.getUsedPorts()
    print(success)
    return success

@socketio.on('getSerialPorts', namespace='/sock')
def getSerialPorts():
    """Get a list of serial ports returning message to browser"""
    print("get serial ports")
    success = serialFunctions.GetSerialPorts()
    return success


@socketio.on('getCameras', namespace='/sock')
def getCameras():
    """Get a list of Cameras returning message to browser"""
    print("get cameras event")
    cams = cameraFunctions.get_cameras()
    result = []
    for c in cams:
        result += str(c)
    print("result="+str(result))
    return result


@socketio.on('closeCamera', namespace='/sock')
def closeCamera():
    """Close the last used Camera returning message to browser"""
    result = cameraFunctions.CloseCamera()
    return result


@socketio.on('openCamera', namespace='/sock')
def openCamera(index):
    """Close the last used Camera returning message to browser"""
    print("Opening Cam " + str(index))
    #result = views_camera.activateCam(index)
    result = cameraFunctions.OpenCamera(index)
    propFunctions.setProperty('personal','CAMERA_INDEX',str(index) )
    #print("result="+str(result))
    #return json.dumps(result)
    
    return "Done"#result


@socketio.on('getDollarGMeanings', namespace='/sock')
def getDollarGMeanings(code):
    return gCodeGrbl.getDollarGMeanings(code)

@socketio.on('getDollarHashMeanings', namespace='/sock')
def getDollarHashMeanings(code):
    return gCodeGrbl.getDollarHashMeanings(code)
    
@socketio.on('emergencyStop', namespace = '/sock')
def emergencyStop(message):
    success = serialFunctions.emergencyStop()
    return success
    


@socketio.on('isSerialPortOpen', namespace = '/sock')
def isSerialPortOpen():
    success = serialFunctions.isSerialPortOpen()
    return success


@socketio.on('getCurrentPortAndBaud', namespace = '/sock')
def getCurrentPortAndBaud():
    success = serialFunctions.getCurrentPortAndBaud()
    return success


@socketio.on('getCurrentCamera', namespace = '/sock')
def getCurrentCamera():
    success = cameraFunctions.getCurrentCamera()
    return success


@socketio.on("generateGcode", namespace='/sock')
def generateGcode():
    return processFile.generateGcode()
    #return "This is the returned GCode"

@socketio.on('runLine', namespace='/sock')
def runLine(jsontext):
    cmd = json.loads(jsontext)
    print("received " + jsontext)
    print(cmd["l"])
    serialResponse = serialFunctions.WriteToSerial(cmd["l"])

    retVal = '{"res":"%s", "n":%d}'% (serialResponse, cmd["n"]) 

    emit('liner', retVal)
    return retVal
   
'''
    receive a json string of the gcode to be sent 

@socketio.on("streamGcode", namespace='/sock')
def streamGcode(jsonLines):
    print( "in events.streamGcode")
    serialFunctions.streamLines(jsonLines)
    return
'''



@socketio.on('calcProcessRotation', namespace = '/sock')
#def runProcess(h1X, h1Y, h2X, h2Y, jobContext):
def runProcess(sh1X, sh1Y, sh2X, sh2Y, ssZ, sdD):

    h1X = float(sh1X)
    h1Y = float(sh1Y)
    h2X = float(sh2X)
    h2Y = float(sh2Y)
    sZ = float(ssZ)
    dD = float(sdD)

    
    JobObject = views_file.job
    JobObject.CNC_SAFE_HEIGHT = sZ
    JobObject.CNC_DRILL_DEPTH = dD


    JobObject = views_file.job
    thisLogger.debug("Calculating CNC DATA -------------------------")
    thisLogger.debug("calculating with H1: (%3.3f, %3.3f)"% (h1X, h1Y))
    thisLogger.debug("calculating with H2: (%3.3f, %3.3f)"% (h2X, h2Y))
    
    JobObject.CNChole1 = h1X, h1Y
    JobObject.CNChole2 = h2X, h2Y

    CNCRadAngle = JobObject.calculatePCBRotationInRads()
    CNCAngle = math.degrees(CNCRadAngle)
    logging.debug(" sanity check ------------------------------- calculate distance between holes on CNC")
    CNCDistance =  math.sqrt( (h1X-h2X)**2 + (h1Y-h2Y)**2 )
    thisLogger.debug(" CNC Distance = %3.3f"% (CNCDistance))
    thisLogger.debug("CNCRadAngle = %3.3f radians, and %3.3f degrees."% (CNCRadAngle, CNCAngle) )
    thisLogger.debug("==========================================================")



    # get distance & angles from Drill file ( after zero & flip )
    PCBRadAngle = JobObject.PCBRadAngle
    PCBAngle = math.degrees(PCBRadAngle)
    thisLogger.debug("PCBRadAngle = %3.3f radians, and %3.3f degrees."% (PCBRadAngle, PCBAngle) )

    RotRadAngle =   CNCRadAngle - PCBRadAngle
    RotAngle = math.degrees(RotRadAngle)
    

    thisLogger.debug("Rotation = %3.3f radians, and %3.3f degrees."% (RotRadAngle, RotAngle) )

    thisLogger.debug("hole 1 X: %3.3f  Y: %3.3f  "% (JobObject.h1.zeroedAndFlippedPoint[0], JobObject.h1.zeroedAndFlippedPoint[1]))
    thisLogger.debug("hole 2 X: %3.3f  Y: %3.3f  "% (JobObject.h2.zeroedAndFlippedPoint[0], JobObject.h2.zeroedAndFlippedPoint[1]))

    # scale 
    CNCScale = JobObject.CNCScale


    
    thisLogger.debug("==========================================================")

    return '{"RotRadAngle":"%3.3f", "RotAngle":"%3.3f", "CNCDistance":"%3.2f", "GCodeRotation":"%3.3f", "CNCScale":"%3.3f"}'% (CNCRadAngle, CNCAngle, CNCDistance, RotAngle, CNCScale)



