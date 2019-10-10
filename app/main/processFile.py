import logging
from collections import defaultdict
from . import Hole
from . import Tool

  
def ReadFile(inputFilename, tools, holes, intDigits, decDigits):
    #params needed: 
    # 1 File name
    # 2 This is our toolsDict dictionary which will be populated
    # 3 This is our holes array
    # 4 Digits in front of Decimal. Normally 3
    # 5 Digits following Decimal. Normally 3
    
    inHeader = True
    isMetric = False
    isInch = False
    isLZ = False
    isTZ = False    
    currentTool = -1
    holeNum = 0
    
    #NOTE: added get min & max for holes into read loop 
    minY = 999.999
    minX = 999.999
    maxX = -999.999
    maxY = -999.999
    
    f = open(inputFilename,"r")
    fl = f.readlines()
    for x in fl:

        #Determine if we reached the end of the Header section yet
        if x[0] == '%' or "M95" in x:
            inHeader = False
            logging.debug("Found end of Header")

        if inHeader:
            if "METRIC" in x:
                isMetric = True
                logging.debug("Found metric")
            if "INCH" in x:
                isInch = True
                logging.debug("Found inch")
            if "TZ" in x:
                isTZ = True
                logging.debug("Found TZ")
            if "LZ" in x:
                isLZ = True
                logging.debug("Found LZ")
            if x[0] == "T" and "C" in x:
                #Found a tool
                parts = x.split("C")
                toolNumber = parts[0][1:5].strip()
                toolSize = parts[1].strip()
                logging.debug("Found a Tool - Toolnumber=%s with Size=%s", toolNumber, toolSize)
                #toolsDict[toolNumber] = toolSize.strip()
                tools.append(Tool.Tool(toolNumber, toolSize, "0"))

        if not inHeader:
            #read Tools
            if x[0] == "T":
                currentTool = int(x[1:5].strip())
                toolSize = tools[currentTool-1].size
                print("ToolSize=<"+str(toolSize)+">")

            
            #read holes
            if x.startswith("X") and "Y" in x:
                # we have a hole 
                parts = x.split("Y")
                xpart = parts[0][1:(1+intDigits+decDigits)]
                ypart = parts[1]
                if isTZ:
                    xval = float(xpart)/(10**decDigits)
                    yval = float(ypart)/(10**decDigits)
                else:
                    #Thus it must be isLZ
                    xval = float(xpart[0:intDigits]+"."+xpart[intDigits:intDigits+decDigits])
                    yval = float(ypart[0:intDigits]+"."+ypart[intDigits:intDigits+decDigits])
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
                logging.debug("Found a Hole - Holenumber=%s with X=%s and Y=%s and line=%s", holeNum, xval, yval, x)
                holes.append(Hole.Hole(holeNum, filePoint, currentTool, toolSize, isMetric))
                tools[currentTool-1].holeCount += 1

            
                # Warn if Toolnumber=0 
                if currentTool == -1:
                    logging.warning("Found a hole but no tool... - Toolnumber=%s with Size=%s", toolNumber, toolSize)


    #Done reading file.         
    f.close()

    #Sanities
    if isInch and isMetric:
        logging.warning("Found both METRIC and INCH. Assume METRIC")
        isMetric = True
        isInch = False

    if not (isInch or isMetric):
        logging.warning("Did not find either METRIC or INCH. Assume METRIC")
        isMetric = True
    
    if isLZ and isTZ:
        logging.warning("Found both TZ and LZ. Assume TZ")
        isTZ = True
        isLZ = False

    if not (isLZ or isTZ):
        logging.warning("Did not find either TZ and LZ. Assume TZ")
        isTZ = True

    #print tools
    #print("Now print tools:")
    #Tool.PrintTools(tools)

    # flip & zero
    for h in holes:
        h.translateAndFlipHole(minY, maxY, minX )
    #print("Holes translated & flipped")

    # get maxDistance
    global maxDistance
    global h0
    global h1
    h0, h1, maxDistance = Hole.FindMaxDistanceBetweenHoles(holes)
    print("Max Distance is between hole: %d and %d with a distance of %f"% (h0.holeNumber, h1.holeNumber, maxDistance))


