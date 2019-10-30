from flask import session, redirect, url_for, render_template, request, Response
from .. import main
#from .forms import LoginForm
import cv2
#from .camera import VideoCamera
import json
import logging
from flask import current_app as app
from .camera import Camera


def get_cameras():
    print("cams funcs get cam")
    #index = 2
    arr = []
    for index in range(5):
        print("Cam="+str(index))
        try:
            logging.debug("Try to read camera no <" + str(index) + ">")
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                #cap = cv2.VideoCapture(index)
                logging.debug("Cannot read camera no <" + str(index) + ">")
                #break
            else:
                logging.info("Adding camera no <" + str(index) + ">")
                arr.append(index)
                #index += 1
                cap.release()
        except:
            logging.error("Cannot close")
            #break

    global sCameras
    sCameras = arr
    logging.debug("Returning " + json.dumps(arr))
    print("Returning cams " + json.dumps(arr))
    return arr
    #return json.dumps(arr)


def OpenCamera(cam_num):
    Camera.set_video_source(int(cam_num))
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



def CloseCamera():
    Camera.stop()
    return "Camera stopped"




# def getVideoFrame(video):
#     print("camera getting frame")
#     success, image = video.read()
#     width = int(video.get(3))
#     height = int(video.get(4))

#     w2 = int(width/2)
#     h2 = int(height/2)

#     image = cv2.line(image, (w2,0), (w2,height), (0,255,255), 1)
#     image = cv2.line(image, (0, h2), (width, h2), (0,255,255), 1)
    
#     ret, jpeg = cv2.imencode('.jpg', image)

#     return jpeg.tobytes()



def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
               