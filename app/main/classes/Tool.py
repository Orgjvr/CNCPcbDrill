from collections import defaultdict
import math
import logging

class Tool:

    tool_index = defaultdict(list)

    def __init__(self, toolNum, size, holeCount):
        self.toolNum = toolNum
        self.size = float(size)
        self.holeCount = int(holeCount)
        Tool.tool_index[toolNum].append(self)
    
    @classmethod
    def find_by_number(self, num):
        #return Tool.tool_index.get(num)
        for t in Tool.tool_index:
            if (t.toolNum == num):
                return t


    #@classmethod
    #def addHole(self, toolNum):
    #    print("toolNum=<"+str(toolNum)+">")
    #    print("toolHoleCnt=<"+str(Tool.tool_index[toolNum].holeCount)+">")
    #    Tool.tool_index[toolNum].holeCount += 1

def PrintTools(tools):
    for t in tools:
        print("toolNum=<"+str(t.toolNum)+"> size=<"+str(t.size) +"> holeCount=<"+str(t.holeCount)+">")    

