from collections import defaultdict
import math
import logging
from .. import processFile


class Job:

    #tool_index = defaultdict(list)

    def __init__(self):
        self.inputFilename = ""
        self.holes = []
        self.tools = []
        self.h1 = None
        self.h2 = None
        self.maxDistance = -999.999
        self.isMetric = False
        self.isInch = False
        self.intDigits = -1
        self.decDigits = -1
        self.isTZ = False
        self.isLZ = False
        self.fileType = ""
        self.CNChole1 = [-999.999,-999,999]
        self.CNChole2 = [-999.999,-999,999]
        self.CNCRadAngle = 0.0
        self.PCBRadAngle = 0.0


    def newJob(self, inputFileName):
        self.inputFilename = inputFileName
        self.holes = []
        self.tools = []
        self.h1 = None
        self.h2 = None
        self.maxDistance = -999.999
        self.isMetric = False
        self.isInch = False
        self.intDigits = -1
        self.decDigits = -1
        self.isTZ = False
        self.isLZ = False
        self.fileType = ""
        self.CNChole1 = [-999.999,-999.999]
        self.CNChole2 = [-999.999,-999,999]
        self.CNCRadAngle = 0.0
        self.PCBRadAngle = 0.0

        processFile.ReadFile(self)

        # calculate angle between holes 
        self.PCBRadAngle = math.atan2(self.h2.ZFY - self.h1.ZFY, self.h2.ZFX - self.h1.ZFX)

        logging.info("# holes : %d, tools : %d, Hole1 : %d, Hole2 : %d"% (self.holes.__len__(), self.tools.__len__(), self.h1.holeNumber, self.h2.holeNumber))

    def setCNCholes(self, h1X, h1Y, h2X, h2Y):
        self.CNChole1 = float( h1X) , float (h1Y) 
        self.CNChole2 = float (h2X) , float (h2Y)

        # calculate angle between holes 
        self.CNCRadAngle = math.atan2(self.CNChole2[1] - self.CNChole1[1], self.CNChole2[0] - self.CNChole1[1])
        return self.CNCRadAngle

    


     
