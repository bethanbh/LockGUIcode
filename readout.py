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

import upkeep

from PyQt5.QtGui import QFont


''' 
This bit will have a button that should read all the stored variables from the arduino, and present them '''

class Readout(QtGui.QMainWindow):

    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self.parentGui = parent
        self.sampling_rate = 250
        self.initUI()

    def initUI(self):
        #AWG
        self.examplefilename = 'example filename'
        self.peak1pos = 100
        self.peak2pos = 200
        self.peak3pos = 300
        self.currentlasererror = 23
        self.currentcaverror = 34
        
        self.baudrate = 230400
        self.general_things = upkeep.Upkeep(self)
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
            ## w1: peak positions
            #######################################################################
            self.w1 = pg.LayoutWidget()
            
            self.read_peakpos_btn = QtGui.QPushButton('Peaks?')
            self.read_peakpos_btn.clicked.connect(self.WhenPeakPosBtnPressed)
            self.read_peakpos_btn.setStyleSheet(':hover { background: powderblue }')
            self.unit_swapcheckbox = QtGui.QCheckBox('ms?')
            
            self.peak1pos_label = QtGui.QLabel('Peak 1')
            self.peak2pos_label = QtGui.QLabel('Peak 2')
            self.peak3pos_label = QtGui.QLabel('Peak 3')
            
            self.peak1posvalue = QtGui.QLabel(str(self.peak1pos))
            self.peak2posvalue = QtGui.QLabel(str(self.peak2pos))
            self.peak3posvalue = QtGui.QLabel(str(self.peak3pos))
            self.peak1posvalue.setAlignment(QtCore.Qt.AlignCenter)
            self.peak2posvalue.setAlignment(QtCore.Qt.AlignCenter)
            self.peak3posvalue.setAlignment(QtCore.Qt.AlignCenter)

            self.w1.addWidget(self.read_peakpos_btn, row=0, col=0)
            self.w1.addWidget(self.unit_swapcheckbox, row=1, col=0)
            self.w1.addWidget(self.peak1pos_label, row=0, col=1)
            self.w1.addWidget(self.peak2pos_label, row=0, col=2)
            self.w1.addWidget(self.peak3pos_label, row=0, col=3)
            self.w1.addWidget(self.peak1posvalue, row=1, col=1)
            self.w1.addWidget(self.peak2posvalue, row=1, col=2)
            self.w1.addWidget(self.peak3posvalue, row=1, col=3)

            #######################################################################
            ## w2:graph of peak positions
            #######################################################################
            # aim is for this one to stop the connection to the arduino, basically stop the program running without fully closing the window
      
            self.w2 = pg.LayoutWidget()

            self.fig_peakpos = plt.figure(facecolor='white', frameon = True, figsize=(8,2))
            self.canvas_peakpos = FigureCanvas(self.fig_peakpos)
    #        self.ax_pulses = self.fig_pulses.add_subplot(1,1,1)
    #
    #        self.ax_pulses.plot(10,10,s=200,c='g',alpha=.8)

            self.w2.addWidget(self.canvas_peakpos, row=0, col=0)
            
            #######################################################################
            ## w2: graph of peak pos over time 
            #######################################################################
            self.w3 = pg.LayoutWidget()
            
            self.fig_peakposovertime = plt.figure(facecolor='white', frameon = True)
            self.canvas_peakposovertime = FigureCanvas(self.fig_peakposovertime)
  
            
            self.w3.addWidget(self.canvas_peakposovertime, row=0, col=0)
            
            #######################################################################
            ## w2: error info
            #######################################################################
      
            self.w4 = pg.LayoutWidget()
            self.read_errors_pushbtn = QtGui.QPushButton('Error?')
            self.read_errors_pushbtn.clicked.connect(self.WhenErrorbtnPress)
            self.read_errors_pushbtn.setStyleSheet(':hover { background: palegreen }')
            self.laser_error_label = QtGui.QLabel('Laser error')
            self.laser_error = QtGui.QLabel('1')
            #self.label_error.setFont(QFont('Helvetica', 10))
            self.cav_error_label = QtGui.QLabel('Cavity error')
            self.cav_error = QtGui.QLabel('2')

         
            self.w4.addWidget(self.read_errors_pushbtn, row=0, col=0, colspan=1)
            self.w4.addWidget(self.laser_error_label, row=0, col=1)
            self.w4.addWidget(self.laser_error, row=0, col=2)
            self.w4.addWidget(self.cav_error_label, row=0, col=3)
            self.w4.addWidget(self.cav_error, row=0, col=4)
        
      
            self.d1.addWidget(self.w1, row=0, col=0)
            self.d1.addWidget(self.w2, row=1, col=0)
            self.d1.addWidget(self.w3, row=2, col=0)
            self.d1.addWidget(self.w4, row=3, col=0)
            
            
            
            
    def ExtractPeakPos(self):
        #TALKING TO THE ARDUINO, UPDATE VALUES IN PYTHON CODE
        #choose the COM port to set up for serial communication using the drop down menu
        comport = self.general_things.parameter_loop_comboBox.currentText()

        try:
            arduino = serial.Serial(comport, self.baudrate, timeout=.1)#should hopefully open the serial communication?
            print('COM port open in talking')
            
            #set peak 1
            arduino.write(str.encode('pf!'))
            peak1pos = arduino.readline()
            self.peak1pos = peak1pos.decode()
            
            #set peak 2
            arduino.write(str.encode('pg!'))
            peak2pos = arduino.readline()
            self.peak2pos = peak2pos.decode()
            
            #set peak 3
            arduino.write(str.encode('ph!'))
            peak3pos = arduino.readline()
            self.peak3pos = peak3pos.decode()
            
            arduino.close()
            print('port closed in talking')
        except (OSError, serial.SerialException):
            print('whoops the arduino is not there')  
            
    
    def WhenPeakPosBtnPressed(self):
        #talk to the arduino
        self.ExtractPeakPos()
        #update the labels here- taking care to use the selected units
        if self.unit_swapcheckbox.isChecked(): #ie if we want ms
            newunitpeak1pos = float(self.peak1pos)/(84*1000000*10**-3)
            newunitpeak2pos = float(self.peak2pos)/(84*1000000*10**-3)
            newunitpeak3pos = float(self.peak3pos)/(84*1000000*10**-3)
            self.peak1posvalue.setText(str(round(newunitpeak1pos,3)))
            self.peak2posvalue.setText(str(round(newunitpeak2pos,3)))
            self.peak3posvalue.setText(str(round(newunitpeak3pos,3)))
        else: #just the random numbers the arduino spits out
            self.peak1posvalue.setText(str(round(float(self.peak1pos),3)))
            self.peak2posvalue.setText(str(round(float(self.peak2pos),3)))
            self.peak3posvalue.setText(str(round(float(self.peak3pos),3)))
            
    def ExtractError(self):
        #choose the COM port to set up for serial communication using the drop down menu
        comport = self.general_things.parameter_loop_comboBox.currentText()

        try:
            arduino = serial.Serial(comport, self.baudrate, timeout=.1)#should hopefully open the serial communication?
            print('COM port open in talking')
            
            #get laser error
            arduino.write(str.encode('pl!'))
            currentlasererror = arduino.readline()
            self.currentlasererror = currentlasererror.decode()
        
            
            #get cavity error
            arduino.write(str.encode('pm!'))
            currentcaverror = arduino.readline()
            self.currentcaverror = currentcaverror.decode()
            
            arduino.close()
            print('port closed in talking')
        except (OSError, serial.SerialException):
            print('whoops the arduino is not there')  
            
            
    def WhenErrorbtnPress(self):
        #talk to arduino and get the values out
        self.ExtractError()
        #update the display
        self.laser_error.setText(str(self.currentlasererror))
        self.cav_error.setText(str(self.currentcaverror))
        
        
        
            
        
            