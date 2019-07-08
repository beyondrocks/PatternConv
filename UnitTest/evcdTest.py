import sys, os

sys.path.append("..")
from PatternConv.PinDataWriter import PinDataWriter
from PatternConv.evcdParser import Parser
from PatternConv.CyclizePinData import CyclizePinData

def toExcel(fname,tables):
    """ Export the tables from toTables to Excel
    """
    writer = pd.ExcelWriter(fname)
    for k,v in tables.items():
        # Make sure the order of columns complies the specs
        record = [r for r in V4.records if r.__class__.__name__.upper()==k]
        if len(record)==0:
            print("Ignore exporting table %s: No such record type exists." %k)
        else:
            columns = [field[0] for field in record[0].fieldMap]
            v.to_excel(writer,sheet_name=k,columns=columns,index=False,na_rep="N/A")
    writer.save()


if __name__ == '__main__':
    fin = "C:\\Users\\tli56\\PycharmProjects\\DataAnalysis\\UnitTest\\debug_evcd_reduce.evcd"
    f = open(fin, 'r')
    fout = open(fin+"_out.txt", 'w')
    p = Parser(inp =f)
    pinDataWrIns = PinDataWriter()
    cyclizeIns = CyclizePinData(stream = fout)
    cyclizeIns.InitPinTiming(13.0, 11.7)
    cyclizeIns.SetPinTiming("TCK_SWDCLK",19.5, 11.7)
    cyclizeIns.SetPinTiming("CELL_CLK",19.5, 11.7)
    cyclizeIns.SetPinTiming("RP_I2C_SCL",19.5, 11.7)
    cyclizeIns.SetPinTiming("HW_MON2",19.5, 11.7)
    cyclizeIns.SetPinTiming("PCI_REFCLK_N",19.5, 11.7)
    cyclizeIns.SetPinTiming("PCI_REFCLK_P",6.5, 11.7)
    cyclizeIns.SetPinTiming("MIPI_PTI_CLK",0, 11.7)
    cyclizeIns.SetPinTiming("MIPI_PTI_DATA1",0, 11.7)
    cyclizeIns.SetPinTiming("HW_MON1",19.5, 11.7)
    cyclizeIns.SetPinTiming("TDO",19.5, 13.0)
    cyclizeIns.SetPinTiming("NAND_ADQ_5",19.5, 13.0)
    cyclizeIns.SetPinTiming("MIPI_PTI_DATA1",19.5, 1.0)  
    cyclizeIns.setCyclePeriod(cyclePeriod=26.0)  
    pinDataWrIns.setCyclePeriod(cyclePeriod=26.0)
    pinDataWrIns.addSink(cyclizeIns)
    p.addSink(pinDataWrIns)
    p.parse()
    print("process done now!!!!! \n")
