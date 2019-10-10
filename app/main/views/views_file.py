from flask import session, redirect, url_for, render_template, request, Response, flash
from .. import main
#from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
import json
import logging
from flask import current_app as app
from .. import processFile
from collections import defaultdict
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import io

ALLOWED_EXTENSIONS = set(['drl', 'txt', 'xln'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_figure():
    logging.info("creating Figure.........")
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    #fig = plt.figure(figsize=(10,8))
    
    colordict = dict(app.config.get('COLOR_DICT'))
    #cnt = 0
    for h in g_holes:
        #if(cnt < 260):
            px = h.zeroedAndFlippedPoint[0]
            py = h.zeroedAndFlippedPoint[1] 
            #axis.plot(px, py, color=colordict[h.toolNum],markersize=toolDict[h.toolNum]*2 ,marker='o')
            logging.info("Plotting hole: "+str(h.holeNumber))
            axis.plot(px, py, color=colordict[h.toolNum],markersize=(h.size)*2 ,marker='o')
        #    cnt += 1
        #else:
        #    break
    #font = {'family': 'serif', 
    #        'color':  'darkred',
    #        'weight': 'normal',
    #    }
    #        'size': 16,
    
    #axis.set_title("Max Distance : %3.3f "% (maxDistance))
    # plot max Line
    #axis.add_line(Line2D(line1_xs, line1_ys, linewidth=2, color='blue'))
    #axis.plot( h0.zeroedAndFlippedPoint, h1.zeroedAndFlippedPoint, linewidth=2, color='red')
    return fig


@main.route('/uploads/<filename>')
def uploaded_file(filename):
    #logging.basicConfig(level=logging.DEBUG)
    logging.debug("Building endpoint uploaded_file")
    colordict = dict(app.config.get('COLOR_DICT'))
    toolCollection = dict()
    for t in g_tools:
        tool = dict()
        tool["toolNum"] = int(t.toolNum)
        tool["size"] = float(t.size)
        tool["holeCount"] = t.holeCount
        tool["color"] = colordict[int(t.toolNum)]
        toolCollection[int(t.toolNum)] = tool
    #print("urlmap")
    #print(app.url_map)
    #for t in toolCollection:
    #    td = toolCollection[t]
    #    #print(td)
    #return render_template('index.html', toolCollection=toolCollection, sPorts=sPorts, checkit=checkit, serialPort=serialPort)
    return render_template('index.html', toolCollection=toolCollection, sPorts=[], serialPort='')
    #return "uploaded_file rendered"

#@main.route('/', methods=['GET', 'POST'])
@main.route('/open_file', methods=['GET', 'POST'])
def upload_file():
    #logging.basicConfig(level=logging.DEBUG)
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
            UploadFolder = str(app.config.get('UPLOAD_FOLDER'))
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
            # Get some more config settings
            # replaced with Read from Drill File 
            #intDigits = int(app.config.get('INTEGER_DIGITS_IN_DRILLFILE'))
            #decDigits = int(app.config.get('DECIMAL_DIGITS_IN_DRILLFILE'))
            #print("About to process file....")
            global g_holes
            g_holes = []
            global g_tools
            g_tools = []
            processFile.ReadFile(filepath, g_tools, g_holes)
            #processFile(filepath)
            return redirect(url_for('main.uploaded_file', filename=filename))
            #return 'uploads/'+str(filename)
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

@main.route('/plot_png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    print("plotting")
    return Response(output.getvalue(), mimetype='image/png')

