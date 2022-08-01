# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 10:03:12 2022

@author: mcwt12
"""

import pyqtgraph
import sys
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph.dockarea as dockarea

import modifyvariables
import modifyandreadvariables
import readvariables
import upkeep
import readout
import serial

class schlagmuller_window(QtWidgets.QMainWindow):
    
    def __init__(self, parent = None):
        super(schlagmuller_window,self).__init__(parent)
        self.parentGui = parent
        self.initUI()

    def initUI(self):
        #AWG
        # self.ip_hostname='10.117.48.117'
        
        # self.pulser = PulseStreamer(self.ip_hostname)
        # respond = self.pulser.isStreaming()
        
#        setting the trigger mode
        # start = Start.HARDWARE_RISING
        # mode = Mode.NORMAL #retrigger enable
        # self.pulser.setTrigger(start=start, mode=mode)
        
                
        # self.seq = Sequence()

        
 
        #self.modify_variables = modifyvariables.Modify_variable(self)
        self.modifyandread_variables = modifyandreadvariables.ModifyandRead_variable(self)
        #self.read_variables = readvariables.Read_variable(self)
        self.general_things = upkeep.Upkeep(self)
        self.readout = readout.Readout(self)

        
        #GUI
        self.area = dockarea.DockArea()
        self.setCentralWidget(self.area)
        self.resize(1000,200)
        self.setWindowTitle('STCL Test GUI')
        self.setStyleSheet("background-color: ghostwhite;")
        self.createDocks()
        self.show()
        
        #testzone
        #self.general_things.Readfromarduino()
        #self.general_things.TalktoArduino()
        #self.readout.ExtractError()
        #self.modifyandread_variables.SaveParameters()
        
        
    def createDocks(self):
        
        self.d1 = self.modifyandread_variables.d1 #adding the modify variables bit (d1 is the actual window part)
        self.area.addDock(self.d1,'left')
        #self.d2 = self.read_variables.d1 #adding the read variables bit (d1 is the actual window part)
        #self.area.addDock(self.d2,'right', self.d1)
        self.d3 = self.general_things.d1 #adding the read variables bit (d1 is the actual window part)
        self.area.addDock(self.d3,'left', self.d1)
        self.d4 = self.readout.d1 #adding the read variables bit (d1 is the actual window part)
        self.area.addDock(self.d4,'right', self.d1)



    
        
def main():        
    
    app=QtGui.QApplication(sys.argv)
    fen=schlagmuller_window()
    
    try :
        ret = app.exec_()
    except Exception as err:
        print('Error occurred',type(err))
    finally :
        #We have to clear the tasks when we close the program
        #or we will have problems when we restart it (if the tasks are not cleared
        #the program won't be able to create them again at the beginning) 
        del fen
        print('Cheers')
    return ret

if __name__ == '__main__':
    main()