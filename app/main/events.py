from flask import session, Response, g
from flask_socketio import emit, join_room, leave_room
#import jsonpickle
from .. import socketio
from . import serialFunctions 
from . import cameraFunctions 
from . import coreFunctions
from . import propFunctions
from . import gCodeGrbl
from .classes import Job
from .views import views_camera
from .views import views_file
import json
import math

@socketio.on('get3dPos', namespace='/sock')
def get3dPos(message):
    """Get the machine position and send it back to the browser"""
    pos = serialFunctions.get3dPos()
    print("Emitting position")
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
#def runProcess(h1X, h1Y, h2X, h2Y, jobContext):
def emergencyStop(message):
    success = serialFunctions.emergencyStop()
    return success

@socketio.on('runProcess', namespace = '/sock')
#def runProcess(h1X, h1Y, h2X, h2Y, jobContext):
def runProcess(h1X, h1Y, h2X, h2Y):
    
    JobObject = views_file.job

    CNCRadAngle = JobObject.setCNCholes( float(h1X), float(h1Y), float(h2X) , float(h2Y))
    CNCAngle = math.degrees(CNCRadAngle)
    print("CNCRadAngle = %3.3f radians, and %3.3f degrees."% (CNCRadAngle, CNCAngle) )

    PCBRadAngle = JobObject.PCBRadAngle
    PCBAngle = math.degrees(PCBRadAngle)
    print("PCBRadAngle = %3.3f radians, and %3.3f degrees."% (PCBRadAngle, PCBAngle) )

    RotRadAngle = PCBRadAngle - CNCRadAngle
    RotAngle = math.degrees(RotRadAngle)

    print("Rotation = %3.3f radians, and %3.3f degrees."% (RotRadAngle, RotAngle) )

    return ("Result Rotation Angle = %3.3f radians, and %3.3f degrees."% (RotRadAngle, RotAngle) )



