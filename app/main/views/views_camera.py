from flask import session, redirect, url_for, render_template, request, Response
from .. import main
#from .forms import LoginForm
import cv2
from .. import cameraFunctions
from ..camera import VideoCamera
import json
import logging
from flask import current_app as app

#TODO: add send of json camera list from GetCameras
#TODO: add dynamic route to activate camera /c/2 

@main.route('/c/<cam_num>')
def activateCam(cam_num):
    global showCam
    showCam=True
    print("Activating Cam: "+cam_num)
    global camIndex
    camIndex = int(cam_num)
    return Response(gen(VideoCamera(camIndex)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

    #return "Camera %d activated"% (camIndex)


@main.route('/cs/<cam_num>')
def stopCam(cam_num):
    global showCam
    showCam=False
    print("Closing cam")
    global camIndex
    camIndex = int(cam_num)
    VideoCamera(camIndex).__del__
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
    camera.__del__ #  .release()
    while showCam:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@main.route('/video_feed')
def video_feed():
    global camIndex
    camIndex = int(app.config.get('CAMERA_INDEX'))
    #print('getting video feed')
    #if oldIndex != camIndex:
    #    mustCaptureVideo = False
    #    oldIndex=camIndex
    #return Response(gen(VideoCamera(0)),
    return Response(gen(VideoCamera(camIndex)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

global showCam
showCam=True