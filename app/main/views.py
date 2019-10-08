from flask import session, redirect, url_for, render_template, request, Response
from . import main
#from .forms import LoginForm
import cv2
from .camera import VideoCamera

@main.route('/hi')
def hi():
        return "Hello World!"

@main.route('/')
def index():
        return "You have reached a dead end on the internet... :("

@main.route('/c0')
def cam0():
        global camIndex
        camIndex = 0
        return "Camera 0 selected"
        #return "/video_feed"

@main.route('/c2')
def cam2():
        global camIndex
        camIndex = 2
        return "Camera 2 selected"
        #return "/video_feed"

@main.route('/c4')
def cam4():
        global camIndex
        camIndex = 4
        return "Camera 4 selected"
        #return "/video_feed"

@main.route('/get_cameras')
def get_cameras():
    #index = 2
    arr = []
    for index in range(5):
        try:
            print("Try to read camera no <" + str(index) + ">")
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                print("Cannot read camera no <" + str(index) + ">")
                #break
            else:
                print("Adding camera no <" + str(index) + ">")
                arr.append(index)
                index += 1
                cap.release()
        except:
            print("Cannot close")
            #break

    global sCameras
    sCameras = arr
    return  "nothing"


def gen(camera):
    camera.__del__ #  .release()
    
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@main.route('/video_feed')
def video_feed():
    global camIndex
    #print('getting video feed')
    #if oldIndex != camIndex:
    #    mustCaptureVideo = False
    #    oldIndex=camIndex
    #return Response(gen(VideoCamera(0)),
    return Response(gen(VideoCamera(camIndex)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
