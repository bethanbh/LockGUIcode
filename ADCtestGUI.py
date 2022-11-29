# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:47:42 2022

@author: mcwt12
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 10:03:12 2022

@author: mcwt12S
"""

import pyqtgraph
import sys
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

import pyqtgraph.dockarea as dockarea


#import plotgraphmultiplextest
#import plotgraphmultiplextestDELAYTEST
#import plotgraphmultiplextestCALIBRATE
#import plotgraphmultiplextestDELAYTESTthreechannel
import plotgraphADCtestsoftwareinterrupt

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

        
 
        #importing the file with all the functions etc in it
        #self.mainthings = plotgraphmultiplextest.PlotOutputs(self)
        #self.mainthings = plotgraphmultiplextestDELAYTEST.PlotOutputs(self)
        #self.mainthings = plotgraphmultiplextestCALIBRATE.PlotOutputs(self)
        #self.mainthings = plotgraphmultiplextestDELAYTESTthreechannel.PlotOutputs(self)
        self.mainthings = plotgraphADCtestsoftwareinterrupt.PlotOutputs(self)
        
        #GUI
        self.area = dockarea.DockArea()
        self.setCentralWidget(self.area)
        self.resize(1500,200)
        self.setWindowTitle('STCL Test GUI')
        self.setStyleSheet("background-color: ghostwhite;")
        self.createDocks()
        self.show()
        
        
        
    def createDocks(self):

        self.d1 = self.mainthings.d1 
        self.area.addDock(self.d1,'left')



    
        
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
        
        #this is to stop any data-taking loop when you close the window
        fen.mainthings.StopTracker()
        del fen

        print('Cheers')
    return ret
    #

if __name__ == '__main__':
    main()