# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import sys

from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QPushButton,
    QWidget,
)

import pyqtgraph
import sys
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets


##import modifyvariables
#import modifyandreadvariables
#import readvariables
import upkeep
#import readout
import serial
import bigcombofile

class schlagmuller_window(QWidget):
    def __init__(self, parent = None):
        super(schlagmuller_window,self).__init__(parent)
        self.parentGui = parent
        
        
        self.setWindowTitle("QGridLayout Example")
        # Create a QGridLayout instance
        layout = QGridLayout()
        # Add widgets to the layout
        layout.addWidget(QPushButton("Button at (0, 0)"), 0, 0)
        layout.addWidget(QPushButton("Button at (0, 1)"), 0, 1)
        layout.addWidget(QPushButton("Button at (0, 2)"), 0, 2)
        layout.addWidget(QPushButton("Button at (1, 0)"), 1, 0)
        layout.addWidget(QPushButton("Button at (1, 1)"), 1, 1)
        layout.addWidget(QPushButton("Button at (1, 2)"), 1, 2)
        layout.addWidget(QPushButton("Button at (2, 0)"), 2, 0)
        layout.addWidget(QPushButton("Button at (2, 1)"), 2, 1)
        layout.addWidget(QPushButton("Button at (2, 2)"), 2, 2)
        # Set the layout on the application's window
        self.setLayout(layout)
        self.show()
        

def main():        
    
    app=QtGui.QApplication(sys.argv)
    fen=schlagmuller_window()
    #fen.show()
    
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
