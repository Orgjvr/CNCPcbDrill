from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, models, forms, events
from .camera import VideoCamera

from . import serialFunctions
from . import cameraFunctions
from . import processFile

serialFunctions.printSerialPorts()



