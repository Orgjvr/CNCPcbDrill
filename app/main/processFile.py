import logging
from collections import defaultdict
from main import Hole

  
    
def ReadFile(inputFilename, holes, intDigits, decDigits):
    #params needed: 
    # 1 File name
    # 2 This is our holes array
    # 3 Digits in front of Decimal. Normally 3
    # 4 Digits following Decimal. Normally 3
    
    #intDigits = 3
    #decDigits = 3
    #inputFilename = "pic_programmer2.drl"

    inHeader = True
    isMetric = False
    isInch = False
    isLZ = False
    isTZ = False
    currentTool = 0
    holeNum = 0
    toolsDict = dict()

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
                toolSize = parts[1]
                logging.debug("Found a Tool - Toolnumber=%s with Size=%s", toolNumber, toolSize)
                toolsDict[toolNumber] = toolSize.strip()

        if not inHeader:
            #read Tools
            if x[0] == "T":
                currentTool = int(x[1:5].strip())
            
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

                holeNum = holeNum + 1
                logging.debug("Found a Hole - Holenumber=%s with X=%s and Y=%s and line=%s", holeNum, xval, yval, x)
                holes.append(Hole.Hole(holeNum, filePoint, currentTool, toolsDict[str(currentTool)], isMetric))

            
                # Warn if Toolnumber=0 
                if currentTool == 0:
                    logging.warning("Found a hole but no tool... - Toolnumber=%s with Size=%s", toolNumber, toolSize)


    #Done reading file.         
    f.close()

    #Sanities
    if isInch and isMetric:
        logging.debug("Found both METRIC and INCH. Assume METRIC")
        isMetric = True
        isInch = False

    if not (isInch or isMetric):
        logging.debug("Did not find either METRIC or INCH. Assume METRIC")
        isMetric = True
    
    if isLZ and isTZ:
        logging.debug("Found both TZ and LZ. Assume TZ")
        isTZ = True
        isLZ = False

    if not (isLZ or isTZ):
        logging.debug("Did not find either TZ and LZ. Assume TZ")
        isTZ = True



