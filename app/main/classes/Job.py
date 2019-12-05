from collections import defaultdict
import math
import logging
from .. import processFile
from . import Hole

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
        self.numHoles = 0
        # CNC ----------------------------
        self.CNChole1 = [-999.999,-999,999]
        self.CNChole2 = [-999.999,-999,999]
        self.CNCRadAngle = 0.0
        self.CNCScale = 1.0
        self.CNCDistance = 0.0
        self.CNC_PCB_ORIGIN = [-999.999,-999,999]
        self.CNC_SAFE_HEIGHT = 0.0
        self.CNC_DRILL_DEPTH = 0.0
        # PCB ----------------------------
        self.PCBRadAngle = 0.0
        self.PCBDistance = 0.0
        # GCode --------------------------
        self.GCodeRotation = 0.0
        


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
        # CNC ---------------------------
        #self.CNChole1 = [-999.999,-999.999]
        #self.CNChole2 = [-999.999,-999,999]
        #self.CNCRadAngle = 0.0
        #self.CNCScale = 1.0
        #self.CNCDistance = 0.0      # distance between holes 1 & 2
        # PCB ----------------------------
        #self.PCBRadAngle = 0.0
        #self.PCBDistance = 0.0      # distance between holes 1 & 2
        # GCode --------------------------
        #self.GCodeRotation = 0.0


        processFile.ReadFile(self)

        # calculate angle between holes 
        self.PCBRadAngle = math.atan2(self.h2.ZFY - self.h1.ZFY, self.h2.ZFX - self.h1.ZFX)

        logging.info("# holes : %d, tools : %d, Hole1 : %d, Hole2 : %d"% (self.holes.__len__(), self.tools.__len__(), self.h1.holeNumber, self.h2.holeNumber))

    def calculatePCBRotationInRads (self):

        h1X , h1Y = self.CNChole1
        h2X , h2Y = self.CNChole2

        # calculate distances & scale 
        self.CNCDistance = math.sqrt( (h1X-h2X)**2 + (h1Y-h2Y)**2)
        self.PCBDistance = math.sqrt( (self.h1.ZFX-self.h2.ZFX)**2 + (self.h1.ZFY-self.h2.ZFY)**2)
        self.CNCScale = self.CNCDistance / self.PCBDistance * 100


        # calculate angle between holes 
        self.CNCRadAngle = math.atan2(h2Y-h1Y, h2X-h1X)

        # calculate GCode Rotation
        self.GCodeRotation = self.CNCRadAngle - self.PCBRadAngle
        print(" G code rotation  : %3.3f" %( math.degrees(self.GCodeRotation )))

        # calculate position of PCB 0,0 on CNC from Hole1
        holeAngleToZero = self.h1.angleFromZero*-1
        print(" hole angle to Zero : %3.3f" %( math.degrees(holeAngleToZero)))

        GCodeAngleToZero = holeAngleToZero - self.GCodeRotation*-1
        print(" Gcode Angle to Zero : %3.3f" %( math.degrees(GCodeAngleToZero)))

        holeDistanceToZero = self.h1.distanceFromZero
        PcbOriginOnCNC_X = self.CNChole1[0] + ( holeDistanceToZero * (self.CNCScale/100) * math.cos(GCodeAngleToZero))
        PcbOriginOnCNC_Y = self.CNChole1[1] + ( holeDistanceToZero * (self.CNCScale/100) * math.sin(GCodeAngleToZero))
        
        self.CNC_PCB_ORIGIN = PcbOriginOnCNC_X, PcbOriginOnCNC_Y

        # testing 
        #self.GCodeRotation = math.radians(-90)

        for thisHole in self.holes:
            thisHole.calculateCNCPoint(self.CNC_PCB_ORIGIN, self.GCodeRotation, self.CNCScale)


        return self.CNCRadAngle

    


     
