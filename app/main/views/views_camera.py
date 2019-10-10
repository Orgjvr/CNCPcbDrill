from flask import session, redirect, url_for, render_template, request, Response
from .. import main
#from .forms import LoginForm
import cv2
from ..camera import VideoCamera
import json
import logging
from flask import current_app as app

#TODO: add send of json camera list from GetCameras
#TODO: add dynamic route to activate camera /c/2 

@main.route('/c/<cam_num>')
def activateCam(cam_num):
    
    global camIndex
    camIndex = int(cam_num)
    return Response(gen(VideoCamera(camIndex)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

    #return "Camera %d activated"% (camIndex)

@main.route('/get_cameras')
def get_cameras():
    logging.basicConfig(level=logging.DEBUG)
    #index = 2
    arr = []
    for index in range(5):
        try:
            logging.debug("Try to read camera no <" + str(index) + ">")
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                logging.debug("Cannot read camera no <" + str(index) + ">")
                #break
            else:
                logging.info("Adding camera no <" + str(index) + ">")
                arr.append(index)
                index += 1
                cap.release()
        except:
            logging.error("Cannot close")
            #break

    global sCameras
    sCameras = arr
    logging.debug("Returning " + json.dumps(arr))
    return Response(json.dumps(arr))


def gen(camera):
    camera.__del__ #  .release()
    
    while True:
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
