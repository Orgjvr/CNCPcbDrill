from flask import session, Response, g, send_file
from flask_socketio import emit, join_room, leave_room
from PIL import Image
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
import logging
import json
import base64
import io
import numpy as np
import cv2


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

@socketio.on('generateCNCPreview', namespace = '/sock')
def generateCNCPreview():
    # generate image and return

    
    print("creating CNC Preview .........")
    cncFig = Figure()
    canvas = FigureCanvas(cncFig)
    axis = cncFig.add_subplot(1, 1, 1)
    #fig = plt.figure(figsize=(10,8))
    job = views_file.job
    # plot hole 1 
    axis.plot(10, 10, color="red", markersize=10, marker='o')
    #axis.plot(job.CNChole1[0], job.CNChole1[1], color="red", markersize=10, marker='o')
    # plot hole 2 
    axis.plot(100, 100, color="red", markersize=10, marker='o')
    #axis.plot(job.CNChole2[0], job.CNChole2[1], color="red", markersize=10, marker='o')
    
    axis.plot( (10,10),(100,100), linewidth=2, color='red')

    #axis.text(job.CNChole1[0],job.CNChole1[1], ' Hole 1',size=15) 
    #axis.text(job.CNChole2[0],job.CNChole2[1], ' Hole 2',size=15)
    
    img = get_img_from_fig(cncFig)

    #print(img)
   
    canvas.draw()


    # convert numpy array to PIL Image
    #img2 = Image.fromarray(img.astype('uint8'))

    # create file-object in memory
    #file_object = io.BytesIO()

    # write PNG in file-object
    #img2.save(file_object, 'PNG')

    # move to beginning of file so `send_file()` it will read from start    
    #file_object.seek(0)


    data = {}
    bob = base64.b64encode(img.astype('uint8'))
    print(bob[:10])

    data['img'] = bob
    
    #data['img'] = base64.standard_b64encode(img)

    #print(data['img'][:100])

    return data

    
    #fo = base64.b64encode(file_object)


    #return send_file(file_object, mimetype='image/PNG')





    '''
    print(json.dumps(data))
    Then, use base64.b64decode(data['img']) to convert back.


    return cncFig
    '''

def get_img_from_fig(fig, dpi=180):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return img


@socketio.on('calcProcessRotation', namespace = '/sock')
#def runProcess(h1X, h1Y, h2X, h2Y, jobContext):
def runProcess(sh1X, sh1Y, sh2X, sh2Y):

    h1X = float(sh1X)
    h1Y = float(sh1Y)
    h2X = float(sh2X)
    h2Y = float(sh2Y)


    
    JobObject = views_file.job

    JobObject = views_file.job
    thisLogger.debug("Calculating CNC DATA -------------------------")
    thisLogger.debug("calculating with H1: (%3.3f, %3.3f)"% (h1X, h1Y))
    thisLogger.debug("calculating with H2: (%3.3f, %3.3f)"% (h2X, h2Y))
    
    CNCRadAngle = JobObject.setCNCholes( h1X, h1Y, h2X , h2Y)
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
    
    thisLogger.debug("==========================================================")

    return '{"RotRadAngle":"%3.3f", "RotAngle":"%3.3f", "CNCDistance":"%3.2f", "GCodeRotation":"%3.3f"}'% (CNCRadAngle, CNCAngle, CNCDistance, RotAngle)



