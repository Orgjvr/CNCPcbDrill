from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from . import serialFunctions 

@socketio.on('get3dPos', namespace='/sock')
def get3dPos(message):
    """Get the machine position and send it back to the browser"""
    pos = serialFunctions.get3dPos()
    print("Emitting position")
    emit('position', pos)
    return pos


@socketio.on('openSerial', namespace='/sock')
def openSerial(portName,baud):
    """Open serial port to machine returning message to browser"""
    print("Opening serial")
    #portName = portName.replace("~","/")
    success = serialFunctions.openSerialPort(portName,baud)
    return success

