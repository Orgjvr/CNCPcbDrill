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




@main.route('/get_cameras')
def get_cameras():
    print("in view for get_cameras")
    closeLastCam()
    cams = cameraFunctions.get_cameras()
    return Response(json.dumps(cams))


@main.route('/close_last_cam')
def closeLastCam():
    global showCam
    showCam=False
    global camIndex
    print("Closing cam")
    #camIndex = int(cam_num)
    VideoCamera(camIndex).__del__
    return "Cam Closed"


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