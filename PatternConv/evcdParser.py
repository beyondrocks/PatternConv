#
# eVCDParser - python to parse EVCD
#
#
import sys
import struct
import re


from PatternConv.Types import *
from PatternConv import evcdType

from PatternConv.DataSource import DataSource


class Parser(DataSource):

  def sendData(self, header, data):
    if (header.typ, header.sub) in self.recordMap:
        recType = self.recordMap[(header.typ, header.sub)]
        fields = data
        if len(fields) < len(recType.columnNames):
            fields += [None] * (len(recType.columnNames) - len(fields))
        self.send((recType, fields))      

  def readline(self):
    self.curline = self.inp.readline()
    if len(self.curline) == 0:
        self.eof = 1
        return True
    header = RecordHeader()
    # check for time scale token
    tokenFound = re.search(r'^\$(date|version|timescale|end|enddefinitions|dumpports|comment)\s*(.*)',self.curline)
    timescaleFound = re.search(r'(\d+)\s*(ps|ns|fs|ms|us|s)', self.curline)
    portFound = re.search(r'\$var\s*port\s*(\S*)\s*\<\s*(\d*)\s*(\w*)\s*\$end',self.curline)
    stimulusFound =  re.search(r'p(\w+)\s+\d+\s+\d+\s+<(\d+)',self.curline)
    noemptyFound = re.search(r'\s*(\S+\s*.*)',self.curline)
    if tokenFound:
        header.typ = 0
        header.sub = 70
        self.sendData(header,[tokenFound.group(1),tokenFound.group(2)])
    elif timescaleFound:
        header.typ = 0
        header.sub = 30
        self.sendData(header,[timescaleFound.group(2),timescaleFound.group(1)])
    elif portFound:
        tmpPortName = portFound.group(3)
        tmpPortID = portFound.group(2)
        portIndx = portFound.group(1)
        busPortFound = re.search(r'\s*\[\s*(\d*)\s*:\s*(\d*)\s*\]',portIndx)
        pinFound = re.search(r'\s*(\d*)\s*',portIndx)
        if busPortFound:
            tmpMSB = int(busPortFound.group(1))
            tmpLSB = int(busPortFound.group(2))
            tmpPortSize = abs(tmpPortInfo.MSB - tmpPortInfo.LSB + 1)
        else:
            if pinFound:
                tmpPortSize =int(pinFound.group(1))
        header.typ = 0
        header.sub = 40
        self.sendData(header,[tmpPortSize,tmpPortID,tmpPortName])
    elif self.curline.startswith("#") and self.curline[1:].strip().isdigit():
        stimCurTime = int(self.curline[1:].strip())
        header.typ = 0
        header.sub = 50
        self.sendData(header,[stimCurTime])    
    elif stimulusFound:
        header.typ = 0
        header.sub = 60
        self.sendData(header,[stimulusFound.group(2),stimulusFound.group(1)]) 
    elif noemptyFound:
        header.typ = 0
        header.sub = 80 
        self.sendData(header,[noemptyFound.group(1)])        


  def parse_records(self, count=0):
    i = 0
    self.eof = 0
    fields = None
    try:
      while self.eof == 0:
        self.readline()
        if count:
          i += 1
          if i >= count: break
    except EofException: pass


  def parse(self, count=0):
    self.begin()
    try:
      self.parse_records(count)
      self.complete()
    except Exception as exception:
      self.cancel(exception)
      raise


  def __init__(self, recTypes=evcdType.records, inp=sys.stdin):
    DataSource.__init__(self, ['header']);
    self.eof = 1
    self.recTypes = set(recTypes)
    self.inp = inp

    self.recordMap = dict(
      [ ((recType.typ, recType.sub), recType)
        for recType in recTypes ])