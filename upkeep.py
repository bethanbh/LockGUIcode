# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 12:43:00 2022

@author: mcwt12
"""


import matplotlib.pyplot as plt
import sys

import numpy as np
import os
import importlib
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.dockarea as dockarea
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import time
import serial
import serial.tools.list_ports

from PyQt5.QtGui import QFont



USUAL_DIR = os.getcwd()


class Upkeep(QtGui.QMainWindow):

    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self.parentGui = parent
        self.sampling_rate = 250
        self.initUI()

    def initUI(self):
        #AWG
        self.cavPgain = 1
        self.cavIgain = 2
        self.laserPgain = 3
        self.laserIgain = 4
        self.laserDgain = 5
        self.laserfreqsetpoint = 6
        self.cavoffsetpoint = 7
        self.highthreshold = 8
        self.lowthreshold = 9
        self.examplefilename = USUAL_DIR
        
        self.list_comports = []
        #self.t_max = 1000
        #self.time_resolution = 1
        #self.table_pulses = np.zeros((8,self.t_max))
#        self.P_normed = []
#        self.P_normed_eff = []
        #self.time_list = [] 
        #self.time_edge_array = []
        #self.widget_per_channel = []
        #self.layout_per_channel = []
        #self.nb_pulses_list = [1,1,1,1,1,1,1,1]
        #self.label_channel_list = ['A','B','C','D','E','F','G','H']

        
        #self.lock_thread = LockThread(self)
        # self.connect(self.lock_thread,QtCore.SIGNAL("finished()"),self.done)
        #self.lock_thread.new_value_signal.connect(self.new_value_loop)
        #self.perform_lock = False

        
        #GUI
        self.area = dockarea.DockArea()
        self.setCentralWidget(self.area)
        self.resize(100,100)
        self.setWindowTitle('Adiabatic')
        self.createDocks()
        
    def createDocks(self):
            self.d1 = dockarea.Dock("AWG", size=(300,200))
            self.d1.hideTitleBar()
            
            
            self.area.addDock(self.d1, 'left')
            
            #######################################################################
            ## w1: Choose COM port
            #######################################################################
    
            self.w1 = pg.LayoutWidget()
            self.label_comport = QtGui.QLabel('COM port')
            self.label_comport.setFont(QFont('Helvetica', 10))
            self.label_comport.setStyleSheet(':hover { background: lightpink }') #this is just set to change colour when hovered over for now, but ideally goes green if the COM port you've selected is all good
    
            self.label_comport.setAlignment(QtCore.Qt.AlignLeft)
            
            self.parameter_loop_comboBox = QtGui.QComboBox() 
            #finding all the available COM ports and adding their names to the drop down menu
            list_serialports = serial.tools.list_ports.comports()
            for n in range(len(list_serialports)):
                test = list_serialports[n][0]
                self.parameter_loop_comboBox.addItem(str(test)) 
        
            
            self.w1.addWidget(self.label_comport, row=0, col=0,colspan = 1)
            self.w1.addWidget(self.parameter_loop_comboBox, row = 0, col = 1,colspan = 1)  
      
        
            #######################################################################
            ## w2: stop button? (not sure whether I'll need this)
            #######################################################################
            # aim is for this one to stop the connection to the arduino, basically stop the program running without fully closing the window
      
            self.w2 = pg.LayoutWidget()
            self.stop_btn = QtGui.QPushButton('Stop')
            self.stop_btn.setStyleSheet(':hover { background: red }')   
            
            self.w2.addWidget(self.stop_btn, row=0, col=0)
            
            #######################################################################
            ## w3: lock button
            #######################################################################

            self.w3 = pg.LayoutWidget()
            self.lock_btn = QtGui.QPushButton('Lock')
            self.lock_btn.setStyleSheet(':closed { background: green , border:none}')   
            self.save_values_checkbox = QtGui.QCheckBox("Save?")
            
            self.w3.addWidget(self.lock_btn, row=0, col=0)
            self.w3.addWidget(self.save_values_checkbox, row=0, col=1)
            
            #######################################################################
            ## w5: saving things
            #######################################################################
    
            self.w5 = pg.LayoutWidget()
            self.label_filename = QtGui.QLabel('Filename')
            self.label_filename.setFont(QFont('Helvetica', 10))
    
            self.label_filename.setAlignment(QtCore.Qt.AlignLeft)
            self.filenameLE = QtGui.QLineEdit(str(self.examplefilename))
 
            
            self.w5.addWidget(self.label_filename, row=0, col=0,colspan = 1)
            self.w5.addWidget(self.filenameLE, row = 0, col = 1,colspan = 2)  
      
            
            
            #######################################################################
            ## w4: error info
            #######################################################################
      
            self.w4 = pg.LayoutWidget()
            self.label_error = QtGui.QLabel('Error details')
            self.label_error.setFont(QFont('Helvetica', 10))
            self.status = QtGui.QLabel('Status?')
            self.status.setStyleSheet(':hover { background: red }') #ideally will want this to go red if bad stuff is happening
            self.errordetails = QtGui.QLabel('Error details would go here')
            self.errordetails.setStyleSheet('border: 1px solid black')
         
            self.w4.addWidget(self.label_error, row=0, col=0, colspan=1)
            self.w4.addWidget(self.status, row=0, col=2)
            self.w4.addWidget(self.errordetails, row=1, col=0, rowspan= 40, colspan=2)
        
      
            self.d1.addWidget(self.w1, row=0, col=0)
            self.d1.addWidget(self.w2, row=1, col=0)
            self.d1.addWidget(self.w3, row=2, col=0)
            self.d1.addWidget(self.w4, row=4, col=0)
            self.d1.addWidget(self.w5, row=3, col=0)
            
    def Readfromarduino(self):
        comport = self.parameter_loop_comboBox.currentText()
        print(f' The selected COM port is: {comport}') #okay, so this does print out the COM port okay! (tested in testzone in STCLGUI page)
               #arduino = serial.Serial('COM1', self.baudrate, timeout=.1)
#while True:
#	data = arduino.readline()[:-2] #the last bit gets rid of the new-line chars
#	if data:
#		print data
    

    #def SaveParameters(self):
        #This should read the parameters from the 

    

      

