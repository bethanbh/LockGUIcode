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
import random
import modifyandreadvariables

from PyQt5.QtGui import QFont


''' 
This bit will have a button that should read all the stored variables from the arduino, and present them '''


#thinking about threading
class PeakPosTrackerThread(QtCore.QObject):
    #signals here- so like a finished one? there's also a progress one?
    updated = QtCore.pyqtSignal(list)
    #time = QtCore.pyqtSignal(float)
    
    def __init__(self, ctrl):
        QtCore.QThread.__init__(self)
        #ExpControl window is the parent
        #self.parent = parent
        #self.memory = '2.0'
        self.ctrl = ctrl
        self.general_things = upkeep.Upkeep(self)
        comport = self.general_things.parameter_loop_comboBox.currentText()
        self.arduino = serial.Serial(comport, 230400, timeout=.1)#should hopefully open the serial communication?
        
    
    def TASK(self):
        self.ctrl['break'] = False
    #long running task- ie want to talk to the arduino and update the peak positions
    #maybe everytime the peak positions are updated, it sends a signal which triggers the plotting function?
    #not sure whether this is gonna be worth it but there we go
        #comport = self.general_things.parameter_loop_comboBox.currentText()
        
        try:
            #arduino = serial.Serial(comport, 230400, timeout=.1)#should hopefully open the serial communication?
            print('COM port open in talking')
            
            starttime = time.time()
            
            while time.time()< (starttime+30): #want this bit to actually be about whether the peak button is pressed and cycle thing on
                print("tick")
                #arduino = serial.Serial(comport, 230400, timeout=.1)#should hopefully open the serial communication?
                
                #set peak 1
                self.arduino.write(str.encode('pf!'))
                peak1pos = self.arduino.readline()
                #self.peak1pos = peak1pos.decode()
                
                #set peak 2
                self.arduino.write(str.encode('pg!'))
                peak2pos = self.arduino.readline()
                #self.peak2pos = peak2pos.decode()
                
                #set peak 3
                self.arduino.write(str.encode('ph!'))
                peak3pos = self.arduino.readline()
                #self.peak3pos = peak3pos.decode()
                print([peak1pos.decode(), peak2pos.decode(), peak3pos.decode(), time.time()])
                self.updated.emit([peak1pos.decode(), peak2pos.decode(), peak3pos.decode(), time.time()]) #emit a signal to say it's been updated!
                #self.updated.emit(time.time())
                
                time.sleep(1 - ((time.time() - starttime) % 1))
                
                if self.ctrl['break']:
                    print('we sleeping')
                    #self.testsignal.connect(self.SENDMESSAGE)
                    #arduino.close()
                    #time.sleep(3)
                    message = 'm' + 'a' + self.ctrl['value'] + '!' #encode given data into a message the arduino can understand
                    #print(f'message is {message}')
                    try:
                        self.arduino.write(str.encode(message)) #send this message to the arduino, activates the message_parser function
                        print(f'yep we wrote a message: {message}')
                        #print('port closed in talking')
                    except (OSError, serial.SerialException):
                        print('whoops the arduino is not there test edition')
                    
                    self.ctrl['break'] = False
                    #arduino = serial.Serial(comport, 230400, timeout=.1)#should hopefully open the serial communication?
                    
                #want to emit signal that will say oh we've updated
            
            self.arduino.close()
            print('port closed in talking')
        except (OSError, serial.SerialException):
            print('LOOP version whoops the arduino is not there') 


    '''def SENDMESSAGE(self, value):
        message = 'm' + 'a' + str(value) + '!' #encode given data into a message the arduino can understand
        #print(f'message is {message}')
        try:
            self.arduino.write(str.encode(message)) #send this message to the arduino, activates the message_parser function
            print('yep we wrote a message')
            #print('port closed in talking')
        except (OSError, serial.SerialException):
            print('whoops the arduino is not there test edition')'''

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
        self.modifyvariables = modifyandreadvariables.ModifyandRead_variable(self)
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

        self.testsignal = QtCore.pyqtSignal(str)        

        #self.lock_thread = LockThread(self)
        # self.connect(self.lock_thread,QtCore.SIGNAL("finished()"),self.done)
        #self.lock_thread.new_value_signal.connect(self.new_value_loop)
        #self.perform_lock = False
        self.ctrl = {'break': False, 'value': '120'}
        
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
            self.read_peakpos_btn.clicked.connect(self.PlotPeaks)
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
            ## w5:buttons to choose what to display
            #######################################################################
            self.w5 = pg.LayoutWidget()
            
            self.peakposbtn = QtGui.QPushButton('Peak pos')
            self.peakposbtn.setCheckable(True)
            self.peakposbtn.setStyleSheet(':checked { color: salmon; background: #ffc9de }')
            self.peakposbtn.clicked.connect(self.ShowPeakPos)
            
            self.peaktrackerbtn = QtGui.QPushButton('Peak tracker')
            self.peaktrackerbtn.setCheckable(True)
            self.peaktrackerbtn.setStyleSheet(':checked { color: orange; background: #fdd97c }') 
            #self.peaktrackerbtn.clicked.connect(self.ShowPeakPosOverTime)
            self.peaktrackerbtn.clicked.connect(self.UpdatePeakTracker)
            
            self.errortrackerbtn = QtGui.QPushButton('Error tracker')
            #self.errortrackerbtn.setCheckable(True)
            self.errortrackerbtn.setStyleSheet(':checked { color: mediumorchid; background: thistle }') 
            self.errortrackerbtn.clicked.connect(self.Break)
            #self.errortrackerbtn.clicked.connect(self.ShowErrorOverTime)
            
            self.testlineedit = QtGui.QLineEdit('12')
            
            self.w5.addWidget(self.peakposbtn,row=0, col=1)
            self.w5.addWidget(self.peaktrackerbtn, row=0, col=2)
            self.w5.addWidget(self.errortrackerbtn, row=0, col=3)
            self.w5.addWidget(self.testlineedit, row=1, col=1, colspan=3)

            #######################################################################
            ## w2:graph of peak positions
            #######################################################################
            # aim is for this one to stop the connection to the arduino, basically stop the program running without fully closing the window
      
            self.w2 = pg.LayoutWidget()

            self.figure = plt.figure(facecolor='ghostwhite', frameon = True, figsize=(10,2))
            self.canvas = FigureCanvas(self.figure)

            self.w2.addWidget(self.canvas, row=0, col=0)
            
            
            #######################################################################
            ## w2: graph of peak pos over time 
            #######################################################################
            self.w3 = pg.LayoutWidget()
            
            self.figurePPOT = plt.figure(facecolor='ghostwhite', frameon = True, figsize=(10,4))
            self.canvasPPOT = FigureCanvas(self.figurePPOT)
            self.axPPOT = self.figurePPOT.add_subplot(111)
            self.figurePPOT.subplots_adjust(0.05, 0.4, 0.95, 0.95) # left,bottom,right,top 
            #self.axPPOT.tick_params(left = False, labelleft=False)
            
            self.w3.addWidget(self.canvasPPOT, row=0, col=0)
            
            #######################################################################
            ## w4: error info
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
            
            #######################################################################
            ## w6: error tracker
            #######################################################################
            self.w6 = pg.LayoutWidget()
            
            self.figureEOT = plt.figure(facecolor='ghostwhite', frameon = True, figsize=(10,4))
            self.canvasEOT = FigureCanvas(self.figureEOT)
  
            
            self.w3.addWidget(self.canvasEOT, row=0, col=0)
        
        
        
      
            self.d1.addWidget(self.w1, row=0, col=0)
            self.d1.addWidget(self.w2, row=2, col=0)
            self.d1.addWidget(self.w5, row=1, col=0)
            self.d1.addWidget(self.w3, row=3, col=0)
            self.d1.addWidget(self.w6, row=4, col=0)
            self.d1.addWidget(self.w4, row=5, col=0)
            
            
 
            
            
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
            self.currentlasererror = currentlasererror.decode().strip()

        
            
            #get cavity error
            arduino.write(str.encode('pm!'))
            currentcaverror = arduino.readline()
            self.currentcaverror = currentcaverror.decode().strip()
            
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
        
        
    def PlotPeaks(self):
        self.ExtractPeakPos()
        
		# clearing old figure
        self.figure.clear()
        
		# create an axis
        ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(0.05, 0.4, 0.95, 0.95) # left,bottom,right,top 
        ax.tick_params(left = False, labelleft=False)
        
        if self.unit_swapcheckbox.isChecked():
            ax.set_xlabel("Peak position (ms)")
            ax.axvline(x=float(self.peak1pos)/84000, ymin=0, ymax= 1, color='#ffa62b')
            ax.axvline(x=float(self.peak2pos)/84000, ymin=0, ymax= 1, color='#ffa62b')
            ax.axvline(x=float(self.peak3pos)/84000, ymin=0, ymax= 1, color='#ffa62b')
        else:
            ax.set_xlabel("Peak position (AU)")
            ax.axvline(x=self.peak1pos, ymin=0, ymax= 1)
            ax.axvline(x=self.peak2pos, ymin=0, ymax= 1)
            ax.axvline(x=self.peak3pos, ymin=0, ymax= 1)
    
		# refresh canvas
        self.canvas.draw()
        
        if self.peakposbtn.isChecked():
            self.canvas.setVisible(True)
            print('should be visible')
        else:
            self.canvas.hide()
            print('should be hiding')
        
    
    def ShowPeakPos(self):
        
        if self.peakposbtn.isChecked():
            self.canvas.setVisible(True)
            self.figure.subplots_adjust(0.05, 0.4, 0.95, 0.95)
        else:
            self.canvas.hide()
            
    def ShowPeakPosOverTime(self):
        
        if self.peaktrackerbtn.isChecked():
            self.canvasPPOT.setVisible(True)
            self.figurePPOT.subplots_adjust(0.05, 0.4, 0.95, 0.95)
        else:
            self.canvasPPOT.hide()
            
    def ShowErrorOverTime(self):
        #hijacking for tests
        #self.testsignal.emit('you should pause folks')
        #self.ctrl['break'] = True
        time.sleep(0.4)
        comport = self.general_things.parameter_loop_comboBox.currentText()
        
        message = 'm' + 'a' + '100' + '!' #encode given data into a message the arduino can understand
        #print(f'message is {message}')
        try:
            arduino = serial.Serial(comport, self.baudrate, timeout=.1)#should hopefully open the serial communication?
            #print('COM port open in talking')
            
            #
            arduino.write(str.encode(message)) #send this message to the arduino, activates the message_parser function
            
            arduino.close()
            print('yep we wrote a message')
            #print('port closed in talking')
        except (OSError, serial.SerialException):
            print('whoops the arduino is not there test edition') 
        
        '''
        if self.errortrackerbtn.isChecked():
            self.canvasEOT.setVisible(True)
            self.figureEOT.subplots_adjust(0.05, 0.4, 0.95, 0.95)
        else:
            self.canvasEOT.hide()'''
            
    def UpdatePeakTracker(self):
        #should take the updated data and then plot 
        self.thread = QtCore.QThread()
        self.worker = PeakPosTrackerThread(self.ctrl)
        self.worker.moveToThread(self.thread)
        
        #connect signals and slots
        
        #this one should ensure the task will be called automatically when the function is called
        self.thread.started.connect(self.worker.TASK)
        #self.worker.updated.connect(self.PlotPeakTrackerGraph)
        
        #also connect the finsihed thread to quit and deleteLater
        
        #maybe have a bit here where if something has happened with the GUI we do that stuff- ie that sends a signal 
        #can we have a bit that's like hmm while we're waiting to take data, if we get this signal, do the stuff
        
        
        #start the thread
        self.thread.start()
        
    def PlotPeakTrackerGraph(self, peakvalues):
        #peakvalues might be a list [1, 2, 3]
        toplot1 = peakvalues[0]
        toplot2 = peakvalues[1]
        toplot3 = peakvalues[3]
        time = peakvalues[3]
        
        self.axPPOT.scatter(time, toplot1, color='deeppink', s=0.7)
        self.axPPOT.scatter(time, toplot2, color='darkturquoise', s=0.7)
        self.axPPOT.scatter(time, toplot3, color='orange', s=0.7)
        
        
    def Break(self):
        self.ctrl['break'] = True
        print('weve set break to true')
        self.modifyvariables = modifyandreadvariables.ModifyandRead_variable(self)
       # self.testsignal.emit('120')
        #self.ctrl['value'] = str(self.testlineedit.text())
        self.ctrl['value'] = str(self.modifyvariables.cavPgainLE.text())
        print(self.ctrl['value'])