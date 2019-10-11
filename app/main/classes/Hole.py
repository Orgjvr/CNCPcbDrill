from collections import defaultdict
import math
import logging
from .. import processFile

class Hole:

    hole_index = defaultdict(list)

    def __init__(self, holeNum, point, toolNum, size, isMetric):
        self.toolNum = toolNum
        self.size = size
        self.filePoint = point
        self.rotationAngle = 0
        self.isHoleZero = False
        self.isHole2 = False
        self.holeZero = None
        self.flippedY = None
        self.zeroedAndFlippedPoint = [-999.999, -999.999]
        self.rotatedPoint = None
        self.holeNumber = holeNum
        self.furthestHole = 0
        self.furthestDist = 0
        self.isMetric = True
        Hole.hole_index[holeNum].append(self)
    
    @classmethod
    def find_by_number(self, num):
        return Hole.hole_index.get(num)

    def rotate(self):
        #if self.holeZero == None:
            # throw Exception
        #    raise Exception("'Hole Zero not Set, Cannot Rotate")
        rotationAngle = self.rotationAngle
        # get angle from Hole Zero 
        
        zX, zY  = self.zeroedAndFlippedPoint

        currentAngle = math.atan2(zY, zX)
        angleinRadsToRotate = math.radians(rotationAngle) + currentAngle
        #dist = math.sqrt((zX)**2 + (zY)**2)
        #self.rotatedX = self._rotate(angleinRadsToRotate)
        self._rotate(angleinRadsToRotate)


    def _rotate(self, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.
        The angle should be given in radians.
        """
        px, py = self.zeroedAndFlippedPoint
        qx = math.cos(angle) * (px) - math.sin(angle) * (py)
        qy = math.sin(angle) * (px) + math.cos(angle) * (py)
        self.rotatedPoint = qx,qy
 
        
    def translateAndFlipHole(self, minY, maxY, minX):
        # move to X = 0 axis
        self.zeroedAndFlippedPoint[0] = self.filePoint[0] - minX
        # do the same for y  (minY )
        translatedY = self.filePoint[1] - minY
        # flip the Y point
        # first move the maxY to Y=0 axis 
        maxTranslatedY = maxY - minY
        self.zeroedAndFlippedPoint[1] = maxTranslatedY - translatedY


def FindMaxDistanceBetweenHoles(holes):
    #method variables 
    maxDistance = -999
    # placeholders for maxDistance holes - not sure how to define this 
    h0 = None
    h1 = None

    for loop_h0 in holes[:-1]:  # from zero to 2nd last hole 
        for loop_h1 in holes[1:]:   # from 2nd hole to end 
            #dist = math.sqrt( (h1.filePoint[0]-h2.filePoint[0])**2 + (h1.filePoint[1]-h2.filePoint[1])**2 )
            dist = CalculateDistanceBetweenHoles(loop_h0, loop_h1)
            if dist > maxDistance:
                maxDistance = dist
                h0 = loop_h0
                h1 = loop_h1
    logging.debug("Max Distance betwween holes Found : Holes are : %d and %d and the distance is %3.3f "% (h0.holeNumber, h1.holeNumber, maxDistance))
    #HACK: check to see which of the two holes has a smaller x value 
    # if so swop 
    #print("h0 x %3.3f      h1 x %3.3f  "% ( h0.zeroedAndFlippedPoint[0],h1.zeroedAndFlippedPoint[0] ))
    if(h0.zeroedAndFlippedPoint[0] > h1.zeroedAndFlippedPoint[0]):
        logging.info("swapping")
        tmp = h1
        h1 = h0
        h0 = tmp
        #print("h0 x %3.3f      h1 x %3.3f  "% ( h0.zeroedAndFlippedPoint[0],h1.zeroedAndFlippedPoint[0] ))

    return h0, h1, maxDistance

def CalculateDistanceBetweenHoles(h0, h1):
    return math.sqrt( (h0.filePoint[0]-h1.filePoint[0])**2 + (h0.filePoint[1]-h1.filePoint[1])**2 )


''' 
#NOTE: removed these as the hole class has methods for this anyway 

def rotateX(px, py, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    """
    #radAngle = math.radians(angle)
    
    qx = math.cos(angle) * (px) - math.sin(angle) * (py)
    return qx

def rotateY(px, py, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    """
    qy = math.sin(angle) * (px) + math.cos(angle) * (py)
    return qy

'''