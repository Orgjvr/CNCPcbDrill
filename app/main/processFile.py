import logging
from collections import defaultdict
from .classes import Hole
from .classes import Tool
from .classes import Job
from .views import views_file


#def ReadFile(job):
#    job.h1, job.h2, job.maxDistance = ReadFile(job.inputFilename, job.tools, job.holes)
  
#def ReadFile(inputFilename, tools, holes):
def ReadFile(job):
    #params needed: 
    # 1 File name
    # 2 This is our toolsDict dictionary which will be populated
    # 3 This is our holes array
    # 4 Digits in front of Decimal. Normally 3
    # 5 Digits following Decimal. Normally 3
    
    inputFilename = job.inputFilename



    inHeader = True
    job.isMetric = False
    job.isInch = False
    job.isLZ = False
    job.isTZ = False    
    job.intDigits = -1
    job.decDigits = -1
    currentTool = -1
    holeNum = 0
    job.fileType = ""
    
    #NOTE: added get min & max for holes into read loop 
    minY = 999.999
    minX = 999.999
    maxX = -999.999
    maxY = -999.999

    f = open(inputFilename,"r")
    fl = f.readlines()
    for x in fl:

        ''' 
        KiCad Header
        M48
        ; DRILL file {KiCad (5.1.4-0-10_14)} date Monday, 16 September 2019 at 14:14:34
        ; FORMAT={3:3/ absolute / metric / suppress leading zeros}
        ; #@! TF.CreationDate,2019-09-16T14:14:34+02:00
        ; #@! TF.GenerationSoftware,Kicad,Pcbnew,(5.1.4-0-10_14)
        FMAT,2
        METRIC, TZ
        '''

        if "KiCad" in x:
            job.fileType = "K"
            
        if "EAGLE" in x:
            job.fileType = "E"


        if "FORMAT=" in x and job.fileType == "K":
            pos = x.find("{")
            endpos = x.find("}")
            logging.debug(" start " + str(pos))
            logging.debug(" end " + str(endpos))
            logging.debug( x[pos+1: endpos])
            parts = x[pos+1:endpos].split("/")
            for p in parts:
                if ":" in p:
                    decs = p.split(":")
                    job.intDigits = int(decs[0])
                    job.decDigits = int(decs[1])
            logging.debug(" FileType = %s, Format is intDigits : %d , decDigits : %d"% (job.fileType, job.intDigits, job.decDigits))

        #Determine if we reached the end of the Header section yet
        if x[0] == '%' or "M95" in x:
            inHeader = False
            logging.debug("Found end of Header")
            if job.intDigits == -1 or job.decDigits == -1:
                #format not found 
                logging.warn("format not found in file, setting default of 3:3")
                job.intDigits = 3
                job.decDigits = 3

        if inHeader:
            if "METRIC" in x:
                if(job.fileType == "E"):
                    parts = x.split(",")
                    for p in parts:
                        if "0.0" in p:
                            decs = p.split(".")
                            print(" the first part of the decs is [%s], second = [%s]"% (decs[0], decs[1]))
                            job.intDigits = decs[0].strip().__len__()
                            job.decDigits = decs[1].strip().__len__()
                            print(" FileType = %s, Format is intDigits : %d , decDigits : %d"% (job.fileType, job.intDigits, job.decDigits))

                job.isMetric = True
                logging.debug("Found metric")
            if "INCH" in x:
                job.isInch = True
                logging.debug("Found inch")
            if "TZ" in x:
                job.isTZ = True
                logging.debug("Found TZ")
            if "LZ" in x:
                job.isLZ = True
                logging.debug("Found LZ")
            if x[0] == "T" and "C" in x:
                #Found a tool
                parts = x.split("C")
                toolNumber = parts[0][1:5].strip()
                toolSize = parts[1].strip()
                logging.debug("Found a Tool - Toolnumber=%s with Size=%s", toolNumber, toolSize)
                #toolsDict[toolNumber] = toolSize.strip()
                job.tools.append(Tool.Tool(toolNumber, toolSize, "0"))

        if not inHeader:
            #read Tools
            if x[0] == "T":
                currentTool = int(x[1:5].strip())
                toolSize = job.getTool(currentTool).size
                logging.info("ToolSize=<"+str(toolSize)+">")

            
            #read holes
            if x.startswith("X") and "Y" in x:
                # we have a hole 
                parts = x.split("Y")
                xpart = parts[0][1:(1+job.intDigits+job.decDigits)]
                
                ypart = parts[1]
                if job.isTZ:
                    xval = float(xpart)/(10**job.decDigits)
                    yval = float(ypart)/(10**job.decDigits)
                else:
                    #Thus it must be isLZ
                    xval = float(xpart[0:job.intDigits]+"."+xpart[job.intDigits:job.intDigits+job.decDigits])
                    yval = float(ypart[0:job.intDigits]+"."+ypart[job.intDigits:job.intDigits+job.decDigits])

                #print("first Part = %s, second = %s, final = %3.3f"% (parts[0],xpart, xval))
                

                filePoint = xval, yval

                # igoring vxal == maxX as it will not change anything 
                if(xval > maxX):
                    maxX = xval
                if(xval < minX):
                    minX = xval
                
                if(yval > maxY):
                    maxY = yval
                if(yval < minY):
                    minY = yval

                holeNum = holeNum + 1
                logging.info("Found a Hole - Holenumber=%s with X=%s and Y=%s and line=%s", holeNum, xval, yval, x)
                job.holes.append(Hole.Hole(holeNum, filePoint, currentTool, toolSize, job.isMetric))
                job.getTool(currentTool).holeCount += 1

            
                # Warn if Toolnumber=0 
                if currentTool == -1:
                    logging.warning("Found a hole but no tool... - Toolnumber=%s with Size=%s", toolNumber, toolSize)


    #Done reading file.         
    f.close()

    job.numHoles = holeNum

    #Sanities
    if job.isInch and job.isMetric:
        logging.warning("Found both METRIC and INCH. Assume METRIC")
        job.isMetric = True
        job.isInch = False

    if not (job.isInch or job.isMetric):
        logging.warning("Did not find either METRIC or INCH. Assume METRIC")
        job.isMetric = True
    
    if job.isLZ and job.isTZ:
        logging.warning("Found both TZ and LZ. Assume TZ")
        job.isTZ = True
        job.isLZ = False

    if not (job.isLZ or job.isTZ):
        logging.warning("Did not find either TZ and LZ. Assume TZ")
        job.isTZ = True

    #print tools
    #print("Now print tools:")
    #Tool.PrintTools(tools)

    # flip & zero
    for h in job.holes:
        h.translateAndFlipHole(minY, maxY, minX )
    #print("Holes translated & flipped")

    # get maxDistance
    job.h1, job.h2, job.maxDistance = Hole.FindMaxDistanceBetweenHoles(job.holes)
    
    logging.info("Max Distance is between hole: %d and %d with a distance of %f"% (job.h1.holeNumber, job.h2.holeNumber, job.maxDistance))

def generateGcode():
    jobObject = views_file.job
    # output html String 
    outString = ""

    for h in jobObject.holes:
        # for now only get 3mm holes 
        if h.size == 3.0:
            # add hole to html
            outString += "G0 X%3.3f Y%3.3f Z%3.3f  \n"% (h.CNCDrillPosition[0], h.CNCDrillPosition[1], jobObject.CNC_SAFE_HEIGHT)
            outString += "G0 Z%3.3f F500 \n"% (jobObject.CNC_SAFE_HEIGHT + jobObject.CNC_DRILL_DEPTH)
            outString += "G0 Z%3.3f \n"% (jobObject.CNC_SAFE_HEIGHT)
            outString += "\n"
    return outString
