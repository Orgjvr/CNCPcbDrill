from flask import session, redirect, url_for, render_template, request, Response
from .. import main
#from .forms import LoginForm
import cv2
from .. import cameraFunctions
#from ..camera import VideoCamera
from ..camera import Camera
import json
import logging
from flask import current_app as app

#TODO: add send of json camera list from GetCameras
#TODO: add dynamic route to activate camera /c/2 

@main.route('/c/<cam_num>')
def activateCam(cam_num):
    print("First close Cam ")
    closeLastCam()
    global showCam
    showCam=True
    global camIndex
    camIndex = int(cam_num)
    print("Activating Cam: "+cam_num)
    return Response(gen(VideoCamera(camIndex)), mimetype='multipart/x-mixed-replace; boundary=frame')
    #return "Camera %d activated"% (camIndex)


@main.route('/cs/<cam_num>')
def stopCam(cam_num):
    global showCam
    showCam=False
    print("Closing cam")
    global camIndex
    camIndex = int(cam_num)
    VideoCamera(camIndex).__del__()
    return "Cam Closed"


@main.route('/close_last_cam')
def closeLastCam():
    global showCam
    showCam=False
    global camIndex
    print("Closing cam")
    #camIndex = int(cam_num)
    VideoCamera(camIndex).__del__
    return "Cam Closed"


@main.route('/get_cameras')
def get_cameras():
    print("in view for get_cameras")
    closeLastCam()
    cams = cameraFunctions.get_cameras()
    return Response(json.dumps(cams))


def gen(camera):
    print("in camera gen")
    #camera.__del__() #  .release()
    #camera.__init__(camera)
    while showCam:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#@main.route('/video_feed')
#def video_feed():
#    global camIndex
    #camIndex = int(app.config.get('CAMERA_INDEX'))
    



@main.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(cameraFunctions.gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/vf2/<cam_num>')
def vf2(cam_num):
    """Video streaming route. Put this in the src attribute of an img tag."""
    Camera.set_video_source(int(cam_num))
    return Response(cameraFunctions.gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@main.route('/vf2s')
def vf2s():
    """Stop the Video streaming feed."""
    Camera.stop()
    return "Stopped"

global showCam
showCam=True
global camIndex
camIndex = 0
#camIndex = int(app.config.get('CAMERA_INDEX'))