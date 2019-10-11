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

        processFile.ReadFile(self)

        print("# holes : %d, tools : %d, Hole1 : %d, Hole2 : %d"% (self.holes.__len__(), self.tools.__len__(), self.h1.holeNumber, self.h2.holeNumber))


     
