from flask import session, redirect, url_for, render_template, request, Response
from . import main
#from flask import send_from_directory
import os
from werkzeug.utils import secure_filename
import json
import logging
from flask import current_app as app
from . import processFile
from collections import defaultdict

ALLOWED_EXTENSIONS = set(['drl', 'txt', 'xln'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Building endpoint uploaded_file")
    toolCollection = dict()
    for t in g_tools:
        tool = dict()
        tool["toolNum"] = int(t.toolNum)
        tool["size"] = float(t.size)
        tool["holeCount"] = t.holeCount
        tool["color"] = "black" #colordict[int(t)]
        toolCollection[int(t.toolNum)] = tool
    #print("urlmap")
    #print(app.url_map)
    #for t in toolCollection:
    #    td = toolCollection[t]
    #    #print(td)
    #return render_template('index.html', toolCollection=toolCollection, sPorts=sPorts, checkit=checkit, serialPort=serialPort)
    return render_template('index.html', toolCollection=toolCollection, sPorts=[], serialPort='')
    #return "uploaded_file rendered"

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
            intDigits = int(app.config.get('INTEGER_DIGITS_IN_DRILLFILE'))
            decDigits = int(app.config.get('DECIMAL_DIGITS_IN_DRILLFILE'))
            #print("About to process file....")
            global g_holes
            g_holes = []
            global g_tools
            g_tools = []
            processFile.ReadFile(filepath, g_tools, g_holes, intDigits, decDigits)
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

