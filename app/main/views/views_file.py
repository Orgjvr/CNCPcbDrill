from flask import session, redirect, url_for, render_template, request, Response, flash, Flask, g
from .. import main
#from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
import json
import logging
#import jsonpickle
from flask import current_app as app
from .. import processFile
from .. import propFunctions
from .. import coreFunctions
from .. import serialFunctions

from collections import defaultdict
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import io
from ..classes import Job
from ..classes import Hole



job = Job.Job()


ALLOWED_EXTENSIONS = set(['drl', 'txt', 'xln'])

@main.route('/', methods=['GET', 'POST'])
@main.route('/open_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("POSTING")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            UploadFolder = propFunctions.getProperty('default','UPLOAD_FOLDER',"uploads")
            logging.debug("UploadFolder : " + UploadFolder)
            global filepath
            filepath = os.path.join(UploadFolder, filename)
            logging.debug("#######################################")
            logging.debug("FilePath : " + filepath)
            logging.debug("#######################################")
            if not os.path.exists(UploadFolder):
                os.mkdir(UploadFolder)
            try:
                os.remove(filepath)
            except:
                pass
            file.save(filepath)
            # read file 
         
            
            job.newJob(filepath)
          
            return redirect(location= url_for('main.uploaded_file', filename=filename))
          
    logging.debug("GETTING")
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    
    '''



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_figure():
    print("creating Figure.........")
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    #fig = plt.figure(figsize=(10,8))
    
    colordict = propFunctions.getDictionary('default', 'COLOR_DICT', '')
    #cnt = 0
    for h in job.holes:
        #if(cnt < 260):
            px = h.zeroedAndFlippedPoint[0]
            py = h.zeroedAndFlippedPoint[1] 
            logging.info("Plotting hole: "+str(h.holeNumber))
            axis.plot(px, py, color=colordict[str(h.toolNum)],markersize=(h.size)*2 ,marker='o')
     
    #NOTE: dont know why these points have to be swopped!!! 
    #axis.plot( job.h2.zeroedAndFlippedPoint,job.h1.zeroedAndFlippedPoint, linewidth=2, color='blue')
    axis.plot( (job.h1.zeroedAndFlippedPoint[0],job.h2.zeroedAndFlippedPoint[0]),(job.h1.zeroedAndFlippedPoint[1],job.h2.zeroedAndFlippedPoint[1]), linewidth=2, color='blue')

    axis.text(job.h1.zeroedAndFlippedPoint[0],job.h1.zeroedAndFlippedPoint[1], ' Hole 1',size=15) 
    axis.text(job.h2.zeroedAndFlippedPoint[0],job.h2.zeroedAndFlippedPoint[1], ' Hole 2',size=15)
    # label holes 

    return fig

def create_cnc_figure():
    print("creating Figure.........")
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    
    colordict = propFunctions.getDictionary('default', 'COLOR_DICT', '')

    # CNCHole1 & 2
    axis.plot(job.CNChole1[0], job.CNChole1[1], color="red", markersize=3, marker='o')
    axis.plot(job.CNChole2[0], job.CNChole2[1], color="red", markersize=3, marker='o')
    
    # line between the points
    # NOTE: the line needs ( in this case? ) and array of X points followed by an array of Y points
    axis.plot( (job.CNChole1[0], job.CNChole2[0]),(job.CNChole1[1], job.CNChole2[1]), linewidth=1, color='red')

    # plot 0,0 axis    
    # so that graphs expands to show orientations 
    #axis.plot( (0, 0), (5, -5), linewidth=1, color='black')
    #axis.plot( (5, -5), (0, 0), linewidth=1, color='black')

    # next calculate location of PCB 0,0 
    axis.plot(job.CNC_PCB_ORIGIN[0], job.CNC_PCB_ORIGIN[1], color="green", markersize=1, marker='o')

    axis.plot( (job.CNC_PCB_ORIGIN[0], job.CNC_PCB_ORIGIN[0]), (job.CNC_PCB_ORIGIN[1] + 5, job.CNC_PCB_ORIGIN[1]-5), linewidth=1, color='green')
    axis.plot( (job.CNC_PCB_ORIGIN[0] + 5, job.CNC_PCB_ORIGIN[0]-5), (job.CNC_PCB_ORIGIN[1], job.CNC_PCB_ORIGIN[1]), linewidth=1, color='green')

    maxX = 0.0
    maxY = 0.0
    minX = 999
    minY = 999

    for thisHole in job.holes:
        axis.plot(thisHole.CNCDrillPosition[0], thisHole.CNCDrillPosition[1], color="blue", markersize=0.5, marker='o')
        if(thisHole.CNCDrillPosition[0] > maxX): 
            maxX = thisHole.CNCDrillPosition[0]
        if(thisHole.CNCDrillPosition[1] > maxY): 
            maxY = thisHole.CNCDrillPosition[1]
        if(thisHole.CNCDrillPosition[0] < minX): 
            minX = thisHole.CNCDrillPosition[0]
        if(thisHole.CNCDrillPosition[1] < minY): 
            minY = thisHole.CNCDrillPosition[1]

    # plot max markers to try and square image 
    if(maxX < maxY):
        maxX = maxY
    if(minX > minY):
        minX = minY
    axis.plot(maxX, maxX , color="green", markersize=1, marker='o')
    axis.plot(minX, minX , color="green", markersize=1, marker='o')
    

    return fig



@main.route('/uploads/<filename>', methods=['POST','GET'])
def uploaded_file(filename): 

    logging.debug("Building endpoint uploaded_file")
    #try:
    global colordict
    print("getting Value from default - returned")
    ans = propFunctions.getProperty('default','COLOR_DICT','None')
    print(ans)
    print("loading json.....")
    jans = json.loads(ans)
    print(jans)

    try:
        colordict = dict(jans)
    except Exception as e:
        print(e)

    #cncMove = dict(app.config.get('CNC_MOVES'))
    global toolCollection
    toolCollection = dict()
    for t in job.tools:
        tool = dict()
        tool["toolNum"] = int(t.toolNum)
        tool["size"] = float(t.size)
        tool["holeCount"] = t.holeCount
        tool["color"] = colordict[str(t.toolNum)]
        toolCollection[int(t.toolNum)] = tool


   
    # now pass to tempate 
    return render_template('index.html', toolCollection=toolCollection, sPorts=[], serialPort='', job=job)
    
@main.route('/cont')
def cont(): 
    currentPortAndBaud = serialFunctions.getCurrentPortAndBaud()
    currentPort = json.loads(currentPortAndBaud)["port"]
    print("Port=" + currentPort)
    return render_template('index.html', toolCollection=toolCollection, sPorts=[], serialPort=currentPort)


@main.route('/plot_png')
def plot_png():
    print('in Plot_png')
    fig = create_figure()
    print('after create_figure')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    print("plotting")
    return Response(output.getvalue(), mimetype='image/png')

@main.route('/plot_cnc_png')
def plot_cnc_png():
    print('in Plot_cnc_png')
    fig_cnc = create_cnc_figure()
    print('after create_figure')
    output_cnc = io.BytesIO()
    FigureCanvas(fig_cnc).print_png(output_cnc)
    print("plotting cnc_fig")
    return Response(output_cnc.getvalue(), mimetype='image/png')



@main.route('/test_session')
def test_session():

    ans = ""
    print("getting job copy from session")
    newJob = jsonpickle.decode(session['job'])
    print(" ok we got it - theoretically " )
    if 'job' in session:
        ans = "the job object is in the session"
        print(ans)
    else:
        ans = "the job object is NOT in the session"
        print(ans)
    return Response(ans)


@main.route('/test22')
def test22():

        retVal = ""
        for t in job.tools:
            retVal += "tool # " + str(t.toolNum + " = " + str(t.holeCount) + "<br/>")
        
        return Response(retVal)
