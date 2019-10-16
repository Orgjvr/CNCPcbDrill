import os
import cv2
from .base_camera import BaseCamera


class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        camera.set(3,320)
        camera.set(4,240)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            width = int(camera.get(3))
            height = int(camera.get(4))

            w2 = int(width/2)
            h2 = int(height/2)

            img = cv2.line(img, (w2,0), (w2,height), (0,255,255), 1)
            img = cv2.line(img, (0, h2), (width, h2), (0,255,255), 1)
    
            #old code# ret, jpeg = cv2.imencode('.jpg', img)

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()



