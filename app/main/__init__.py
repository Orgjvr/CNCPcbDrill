from flask import Blueprint

main = Blueprint('main', __name__)

# views subfolder
from .views import views, views_serial, views_camera, views_file

from . import models, forms, events
from .camera import VideoCamera

from . import serialFunctions
from . import cameraFunctions
from . import processFile


serialFunctions.printSerialPorts()



