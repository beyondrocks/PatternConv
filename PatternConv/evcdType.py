import sys
from PatternConv.Types import RecordMeta, RecordType, stdfToLogicalType
from PatternConv import TableTemplate
import pdb

class Timescale(RecordType, metaclass=RecordMeta):
  """
  **EVCD Time Scale**
  format is as below : 
  ======== === ================================== ============
    $timescale
     1 ps
    $end
  ======== ==== ================================= =============
  Location:
    Required as the first record of the file.
  """
  typ = 0
  sub = 30
  fieldMap = (
    ('Unit', 'Cn'),
    ('Scale', 'U8')    
  )

class PinIndex(RecordType, metaclass=RecordMeta):
  """
  **EVCD Pin Index definition**
  format is as below : 
  ======== === ================================== ============
    $var port 1 <1 PWRGOOD1 $end
  ======== ==== ================================= =============
  Location:
    Required as the first record of the file.
  """
  typ = 0
  sub = 40
  fieldMap = (
    ('Size', 'U8'),
    ('Index', 'U8'), 
    ('PinName', 'Cn')      
  )
class TimeAnchor(RecordType, metaclass=RecordMeta):
  """
  **EVCD current time Anchor definition**
  format is as below : 
  ======== === ================================== ============
    #13000
  ======== ==== ================================= =============
  Location:
    Required as the first record of the file.
  """
  typ = 0
  sub = 50
  fieldMap = (
      ('Time', 'U8'),
      ('Dummy','Cn') 
    )


class PinValue(RecordType, metaclass=RecordMeta):
  """
  **EVCD current pin driver/compare **
  format is as below : 
  ======== === ================================== ============
   pZ 0 0 <247
  ======== ==== ================================= =============
  Location:
    Required as the first record of the file.
  """
  typ = 0
  sub = 60
  fieldMap = (
    ('PinIndex', 'U8'),
    ('StateChar', 'C1')         
  )
  
class Token(RecordType, metaclass=RecordMeta):
  """
  **EVCD tokens like $date, $version, $timescale, $enddefinitions,$dumpports,$comment, $end **
  """
  typ = 0
  sub = 70
  fieldMap = (
    ('Name', 'Cn'),
    ('Value', 'Cn') 
  )
class Content(RecordType, metaclass=RecordMeta):
  """
  **EVCD general no-empty line**
  """
  typ = 0
  sub = 80
  fieldMap =  (
       ('Value', 'Cn'),
        ('Dummy','Cn') 
    )
    
timescale = Timescale()
pinIndex = PinIndex()
timeAnchor = TimeAnchor()
pinValue = PinValue()
token = Token()
content = Content()

records = (
#   timestamp,
#   version,
  timescale,
  pinIndex,
  timeAnchor,
  pinValue,
  token,
  content
)
