import sys, os
from PatternConv.Types import *
from PatternConv import evcdType
from PatternConv.DataSource import DataSource

class PinDataWriter(DataSource):
    def __init__(self,stream=sys.stdout):
        self.stream = stream
        self.generalRecord = {}
        self.endToken = 0 
        self.dateToken = 0
        self.versionToken = 0
        self.timeScaleToken = 0
        self.headerEndToken = 0
        self.dumpPortToken = 0   
        self.commentToken = 0 
        self.pinIndx2NameMap = {}
        self.pinName2IndxMap = {}
        self.curSimTime = 0
        self.simTimeList = []
        self.perPinSimValue= {}
        self.comments = {}
        self.period = 0
        self.curCycleCount = 0
        self.cycleLowBound = 0
        DataSource.__init__(self, []);

    def after_send(self, dataSource, data):
        self.analyze_Records(self,data)
        

    def after_complete(self, dataSource):
        #self.logPinData(self)
        self.datalog()

    @staticmethod
    def analyze_Records(self,data):
        rectype = data[0]
        if rectype is evcdType.token:
            # get FAR record
            self.getRecord(self,data)
        elif rectype is evcdType.timescale and self.timeScaleToken == 1:
            # get lot test result
            self.getTimeScale(self,data)
        elif rectype is evcdType.pinIndex:
            # get lot test result
            self.getPinIndex(self,data)
        elif rectype is evcdType.timeAnchor:
            # get PIR data
            self.getTimeAnchor(self,data)        
        elif rectype is evcdType.pinValue:
            # get PIR data
            self.getPinValue(self,data)   
        elif rectype is evcdType.content:
            # get PIR data
            self.getContent(self,data)   
            
    @staticmethod             
    def getRecord(self,data):
        rectype = data[0]
        dictVar = {}
        for idx, val in enumerate(data[1]):
            dictVar[rectype.fieldNames[idx]] = val
        if dictVar['Name'] == "date":
            self.dateToken = 1
        if dictVar['Name'] == "version":
            self.versionToken = 1         
        if dictVar['Name'] == "timescale":
            self.timeScaleToken = 1    
        if dictVar['Name'] == "enddefinitions":
            self.headerEndToken = 1    
        if dictVar['Name'] == "dumpports":
            self.dumpPortToken = 1   
        if dictVar['Name'] == "comment":
            self.commentToken = 1 
        if dictVar['Name'] == "end":
            self.endToken = 1 
            self.dateToken = 0
            self.versionToken = 0
            self.timeScaleToken = 0
            self.headerEndToken = 0
            self.dumpPortToken = 0   
            self.commentToken = 0             

    def __unitConv(self,unit,scale):
        if unit == "fs":
            tmpScale = 1e-6*float(scale)
        elif unit == "ps":
            tmpScale = 1e-3*float(scale)
        elif unit == "ns":
            tmpScale = 1*float(scale)
        elif unit == "us":
            tmpScale = 1e3*float(scale)
        elif unit == "ms":
            tmpScale = 1e6*float(scale)
        elif unit == "s":
            tmpScale = 1e9*float(scale)
        else:
            tmpScale = 1*float(scale)
        return tmpScale

                                                                                   
    @staticmethod
    def getTimeScale(self,data):
        rectype = data[0]
        for idx, val in enumerate(data[1]):
            if(rectype.fieldNames[idx] == 'Unit'):
                self.timeUnit = str(val)
            elif (rectype.fieldNames[idx] == 'Scale'):
                self.timeScale = val
        self.timeScale = self.__unitConv(self.timeUnit, self.timeScale)

        
    @staticmethod
    def getPinIndex(self,data):
        rectype = data[0]
        for idx, val in enumerate(data[1]):
            if(rectype.fieldNames[idx] == 'Size' ):
                size = val
            elif rectype.fieldNames[idx] == 'Index':
                indx = val
            elif rectype.fieldNames[idx] == 'PinName':
                pinName = str(val)   
        self.pinIndx2NameMap[indx] =  pinName
        self.pinName2IndxMap[pinName]= indx
  

    @staticmethod        
    def getTimeAnchor(self,data):

        rectype = data[0]
        for idx, val in enumerate(data[1]):
            if(rectype.fieldNames[idx] == 'Time' ):
                timeslice = float(val)
        self.curSimTime = timeslice * self.timeScale
        if(self.curSimTime in self.simTimeList) :
            print("simulation time already exist. Simulation time is " + str(self.curSimTime))
        else: 
            if(self.curSimTime >= ((self.curCycleCount+1) * self.period)):
                numOfCycle = (self.curSimTime // self.period) - self.curCycleCount
                print("find cycle boundary at " + str(self.curSimTime) + " . Do cycling for cycle =" + str(self.curCycleCount) + " . NumOfCycle = " + str(numOfCycle))
                analydata = [self.simTimeList[self.cycleLowBound:],self.curCycleCount,numOfCycle, self.pinName2IndxMap, self.perPinSimValue] 
                self.process(analydata)
                self.cycleLowBound = len(self.simTimeList)
                self.curCycleCount = (self.curSimTime // self.period)
            self.simTimeList.append(self.curSimTime)

    @staticmethod
    def getPinValue(self,data):
        rectype = data[0]
        for idx, val in enumerate(data[1]):
            if(rectype.fieldNames[idx] == 'PinIndex' ):
                indx = val
            elif(rectype.fieldNames[idx] == 'StateChar' ):
                statechar = str(val)
        self.perPinSimValue[(self.curSimTime,indx)]= stateMap[statechar]

    @staticmethod        
    def getContent(self,data):
        rectype = data[0]
        for idx, val in enumerate(data[1]):
            if(rectype.fieldNames[idx] == 'Value' ):
                contentVal = val
        if self.dateToken == 1:
            self.generalRecord['date']= contentVal
        elif self.versionToken == 1:
            self.generalRecord['version']= contentVal 
        elif self.commentToken == 1:
            if(self.curSimTime in self.comments.keys()):
               self.comments[self.curSimTime]=self.comments[self.curSimTime] + "\n" + contentVal
            else:
               self.comments[self.curSimTime]= contentVal
    @staticmethod
    def logPinData(self):
        # print collected eVCD date 
        for indx, elm in enumerate(self.simTimeList): 
            self.stream.write("Simulation slice time = " + str(elm) + "\n")
            if elm in self.comments.keys():
                self.stream.write("Comment = " + str(self.comments[elm]) + "\n")
            for pinIdx, pinName in self.pinIndx2NameMap.items():
                if (elm, pinIdx) in self.perPinSimValue.keys():
                    self.stream.write("Pin Name = " + str(pinName) + " Value = " + str(self.perPinSimValue[(elm, pinIdx)]) + "\n")
   
        self.stream.flush()

    def setCyclePeriod(self, cyclePeriod):
        self.period = cyclePeriod
        