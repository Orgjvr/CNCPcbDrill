from flask import session, redirect, url_for, render_template, request, Response, flash, Flask, g
from .. import main
#from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
import json
import logging
import jsonpickle
from flask import current_app as app
from .. import processFile
from .. import propFunctions
from .. import coreFunctions

from collections import defaultdict
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import io
from ..classes import Job





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
          
            #NOTE:  @ORG 

            #NOTE: ok , first test, after uploading the drill file, run the load the localhost:5000/test22  page - is shows that the Job instance (called job ) is still in scope...
            #NOTE: but i can't figure out how to access this from the event fired by the process button 


            #NOTE: this is to test the saving of the job class into a session variable  - we can't save objects in there so jsonpickle serializes the object 
            #NOTE: this works in the immediate context  (below)
            #print("the max distance is " + str(job.maxDistance))
            #print('setting job session variable via json pickle ')
            #session['job'] =  jsonpickle.encode(job)

            #print("getting it back")
            #newJob = jsonpickle.decode(session['job'])
            #print("the max distance is " + str(newJob.maxDistance))

            #NOTE: BUT ......
            #NOTE:  if i call do an http get /test_session from browser - the session does not contain the job object

            #NOTE: one last attempt / ok now really last ...  / this doesnt work as g is lost between requests  
            '''
            serializedJob = jsonpickle.encode(job)
            g.serialized_job = serializedJob

            if 'serialized_job' in  g:
                print( "G has 'serialized_job'")
            '''
            #NOTE: only other thing i can think of is to save the serialized object (job) to an in mem DB or a file !!!
            # and read the same db / file in events.py ( or later )

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
    axis.plot( job.h2.zeroedAndFlippedPoint,job.h1.zeroedAndFlippedPoint, linewidth=2, color='blue')

    axis.text(job.h1.zeroedAndFlippedPoint[0],job.h1.zeroedAndFlippedPoint[1], ' Hole 1',size=15) 
    axis.text(job.h2.zeroedAndFlippedPoint[0],job.h2.zeroedAndFlippedPoint[1], ' Hole 2',size=15)
    # label holes 

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
    toolCollection = dict()
    for t in job.tools:
        tool = dict()
        tool["toolNum"] = int(t.toolNum)
        tool["size"] = float(t.size)
        tool["holeCount"] = t.holeCount
        tool["color"] = colordict[str(t.toolNum)]
        toolCollection[int(t.toolNum)] = tool


    '''
    # try get job 
    
    #NOTE: ok this doesnt work as the g context is lost between requests 

    # sjob = serializedJob
    if('serialized_job' in g):
        sjob = g.serialized_job
        print("object was in g")
    else:
        print("object was NOT in g")
        sjob = "failed"
    '''
    
    # now pass to tempate 
    return render_template('index.html', toolCollection=toolCollection, sPorts=[], serialPort='')
    

@main.route('/plot_png')
def plot_png():
    print('in Plot_png')
    fig = create_figure()
    print('after create_figure')
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    print("plotting")
    return Response(output.getvalue(), mimetype='image/png')

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
