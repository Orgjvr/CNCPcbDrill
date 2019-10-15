from flask import session, redirect, url_for, render_template, request, Response
from .. import main
#from .forms import LoginForm
import cv2
from .camera import VideoCamera
import json
import logging
from flask import current_app as app


def get_cameras():
    print("cams funcs get cam")
    logging.basicConfig(level=logging.DEBUG)
    #index = 2
    arr = []
    for index in range(5):
        try:
            print("Cam="+index)
            cap = cv2.VideoCapture(index)
            cap.release()
        except:
            pass
        try:
            logging.debug("Try to read camera no <" + str(index) + ">")
            if not cap.read()[0]:
            cap = cv2.VideoCapture(index)
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
    print("Returning cams " + json.dumps(arr))
    return arr
    #return json.dumps(arr)


