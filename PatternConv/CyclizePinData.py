import sys, os

class CyclizePinData:
    def __init__(self,stream=sys.stdout):
        self.stream = stream
        self.Port2ISampleDict = {}
        self.Port2OSampleDict = {}
        self.defaultISample = 0
        self.defaultOSample = 0
        self.period = 0
        self.curCycleCount = 0
        self.perPinCurInput = {}
        self.perPinCurOut = {}
        self.perPinCurVal = {}
        self.perPinNextVal = {}
        self.cycleData = {}
        self.cycleList = []

    def after_datalog(self, dataSource):
        for indx, elm in enumerate(self.cycleList): 
            self.stream.write("Vector Cycle = " + str(elm) + "\n")
            for pinName in self.Port2ISampleDict.keys():
                if (elm,pinName) in self.cycleData.keys():
                    self.stream.write("Pin Name = " + str(pinName) + " Value = " + str(self.cycleData[(elm, pinName)]) + "\n")
        self.stream.flush()        
        
    def after_process(self, dataSource, data):
        print(" process simulation times = " + str(data[0]) + " for numOfCycle =" + str(data[1]))
        timeList = data[0]
        self.curCycleCount = data[1]
        numOfCycle = data[2]
        pinName2Indx = data[3]
        perPinSimValue = data[4]
        for pinName, pinIdx in pinName2Indx.items():
            if(pinName == "NAND_ADQ_5"):
                print("stop for debug")
            isInputValid = False
            isOutValid = False
            if not(pinName in self.Port2ISampleDict.keys()):
                self.Port2ISampleDict[pinName] = self.defaultISample
            if not(pinName in self.Port2OSampleDict.keys()):
                self.Port2OSampleDict[pinName] = self.defaultOSample                
            for timeIdx in timeList:
                if((timeIdx,pinIdx) in perPinSimValue.keys()):
                    self.perPinNextVal[pinName] = perPinSimValue[(timeIdx,pinIdx)]
                    if ((self.Port2ISampleDict[pinName] +self.curCycleCount*self.period) > timeIdx):
                        if(perPinSimValue[(timeIdx,pinIdx)] == '1' or perPinSimValue[(timeIdx,pinIdx)] == '0' or perPinSimValue[(timeIdx,pinIdx)] == 'Z'): 
                            self.perPinCurInput[pinName] = perPinSimValue[(timeIdx,pinIdx)]
                            isInputValid = True
                    if ((self.Port2OSampleDict[pinName]+self.curCycleCount*self.period) > timeIdx):
                        if(perPinSimValue[(timeIdx,pinIdx)] == 'L' or perPinSimValue[(timeIdx,pinIdx)] == 'H' or perPinSimValue[(timeIdx,pinIdx)] == 'X'): 
                            self.perPinCurOut[pinName] = perPinSimValue[(timeIdx,pinIdx)]
                            isOutValid = True                        
            if(isInputValid and isOutValid):
                if(self.Port2ISampleDict[pinName] >= self.Port2OSampleDict[pinName]):
                    self.perPinCurVal[pinName] = self.perPinCurOut[pinName] 
                else:
                    self.perPinCurVal[pinName] = self.perPinCurInput[pinName]    
            elif isInputValid:
                self.perPinCurVal[pinName] = self.perPinCurInput[pinName]    
            elif isOutValid:    
                self.perPinCurVal[pinName] = self.perPinCurOut[pinName] 
            else:
                if pinName in self.perPinNextVal.keys():
                    self.perPinCurVal[pinName] = self.perPinNextVal[pinName]
                else:
                    self.perPinCurVal[pinName] = 'X'
                    self.perPinNextVal[pinName] = 'X'                    
        # add the cyclized data 
        self.cycleList.append(self.curCycleCount)
        isCycleSplit = False
        for pinName in self.perPinCurVal.keys():
            self.cycleData[(self.curCycleCount,pinName)] = self.perPinCurVal[pinName]
            if(self.perPinCurVal[pinName] != self.perPinNextVal[pinName]):
                isCycleSplit = True
        if isCycleSplit and numOfCycle >1:
            self.cycleList.append(self.curCycleCount + 1)
            for pinName in self.perPinNextVal.keys():
                self.cycleData[(self.curCycleCount + 1,pinName)] = self.perPinNextVal[pinName]
                self.perPinCurVal[pinName] = self.perPinNextVal[pinName]
                    
        self.curCycleCount = self.curCycleCount + numOfCycle


    def InitPinTiming(self,defaultISample,defaultOSample):
        self.defaultISample = defaultISample
        self.defaultOSample = defaultOSample

    def SetPinTiming(self,pinName,ISampleStrb,OSampleStrb):
        self.Port2ISampleDict[pinName] = ISampleStrb
        self.Port2OSampleDict[pinName] = OSampleStrb

    def setCyclePeriod(self, cyclePeriod):
        self.period = cyclePeriod