#!/bin/env python
from app import create_app, socketio
import logging

app = create_app(debug=True)

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    socketio.run(app)
    

