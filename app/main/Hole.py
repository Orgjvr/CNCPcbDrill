from collections import defaultdict
import math
import logging

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


def CalculateFurthestHoles(holes):
    for h1 in holes:
        for h2 in holes:
            dist = math.sqrt( (h1.filePoint[0]-h2.filePoint[0])**2 + (h1.filePoint[1]-h2.filePoint[1])**2 )
            if dist > h1.furthestDist:
                h1.furthestDist = dist
                h1.furthestHole = h2.holeNumber
        logging.debug("Val1="+str(h1.holeNumber)+" is furthest to "+str(h1.furthestHole) +" with distance: "+str(h1.furthestDist))    




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