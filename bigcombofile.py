# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 12:43:00 2022

@author: mcwt12
"""

'''
Editing settings for STCL GUI
'''

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
import datetime


import serial
import serial.tools.list_ports

from PyQt5.QtGui import QFont

# using now() to get current time
current_time = datetime.datetime.now()

import upkeep
USUAL_DIR = os.getcwd()

DATEMARKER = str(current_time.day) + '-' + str(current_time.month) + '-' + str(current_time.year) + '-' + str(current_time.hour) + 'h' + str(current_time.minute) 

#this part is just setting the default filenames to save things to - will have also have date and time in filename
DIR_PARAMS = USUAL_DIR+f'//({DATEMARKER})_lock_params'
DIR_READOUT = USUAL_DIR+f'//({DATEMARKER})_lockdata'
DIR_PEAKPOSPLOT = USUAL_DIR+f'//({DATEMARKER})_peakposplot'
DIR_LASERRORPLOT = USUAL_DIR+f'//({DATEMARKER})_lasererrorplot'
DIR_CAVERRORPLOT = USUAL_DIR+f'//({DATEMARKER})_caverrorplot'



#this worker thread handles the data taking loop for peak pos and errors
class PeakPosTrackerThread(QtCore.QObject):
    #signals here- emitted to the main thread to alert to something going on here
    updated = QtCore.pyqtSignal(list)
    readvalues = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()
    updatederr = QtCore.pyqtSignal(list)
    
    
    def __init__(self, ctrl, readctrl, ctrllock, ctrlstop, ctrllocklaser, ctrllockcav, ctrlpeakdisplay, comport):
        QtCore.QThread.__init__(self)
        
        #various control parameters that allow control from the main thread 
        #ie will switch communication to the arduino to this worker thread when the loop is running
        #stops issues that come up when you try to speak to the arduino when it's speaking
        self.ctrl = ctrl
        self.readctrl = readctrl
        self.ctrllock = ctrllock
        self.stopctrl = ctrlstop
        self.ctrllocklaser = ctrllocklaser
        self.ctrllockcav = ctrllockcav
        self.ctrlpeakdisplay = ctrlpeakdisplay
        
        self.general_things = upkeep.Upkeep(self)
        self.comport = comport

        self.arduino = serial.Serial(comport, 230400, timeout=.1) #open the serial communication
        
    
    def TASK(self):
        self.ctrl['break'] = False
        self.readctrl['break'] = False
        self.stopctrl['break'] = False
        #the data taking loop
        
        try:
            print('COM port open in talking')
            
            starttime = time.time() #find the time at which the data taking starts
            
            while time.time()< (starttime+30): 
                print("tick")
                
                #set peak 1
                self.arduino.write(str.encode('pf!'))
                peak1pos = self.arduino.readline()
                
                #set peak 2
                self.arduino.write(str.encode('pg!'))
                peak2pos = self.arduino.readline()
                
                #set peak 3
                self.arduino.write(str.encode('ph!'))
                peak3pos = self.arduino.readline()
                
                #getting the error data
                self.arduino.write(str.encode('pl!'))
                lasererror = self.arduino.readline()
                
                self.arduino.write(str.encode('pm!'))
                caverror = self.arduino.readline()
                
                #emit a signal to the main thread that has the peak position, error and time data
                #triggers the plotting/saving functions
                self.updated.emit([peak1pos.decode(), peak2pos.decode(), peak3pos.decode(), time.time()-starttime, lasererror.decode(), caverror.decode()]) #emit a signal to say it's been updated!
                
                #controls how often the data is sampled- here it's every second
                time.sleep(1 - ((time.time() - starttime) % 1))
                
                if self.ctrl['break']:
                    #moves sending written in data to the arduino to this worker thread 
                    #(ie this part handles when new values are typed in by hand and enter is pressed)
                    print('we sleeping')
                    
                    message = 'm' + self.ctrl['key'] + self.ctrl['value'] + '!' #encode given data into a message the arduino can understand
                    
                    try:
                        self.arduino.write(str.encode(message)) #send this message to the arduino, activates the message_parser function
                        print(f'yep we wrote a message: {message}')
                        
                    except (OSError, serial.SerialException):
                        print('whoops the arduino is not there test edition')
                    
                    self.ctrl['break'] = False #prevent this loop from running again unless triggered
                    
                if self.readctrl['break']:
                    #this part handles the communication when reading all the values from the arduino
                    #ie when 'values?' button pressed 
                    
                    values = [] #temp list to store the read values in
                    print('yep we reading')
                    try:
                        #set cavity P gain
                        self.arduino.write(str.encode('pa!')) #send this message to the arduino, activates the message_parser function- p means it'll print out the variable associated with the key a
                        cavPgain = self.arduino.readline() #set this value as the readout from the arduino
                        values.append(cavPgain.decode()) #decode from bytes to string and append to the empty array
                        
                        #set cavity I gain
                        self.arduino.write(str.encode('pb!'))
                        cavIgain = self.arduino.readline()
                        values.append(cavIgain.decode())
                        
                        #set laser P gain
                        self.arduino.write(str.encode('pc!'))
                        laserPgain = self.arduino.readline()
                        values.append(laserPgain.decode())
                        
                        #set laser I gain
                        self.arduino.write(str.encode('pd!'))
                        laserIgain = self.arduino.readline()
                        values.append(laserIgain.decode())
                        
                        #set laser D gain
                        self.arduino.write(str.encode('pq!'))
                        laserDgain = self.arduino.readline()
                        values.append(laserDgain.decode())
                        
                        #set laser ref
                        self.arduino.write(str.encode('pe!'))
                        laserfreqsetpoint = self.arduino.readline()
                        values.append(laserfreqsetpoint.decode())
                        
                        #set cavity offset
                        self.arduino.write(str.encode('pp!'))
                        cavoffsetpoint = self.arduino.readline()
                        values.append(cavoffsetpoint.decode())
                        
                        #set high threshold
                        self.arduino.write(str.encode('pk!'))
                        highthreshold = self.arduino.readline()
                        values.append(highthreshold.decode())
                        
                        #set low threshold
                        self.arduino.write(str.encode('pj!'))
                        lowthreshold = self.arduino.readline()
                        values.append(lowthreshold.decode())
                        
                        self.readvalues.emit(values) #emit a signal to say it's been updated, send the new values to main thread ready to display 
                        
                    except (OSError, serial.SerialException):
                        print('whoops the arduino is not there test edition')
                        
                    self.readctrl['break'] = False
                
                
                if self.ctrllock['break']:
                    #this part handles starting/stopping the lock whilst the loop is running
                    if self.ctrllock['value'] == 'lock':
                        self.arduino.write(str.encode('mh1!'))
                        print('should be locked')
                    if self.ctrllock['value'] == 'nolock':
                        self.arduino.write(str.encode('mh0!'))
                        print('should be unlocked')
                    self.ctrllock['break'] = False
                    
                if self.ctrllocklaser['break']:
                    #this part handles locking just the laser whilst the loop is running
                    #does this by setting both the cav gains to be zero temporarily
                    cavPgainmsg = 'm' + 'a' + str(self.ctrllocklaser['cavPgain']) + '!'
                    cavIgainmsg = 'm' + 'a' + str(self.ctrllocklaser['cavIgain']) + '!'
                    self.arduino.write(str.encode(cavPgainmsg))
                    self.arduino.write(str.encode(cavIgainmsg))
                    if self.ctrllocklaser['value'] == 'lock':
                        self.arduino.write(str.encode('mh1!'))
                        print(f'should be locked, {cavPgainmsg} and {cavIgainmsg}')
                    if self.ctrllocklaser['value'] == 'nolock':
                        self.arduino.write(str.encode('mh0!'))
                        print(f'should be unlocked,{cavPgainmsg} and {cavIgainmsg}')
                    self.ctrllocklaser['break'] = False
                    
                if self.ctrllockcav['break']:
                    #this part handles locking just the cav whilst the loop is running
                    #does this by setting both the laser gains to be zero temporarily
                    laserPgainmsg = 'm' + 'c' + str(self.ctrllockcav['laserPgain']) + '!'
                    laserIgainmsg = 'm' + 'd' + str(self.ctrllockcav['laserIgain']) + '!'
                    laserDgainmsg = 'm' + 'k' + str(self.ctrllockcav['laserDgain']) + '!'
                    self.arduino.write(str.encode(laserPgainmsg))
                    self.arduino.write(str.encode(laserIgainmsg))
                    self.arduino.write(str.encode(laserDgainmsg))
                    if self.ctrllockcav['value'] == 'lock':
                        self.arduino.write(str.encode('mh1!'))
                        print(f'should be locked, {laserPgainmsg} and {laserIgainmsg}and {laserDgainmsg}')
                    if self.ctrllockcav['value'] == 'nolock':
                        self.arduino.write(str.encode('mh0!'))
                        print(f'should be unlocked,{laserPgainmsg} and {laserIgainmsg}and {laserDgainmsg}')
                    self.ctrllockcav['break'] = False
                    
                if self.stopctrl['break']:
                    #if the stop loop button is pressed, or the window is closed, break from the loop
                    print('finished loop bc flag raised')
                    break                    
                            
            #once exited the loop, close the serial connection and emit the finished signal so thread etc can be deleted
            self.arduino.close()
            print('port closed in talking')
            self.finished.emit()
        except (OSError, serial.SerialException):
            print('LOOP version whoops the arduino is not there')






#the main class! where all the widgets/functions are
class ModifyandRead_variable(QtGui.QMainWindow):

    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self.parentGui = parent
        #self.sampling_rate = 250
        self.initUI()

    def initUI(self):
        
        #setting placeholder values for the various parameters
        self.cavPgain = 9
        self.cavIgain = 2
        self.laserPgain = 3
        self.laserIgain = 4
        self.laserDgain = 5
        self.laserfreqsetpoint = 6
        self.cavoffsetpoint = 7
        self.highthreshold = 8
        self.lowthreshold = 9
        
        #to help deal with converting units (ie to ms/mV)
        self.laserfreqsetpointMS = 0.6
        self.cavoffsetpointMS = 0.7
        self.highthresholdMV = 0.8
        self.lowthresholdMV = 0.9
        
        self.tempstorageLFSP = 10 
        self.tempstorageCOSP = 13
        
        self.tempstorageHT = 100
        self.tempstorageLT = 130
        
        #baudrate for serial communication over the native port of the arduino
        self.baudrate = 230400
        
        #self.general_things = upkeep.Upkeep(self)
        
        #placeholders for the peak positions and errors
        self.examplefilename = 'example filename'
        self.peak1pos = 100
        self.peak2pos = 200
        self.peak3pos = 300
        self.currentlasererror = 23
        self.currentcaverror = 34
        
        #various control variables to handle moving communication to worker thread when loop is running
        self.ctrl = {'break': False, 'value': '120', 'key': 'b'}
        self.readctrl = {'break':False, 'cPvalue': '12', 'cPkey': 'a', 'cIvalue':'13', 'cIkey':'b', 'lPvalue':'14', 'lPkey':'c', 'lIvalue':'14', 'lIkey':'d', 'lDvalue':'15', 'lDkey':'q', 'LFOSvalue':'16', 'LFOSkey':'e', 'COSvalue':'17', 'COSkey':'p', 'HTvalue':'18', 'HTkey':'k', 'LTvalue':'19', 'LTkey':'j'}
        self.ctrllock = {'break': False, 'value': 'placeholder'}
        self.stopctrl = {'break': False}#
        self.ctrllocklaser = {'break':False, 'lock':'placeholder', 'cavPgain':'44', 'cavIgain':'43'}
        self.ctrllockcav = {'break':False, 'lock':'placeholder', 'laserPgain':'45', 'laserIgain':'46', 'laserDgain':'47'}
        self.ctrlpeakdisplay = {'break':False, }
        
        
        #helps with live plotting the peak positions in the desired units
        self.plotinms = False
        
        #for saving the gains that were present before being set to 0 for locking just laser or just cav
        self.storagecavPgain = 130
        self.storagecavIgain = 140
        self.storagelaserPgain = 150
        self.storagelaserIgain = 160
        self.storagelaserDgain = 170
        
        #storage lists to help with calculating the rms error values
        self.lasererrorvalues = []
        self.caverrorvalues = []
        


        
        #GUI
        self.area = dockarea.DockArea()
        self.setCentralWidget(self.area)
        self.resize(100,100)
        self.setWindowTitle('Adiabatic')
        self.createDocks()
        
    def createDocks(self):
            self.d1 = dockarea.Dock("AWG", size=(300,200))
            self.d1.hideTitleBar()
            self.d2 = dockarea.Dock("AWG1", size=(300,200))
            self.d2.hideTitleBar()
            self.d3 = dockarea.Dock('AWG2', size=(1000,200))
            self.d3.hideTitleBar()
            
            
            
            #######################################################################
            ## w1: modify and read variables
            #######################################################################
    
            self.w1 = pg.LayoutWidget()
            self.label_w1 = QtGui.QLabel('STCL')
            self.label_w1.setFont(QFont('Helvetica', 10))
            self.label_w1.setAlignment(QtCore.Qt.AlignCenter)
            
            
            #button to load values from a file
            self.load_files_btn = QtGui.QPushButton('Load parameters')
            self.load_files_btn.clicked.connect(self.LoadParameters)
            self.load_files_btn.setStyleSheet(':hover {background: aquamarine}')
            
            #button to read the values and update them
            self.read_values_btn = QtGui.QPushButton('Values?')
            self.read_values_btn.clicked.connect(self.WhenValuesBtnPress)
            self.read_values_btn.setStyleSheet(':hover { background: lightpink }')
            
            #checkbox to see if you want to save the parameters
            self.save_params_checkbox = QtGui.QCheckBox('Save parameters?')
    
            
            #read and write boxes to display the values of the locking parameters
            self.cavPgainLE = QtGui.QLineEdit(str(self.cavPgain))
            self.cavPgainLE.returnPressed.connect(self.cavPgainChangeText)
            self.label_cavPgainLE = QtGui.QLabel('Cavity P gain')
            self.cavPgainvalue = QtGui.QLabel(str(self.cavPgain))
            self.cavPgainvalue.setStyleSheet("border: 1px solid black")
            
            self.cavIgainLE = QtGui.QLineEdit(str(self.cavIgain))
            self.cavIgainLE.returnPressed.connect(self.cavIgainChangeText)
            self.label_cavIgainLE = QtGui.QLabel('Cavity I gain')
            self.cavIgainvalue = QtGui.QLabel(str(self.cavIgain))
            self.cavIgainvalue.setStyleSheet("border: 1px solid black")
            
            self.laserPgainLE = QtGui.QLineEdit(str(self.laserPgain))
            self.laserPgainLE.returnPressed.connect(self.laserPgainChangeText)
            self.label_laserPgainLE = QtGui.QLabel('Laser P gain')
            self.laserPgainvalue = QtGui.QLabel(str(self.laserPgain))
            self.laserPgainvalue.setStyleSheet("border: 1px solid black")
            
            self.laserIgainLE = QtGui.QLineEdit(str(self.laserIgain))
            self.laserIgainLE.returnPressed.connect(self.laserIgainChangeText)
            self.label_laserIgainLE = QtGui.QLabel('Laser I gain')
            self.laserIgainvalue = QtGui.QLabel(str(self.laserIgain))
            self.laserIgainvalue.setStyleSheet("border: 1px solid black")
            
            self.laserDgainLE = QtGui.QLineEdit(str(self.laserDgain))
            self.laserDgainLE.returnPressed.connect(self.laserDgainChangeText)
            self.label_laserDgainLE = QtGui.QLabel('Laser D gain')
            self.laserDgainvalue = QtGui.QLabel(str(self.laserDgain))
            self.laserDgainvalue.setStyleSheet("border: 1px solid black")
            
            self.laserfreqsetpointLE = QtGui.QLineEdit(str(self.laserfreqsetpoint))
            self.laserfreqsetpointLE.returnPressed.connect(self.laserfreqsetpointChangeText)
            self.laserfreqsetpointLE.textEdited.connect(self.TextEditmsUnitSortOut)
            self.label_laserfreqsetpointLE = QtGui.QLabel('Laser setpoint')
            self.laserfreqsetpointvalue = QtGui.QLabel(str(self.laserfreqsetpoint))
            self.laserfreqsetpointvalue.setStyleSheet("border: 1px solid black")
            
            self.cavoffsetpointLE = QtGui.QLineEdit(str(self.cavoffsetpoint))
            self.cavoffsetpointLE.returnPressed.connect(self.cavoffsetpointChangeText)
            self.cavoffsetpointLE.textEdited.connect(self.TextEditmsUnitSortOut)
            self.label_cavoffsetpointLE = QtGui.QLabel('Cavity setpoint')
            self.cavoffsetpointvalue = QtGui.QLabel(str(self.cavoffsetpoint))
            self.cavoffsetpointvalue.setStyleSheet("border: 1px solid black")
            
            self.highthresholdLE = QtGui.QLineEdit(str(self.highthreshold))
            self.highthresholdLE.returnPressed.connect(self.highthresholdChangeText)
            self.highthresholdLE.textEdited.connect(self.TextEditmVUnitSortOut)
            self.label_highthresholdLE = QtGui.QLabel('High threshold')
            self.highthresholdvalue = QtGui.QLineEdit(str(self.highthreshold))
            self.highthresholdvalue.setStyleSheet("border: 1px solid black")
            
            self.lowthresholdLE = QtGui.QLineEdit(str(self.lowthreshold))
            self.lowthresholdLE.returnPressed.connect(self.lowthresholdChangeText)
            self.lowthresholdLE.textEdited.connect(self.TextEditmVUnitSortOut)
            self.label_lowthresholdLE = QtGui.QLabel('Low threshold')
            self.lowthresholdvalue = QtGui.QLabel(str(self.lowthreshold))
            self.lowthresholdvalue.setStyleSheet("border: 1px solid black")
            
            self.blankspace= QtGui.QLabel('')
            self.blankspace2= QtGui.QLabel('')
            self.blankspace4= QtGui.QLabel('')
            
            #can choose to save the current parameters
            self.saveparamsbtn = QtGui.QPushButton('Save parameters?')
            self.saveparamsbtn.setStyleSheet(':hover { background: papayawhip }')
    
            #control the units of the whole GUI
            self.swapunits_label= QtGui.QLabel('Swap units')
            self.swaptoms_btn = QtGui.QCheckBox('ms?')
            self.swaptoms_btn.stateChanged.connect(self.WhenmsChecked)
            self.swaptomV_btn = QtGui.QCheckBox('mV?')
            self.swaptomV_btn.stateChanged.connect(self.WhenmVChecked)
            
            
    
            
            self.w1.addWidget(self.load_files_btn, row = 1,col=0, colspan=3)
            self.w1.addWidget(self.read_values_btn, row = 1, col= 3)
            self.w1.addWidget(self.save_params_checkbox, row = 2, col= 1)
            
            self.w1.addWidget(self.blankspace4, row= 3, col=0, colspan=3)
            
            #adding in line edit boxes
            self.w1.addWidget(self.cavPgainLE, row = 4, col = 2)
            self.w1.addWidget(self.cavIgainLE, row = 5, col = 2)
            self.w1.addWidget(self.laserPgainLE, row = 6, col = 2)
            self.w1.addWidget(self.laserIgainLE, row = 7, col = 2)
            self.w1.addWidget(self.laserDgainLE, row = 8, col = 2)
            self.w1.addWidget(self.laserfreqsetpointLE, row = 9, col = 2)
            self.w1.addWidget(self.cavoffsetpointLE, row = 10, col = 2)
            self.w1.addWidget(self.highthresholdLE, row = 11, col = 2)
            self.w1.addWidget(self.lowthresholdLE, row = 12, col = 2)
            #labels
            self.w1.addWidget(self.label_cavPgainLE, row = 4, col = 1)
            self.w1.addWidget(self.label_cavIgainLE, row = 5, col = 1)
            self.w1.addWidget(self.label_laserPgainLE, row = 6, col = 1)
            self.w1.addWidget(self.label_laserIgainLE, row = 7, col = 1)
            self.w1.addWidget(self.label_laserDgainLE, row = 8, col = 1)
            self.w1.addWidget(self.label_laserfreqsetpointLE, row = 9, col = 1)
            self.w1.addWidget(self.label_cavoffsetpointLE, row = 10, col = 1)
            self.w1.addWidget(self.label_highthresholdLE, row = 11, col = 1)
            self.w1.addWidget(self.label_lowthresholdLE, row = 12, col = 1)
            # values
            self.w1.addWidget(self.cavPgainvalue, row = 4, col = 3)
            self.w1.addWidget(self.cavIgainvalue, row = 5, col = 3)
            self.w1.addWidget(self.laserPgainvalue, row = 6, col = 3)
            self.w1.addWidget(self.laserIgainvalue, row = 7, col = 3)
            self.w1.addWidget(self.laserDgainvalue, row = 8, col = 3)
            self.w1.addWidget(self.laserfreqsetpointvalue, row = 9, col = 3)
            self.w1.addWidget(self.cavoffsetpointvalue, row = 10, col = 3)
            self.w1.addWidget(self.highthresholdvalue, row = 11, col = 3)
            self.w1.addWidget(self.lowthresholdvalue, row = 12, col = 3)
            
            
            self.w1.addWidget(self.blankspace2, row = 13, col= 0, colspan= 1) #this is literally just to help with the spacing
            
            self.w1.addWidget(self.swaptoms_btn, row = 14, col= 2, colspan= 1)
            self.w1.addWidget(self.swaptomV_btn, row = 14, col= 3, colspan= 1) 
            self.w1.addWidget(self.swapunits_label, row = 14, col= 1, colspan= 1) #this is literally just to help with the spacing
          
            self.w1.addWidget(self.blankspace, row = 15, col= 0, colspan= 4) #this is literally just to help with the spacing
            
           
            
           
            ##########################################################################
            # w9: the different locking buttons
            ##########################################################################
            
            self.w9 = pg.LayoutWidget()
           
            #locks everything
            self.lock_btn = QtGui.QPushButton('Lock')
            self.lock_btn.setCheckable(True)
            self.lock_btn.setStyleSheet("QPushButton""{""background-color : lightblue;""}""QPushButton::checked""{""color:green; background-color : palegreen;""}")
            self.lock_btn.pressed.connect(self.LockBtn)
            
            #locks just the laser
            self.lockjustlaserbtn = QtGui.QPushButton('Lock laser')
            self.lockjustlaserbtn.setCheckable(True)
            self.lockjustlaserbtn.setStyleSheet("QPushButton""{""background-color : lightblue;""}""QPushButton::checked""{""color:green; background-color : palegreen;""}")
            self.lockjustlaserbtn.clicked.connect(self.LockJustLaser)
            
            #locks just the cavity
            self.lockjustcavbtn = QtGui.QPushButton('Lock cav')
            self.lockjustcavbtn.setCheckable(True)
            self.lockjustcavbtn.setStyleSheet("QPushButton""{""background-color : lightblue;""}""QPushButton::checked""{""color:green; background-color : palegreen;""}")
            self.lockjustcavbtn.clicked.connect(self.LockJustCavity)
            
            self.w9.addWidget(self.lock_btn, row=0, col=1)
            self.w9.addWidget(self.lockjustlaserbtn, row=0, col=2)
            self.w9.addWidget(self.lockjustcavbtn, row=0, col=3)
           
           
           
            #######################################################################
            ## w2: reading out the peak positions and the errors
            #######################################################################
            self.w2 = pg.LayoutWidget()
            
            
            #peak positions
            self.read_peakpos_btn = QtGui.QPushButton('Peaks?')
            self.read_peakpos_btn.clicked.connect(self.WhenPeakPosBtnPressed)
            self.read_peakpos_btn.clicked.connect(self.PlotPeaks)
            self.read_peakpos_btn.setStyleSheet(':hover { background: powderblue }')
            self.unit_swapcheckbox = QtGui.QCheckBox('ms?')
            
            #these are buttons to copy the values required to lock the laser and cav where they 
            #currently are over to the arduino
            self.peak1pos_label = QtGui.QPushButton('Peak 1')
            self.peak2pos_label = QtGui.QPushButton('Peak 2')
            self.peak2pos_label.clicked.connect(self.CopyFollowerLaserPos)
            self.peak1pos_label.clicked.connect(self.CopyFirstPeakPos)
            self.peak3pos_label = QtGui.QLabel('Peak 3')
            self.peak3pos_label.setAlignment(QtCore.Qt.AlignCenter)
            self.peak3pos_label.setStyleSheet("border: 1px solid black")
            
            self.peak1posvalue = QtGui.QLabel(str(self.peak1pos))
            self.peak2posvalue = QtGui.QLabel(str(self.peak2pos))
            self.peak3posvalue = QtGui.QLabel(str(self.peak3pos))
            self.peak1posvalue.setAlignment(QtCore.Qt.AlignCenter)
            self.peak2posvalue.setAlignment(QtCore.Qt.AlignCenter)
            self.peak3posvalue.setAlignment(QtCore.Qt.AlignCenter)
            
            
            #errors
            self.read_errors_btn = QtGui.QPushButton('Error?')
            self.read_errors_btn.clicked.connect(self.WhenErrorbtnPress)
            self.read_errors_btn.setStyleSheet(':hover { background: palegreen }')
            
            self.laser_error_label = QtGui.QLabel('Laser error')
            self.laser_error = QtGui.QLabel('1')
            self.cav_error_label = QtGui.QLabel('Cavity error')
            self.cav_error = QtGui.QLabel('2')
            
            #RMS errors 
            self.laserRMSlabel = QtGui.QLabel('RMS')
            self.laserRMSvalue = QtGui.QLabel('12')
            self.cavRMSvalue = QtGui.QLabel('13')
            
            self.blankspace= QtGui.QLabel('')

            self.w2.addWidget(self.read_peakpos_btn, row=0, col=0)
            self.w2.addWidget(self.peak1pos_label, row=0, col=1)
            self.w2.addWidget(self.peak2pos_label, row=0, col=2)
            self.w2.addWidget(self.peak3pos_label, row=0, col= 3, colspan=2)
            self.w2.addWidget(self.peak1posvalue, row=1, col=1)
            self.w2.addWidget(self.peak2posvalue, row=1, col=2)
            self.w2.addWidget(self.peak3posvalue, row=1, col=3, colspan=2)
            
            self.w2.addWidget(self.blankspace, row=2,col=0, colspan=3)
            
            self.w2.addWidget(self.read_errors_btn, row=3, col=0, colspan=2)
            self.w2.addWidget(self.laser_error_label, row=3, col=2)
            self.w2.addWidget(self.laser_error, row=4, col=2)
            self.w2.addWidget(self.cav_error_label, row=3, col=3)
            self.w2.addWidget(self.cav_error, row=4, col=3)
            self.w2.addWidget(self.laserRMSlabel, row = 5, col=0, colspan=2)
            self.w2.addWidget(self.laserRMSvalue, row = 5, col =2)
            self.w2.addWidget(self.cavRMSvalue, row = 5, col =3)
            
            self.laser_error_label.setAlignment(QtCore.Qt.AlignCenter)
            self.laser_error.setAlignment(QtCore.Qt.AlignCenter)
            self.cav_error_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cav_error.setAlignment(QtCore.Qt.AlignCenter)
            self.laserRMSlabel.setAlignment(QtCore.Qt.AlignRight)
            self.laserRMSvalue.setAlignment(QtCore.Qt.AlignCenter)
            self.cavRMSvalue.setAlignment(QtCore.Qt.AlignCenter)
            
            
            #######################################################################
            ## w5:buttons controlling the data taking loops
            #######################################################################
            self.w5 = pg.LayoutWidget()
            
            #button to stop the data taking loop
            self.STOPbtn = QtGui.QPushButton('STOP loop')
            self.STOPbtn.setStyleSheet("QPushButton""{""background-color : tomato;""}")
            self.STOPbtn.clicked.connect(self.StopTracker)
            
            #button to start the data taking loop
            self.startloopbtn = QtGui.QPushButton('Start Loop')
            self.startloopbtn.setCheckable(True)
            self.startloopbtn.setStyleSheet("QPushButton""{""background-color : navajowhite;""}""QPushButton::checked""{""color: orange; background: #fdd97c""}")
            self.startloopbtn.clicked.connect(self.UpdatePeakTracker)
            
            #if checked, will plot the errors
            self.errortrackerbtn = QtGui.QPushButton('Error tracker')
            self.errortrackerbtn.setCheckable(True)
            self.errortrackerbtn.setStyleSheet(':checked { color: mediumorchid; background: thistle }') 
            
            #if checked, will save the data and also png files of the plots
            self.savereadouttoggle = QtGui.QCheckBox('Save?')
            self.filenametosave = QtGui.QLineEdit('example filename')
            self.filenametosave.returnPressed.connect(self.SetFilePathToSave)
            
            #if checked, will plot the peak positions
            self.peaktrackerbtn = QtGui.QPushButton('Peak Tracker')
            self.peaktrackerbtn.setCheckable(True)
            self.peaktrackerbtn.setStyleSheet(':checked { color: deeppink; background: pink }') 
            
            
            
            self.w5.addWidget(self.STOPbtn,row=0, col=1)
            self.w5.addWidget(self.startloopbtn, row=0, col=4)
            self.w5.addWidget(self.errortrackerbtn, row=0, col=3)
            self.w5.addWidget(self.peaktrackerbtn, row=0, col=2)
            
            self.w5.addWidget(self.savereadouttoggle, row=1, col=1)
            self.w5.addWidget(self.filenametosave, row=1, col=2, colspan=3)
            
           
            #######################################################################
            ## w7:graph of peak positions
            #######################################################################
            
            self.w7 = pg.LayoutWidget()

            self.figure = plt.figure(facecolor='ghostwhite', frameon = True, figsize=(10,2))
            self.canvas = FigureCanvas(self.figure)
            ax = self.figure.add_subplot(111)
            self.figure.subplots_adjust(0.05, 0.4, 0.95, 0.95) # left,bottom,right,top 
            ax.tick_params(left = False, labelleft=False)
            ax.set_xlabel('Peak position')
            

            self.w7.addWidget(self.canvas, row=0, col=0)
            
            
            #######################################################################
            ## w3:graph of peak positions OVER TIME
            #######################################################################
            
            self.w3 = pg.LayoutWidget()

            self.figurePPOT = plt.figure(facecolor='ghostwhite', frameon = True, figsize=(10,2))
            self.canvasPPOT = FigureCanvas(self.figurePPOT)
            self.axPPOT = self.figurePPOT.add_subplot(111)
            self.figurePPOT.subplots_adjust(0.15, 0.15, 0.95, 0.95) # left,bottom,right,top 
            self.axPPOT.set_ylabel('Peak position')
            self.axPPOT.set_xlabel('Time (s)')
            

            self.w3.addWidget(self.canvasPPOT, row=0, col=0)
            
            #######################################################################
            ## w6:graph of errors OVER TIME
            #######################################################################
            
            self.w6 = pg.LayoutWidget()

            self.figureEOT = plt.figure(facecolor='ghostwhite', frameon = True, figsize=(10,2))
            self.canvasEOT = FigureCanvas(self.figureEOT)
            self.axEOT = self.figureEOT.add_subplot(111)
            self.figureEOT.subplots_adjust(0.15, 0.25, 0.95, 0.95) # left,bottom,right,top 
            self.axEOT.set_xlabel('Time (s)')
            self.axEOT.set_ylabel('Cavity error')
            
            self.figureEOT2 = plt.figure(facecolor='ghostwhite', frameon = True, figsize=(10,2))
            self.canvasEOT2 = FigureCanvas(self.figureEOT2)
            self.axEOT2 = self.figureEOT2.add_subplot(111)
            self.figureEOT2.subplots_adjust(0.15, 0.25, 0.95, 0.95) # left,bottom,right,top 
            self.axEOT2.set_xlabel('Time (s)')
            self.axEOT2.set_ylabel('Laser error')
            
            
            self.blankspace3 = QtGui.QLabel('')

            self.w6.addWidget(self.canvasEOT, row=0, col=0)
            self.w6.addWidget(self.canvasEOT2, row=1, col=0)
            #self.w6.addWidget(self.blankspace3, row=0, col=7)
            
            
            #######################################################################
            ## w8: Choose COM port
            #######################################################################
    
            self.w8 = pg.LayoutWidget()
            self.label_comport = QtGui.QLabel('COM port')
            self.label_comport.setFont(QFont('Helvetica', 10))
            
            self.label_comport.setAlignment(QtCore.Qt.AlignRight)
            
            
            self.parameter_loop_comboBox = QtGui.QComboBox() 
            #finding all the available COM ports and adding their names to the drop down menu
            list_serialports = serial.tools.list_ports.comports()
            for n in range(len(list_serialports)):
                test = list_serialports[n][0]
                self.parameter_loop_comboBox.addItem(str(test)) 
            
            if len(list_serialports) == 0: 
                self.label_comport.setStyleSheet('color : tomato') 
    
            
            self.infobutton = QtGui.QPushButton('?')
            self.infobutton.resize(0.01,0.01)
            
            self.w8.addWidget(self.infobutton, row=0, col=0)
            self.w8.addWidget(self.blankspace, row = 0, col= 1, colspan=4)
            self.w8.addWidget(self.label_comport, row=0, col=5,colspan = 8)
            self.w8.addWidget(self.parameter_loop_comboBox, row = 0, col = 14,colspan = 4) 
            
            
            
            
            #organise the widget groups into docks
            
            self.d1.addWidget(self.w8, row=0, col=0)
            self.d1.addWidget(self.w1, row=1, col=0, rowspan=8)
               
            self.d2.addWidget(self.w9, row=0, col=0, rowspan=1)
            self.d2.addWidget(self.w5, row=1, col=0, rowspan=3)
            self.d2.addWidget(self.w7, row=4, col=0, rowspan=5)
            self.d2.addWidget(self.w2, row=9, col=0, rowspan=4)
            
            self.d3.addWidget(self.w3, row=0, col=2, rowspan=6)
            self.d3.addWidget(self.w6, row=6, col=2, rowspan=7)
            
            
           
           
           ############################################################################
           

   
   
    def GenerateParamDict(self):
        #reads the internal parameters and packages them into a dictionary, ready to be saved
        dict = {}
        dict['cavPgain'] = self.cavPgain
        dict['cavIgain'] = self.cavIgain
        dict['laserPgain'] = self.laserPgain
        dict['laserIgain'] = self.laserIgain
        dict['laserDgain'] = self.laserDgain
        dict['laserfreqsetpoint'] = self.laserfreqsetpoint
        dict['cavoffsetpoint'] = self.cavoffsetpoint
        dict['highthreshold'] = self.highthreshold
        dict['lowthreshold'] = self.lowthreshold
        return dict
        #print(dict) 
        

        

    def SaveParameters(self): 
        #saves the internal parameters in dictionary-esque format, in arduino units, not ms or mV
        dict = self.GenerateParamDict()  

        param_file = QtGui.QFileDialog.getSaveFileName(self, 'Save Params', DIR_PARAMS) 

        if param_file:
            with open(param_file[0], 'w') as f :
                for key in dict:
                    msg = ''
                    msg += key
                    msg += '\t' #this is just a big space
                    msg += str(dict[key])
                    msg += '\n'
                    f.write(msg)
                    print(f'saving this: {msg}')
            f.close()
        print(dict)
 

    def TalktoArduino(self):
        #this function talks to the arduino, extracts the current parameter values from it
        #and then sets the internal parameters to be equal to them
        comport = self.parameter_loop_comboBox.currentText()

        try:
            #open serial communication to the arduino
            arduino = serial.Serial(comport, self.baudrate, timeout=.1)
            print('COM port open in talking')
            
            #set cavity P gain
            arduino.write(str.encode('pa!')) #send this message to the arduino, activates the message_parser function- p means it'll print out the variable associated with the key a
            cavPgain = arduino.readline() #set this value as the readout from the arduino
            self.cavPgain = cavPgain.decode() #decode from bytes to string
            
            #set cavity I gain
            arduino.write(str.encode('pb!'))
            cavIgain = arduino.readline()
            self.cavIgain = cavIgain.decode()
            
            #set laser P gain
            arduino.write(str.encode('pc!'))
            laserPgain = arduino.readline()
            self.laserPgain = laserPgain.decode()
            
            #set laser I gain
            arduino.write(str.encode('pd!'))
            laserIgain = arduino.readline()
            self.laserIgain = laserIgain.decode()
            
            #set laser D gain
            arduino.write(str.encode('pq!'))
            laserDgain = arduino.readline()
            self.laserDgain = laserDgain.decode()
            
            #set laser ref
            arduino.write(str.encode('pe!'))
            laserfreqsetpoint = arduino.readline()
            self.laserfreqsetpoint = laserfreqsetpoint.decode()
            
            #set cavity offset
            arduino.write(str.encode('pp!'))
            cavoffsetpoint = arduino.readline()
            self.cavoffsetpoint = cavoffsetpoint.decode()
            
            #set high threshold
            arduino.write(str.encode('pk!'))
            highthreshold = arduino.readline()
            self.highthreshold = highthreshold.decode()
            
            #set low threshold
            arduino.write(str.encode('pj!'))
            lowthreshold = arduino.readline()
            self.lowthreshold = lowthreshold.decode()
            
            
            
            arduino.close()
            print('port closed in talking')
        except (OSError, serial.SerialException):
            print('whoops the arduino is not there') 
            
            
           
    def UpdateAfterRead(self, values):
        #this is the second half of the effect of the 'values?' button after the values have been
        #extracted from the arduino in the worker thread, now displying them nicely in the read boxes
        #HAPPENS IF THE LOOP IS RUNNING!!
        
        #set internal parameters to be thosejust extracted from the arduino
        self.cavPgain = values[0]
        self.cavIgain = values[1]
        self.laserPgain = values[2]
        self.laserIgain = values[3]
        self.laserDgain = values[4]
        self.laserfreqsetpoint = values[5]
        self.cavoffsetpoint = values[6]
        self.highthreshold = values[7]
        self.lowthreshold = values[8]
        
        #now updating the display
        self.cavPgainvalue.setText(str(round(float(self.cavPgain),3)))
        self.cavIgainvalue.setText(str(round(float(self.cavIgain),3)))
        self.laserPgainvalue.setText(str(round(float(self.laserPgain),3)))
        self.laserIgainvalue.setText(str(round(float(self.laserIgain),3)))
        self.laserDgainvalue.setText(str(round(float(self.laserDgain),3)))
        
        if self.swaptoms_btn.isChecked(): #should these values be loaded in ms or AU
            self.laserfreqsetpointMS = float(self.laserfreqsetpoint)#/84000
            self.laserfreqsetpointvalue.setText(str(round(self.laserfreqsetpointMS,3)))
            self.cavoffsetpointMS = float(self.cavoffsetpoint)/84000
            self.cavoffsetpointvalue.setText(str(round(self.cavoffsetpointMS,3)))
        else:
            self.laserfreqsetpointvalue.setText(str(round(float(self.laserfreqsetpoint),3)))
            self.cavoffsetpointvalue.setText(str(round(float(self.cavoffsetpoint),3)))
        if self.swaptomV_btn.isChecked():
            self.highthresholdMS = float(self.highthreshold)/100
            self.highthresholdvalue.setText(str(round(self.highthresholdMS,3)))
            self.lowthresholdMS = float(self.lowthreshold)/100
            self.lowthresholdvalue.setText(str(round(self.lowthresholdMS,3)))
        else:
            self.highthresholdvalue.setText(str(round(float(self.highthreshold),3)))
            self.lowthresholdvalue.setText(str(round(float(self.lowthreshold),3)))
        
        
        #Then give the option to save if the save values is checked
        if self.save_params_checkbox.isChecked():
            self.SaveParameters()
            
        #update all the write boxes to go back to normal colour to show we've extracted the up to date values
        self.cavPgainLE.setStyleSheet("border: 1px solid black; background-color : None")
        self.cavIgainLE.setStyleSheet("border: 1px solid black; background-color : None")
        self.laserPgainLE.setStyleSheet("border: 1px solid black; background-color : None")
        self.laserIgainLE.setStyleSheet("border: 1px solid black; background-color : None")
        self.laserDgainLE.setStyleSheet("border: 1px solid black; background-color : None")
        self.laserfreqsetpointLE.setStyleSheet("border: 1px solid black; background-color : None")
        self.cavoffsetpointLE.setStyleSheet("border: 1px solid black; background-color : None")
        self.highthresholdLE.setStyleSheet("border: 1px solid black; background-color : None")
        self.lowthresholdLE.setStyleSheet("border: 1px solid black; background-color : None")


        
    
        
    def WhenValuesBtnPress(self):
        #should talk to the arduino and update the interal gain values from what we have
        if self.startloopbtn.isChecked():
            #ie if the data taking loop is going, shift communication to the worker thread
            self.readctrl['break'] = True
            print('going to try to read')
        else:
            #update internal parameters to match those in the arduino
            self.TalktoArduino()
            
            #then present all the updated values in the nice read boxes
            self.cavPgainvalue.setText(str(round(float(self.cavPgain),3)))
            self.cavIgainvalue.setText(str(round(float(self.cavIgain),3)))
            self.laserPgainvalue.setText(str(round(float(self.laserPgain),3)))
            self.laserIgainvalue.setText(str(round(float(self.laserIgain),3)))
            self.laserDgainvalue.setText(str(round(float(self.laserDgain),3)))
            if self.swaptoms_btn.isChecked(): #should these values be loaded in ms or AU
                self.laserfreqsetpointMS = float(self.laserfreqsetpoint)#/84000
                self.laserfreqsetpointvalue.setText(str(round(self.laserfreqsetpointMS,3)))
                self.cavoffsetpointMS = float(self.cavoffsetpoint)/84000
                self.cavoffsetpointvalue.setText(str(round(self.cavoffsetpointMS,3)))
            else:
                self.laserfreqsetpointvalue.setText(str(round(float(self.laserfreqsetpoint),3)))
                self.cavoffsetpointvalue.setText(str(round(float(self.cavoffsetpoint),3)))
            if self.swaptomV_btn.isChecked():
                self.highthresholdMS = float(self.highthreshold)/100
                self.highthresholdvalue.setText(str(round(self.highthresholdMS,3)))
                self.lowthresholdMS = float(self.lowthreshold)/100
                self.lowthresholdvalue.setText(str(round(self.lowthresholdMS,3)))
            else:
                self.highthresholdvalue.setText(str(round(float(self.highthreshold),3)))
                self.lowthresholdvalue.setText(str(round(float(self.lowthreshold),3)))
            
            
            #Then give the option to save if the save values is checked
            if self.save_params_checkbox.isChecked():
                self.SaveParameters()
                
            #update all the write boxes to go back to normal colour
            self.cavPgainLE.setStyleSheet("border: 1px solid black; background-color : None")
            self.cavIgainLE.setStyleSheet("border: 1px solid black; background-color : None")
            self.laserPgainLE.setStyleSheet("border: 1px solid black; background-color : None")
            self.laserIgainLE.setStyleSheet("border: 1px solid black; background-color : None")
            self.laserDgainLE.setStyleSheet("border: 1px solid black; background-color : None")
            self.laserfreqsetpointLE.setStyleSheet("border: 1px solid black; background-color : None")
            self.cavoffsetpointLE.setStyleSheet("border: 1px solid black; background-color : None")
            self.highthresholdLE.setStyleSheet("border: 1px solid black; background-color : None")
            self.lowthresholdLE.setStyleSheet("border: 1px solid black; background-color : None")


       
  
    
  
    
  
    
  
    
       
    def LoadParameters(self):
    # occurs when load parameters button is opened
    #choose a file with parameters, then unpack from dictionary and set internal parameters 
    #to be these new values, send to arduino.
    #display new values in the write boxes and change colour of write boxes to alert that 
    #the read and write boxes aren't gonna match
    
        dict = {}
    
        param_file = QtGui.QFileDialog.getOpenFileName(self, 'Open file',DIR_PARAMS)
        
        #this part is just writing the parameters into an empty dictionary, dict
        with open(param_file[0] ,'r') as f:
            
            for line in f :
                if len(line) == 1:
                    pass
                else:
                    #strip() removes the \n, split('\t') return a list whose elements where separated by a \t
                    line = line.strip().split('\t')
                    key = line[0]
                    word = float(line[1])
                    dict[key] = word
        f.close()
        

        
        #now want to send these new values to arduino
        self.WritetoArduino('a', dict['cavPgain'])
        self.WritetoArduino('b', dict['cavIgain'])
        self.WritetoArduino('c', dict['laserPgain'])
        self.WritetoArduino('d', dict['laserIgain'])
        self.WritetoArduino('k', dict['laserDgain'])
        self.WritetoArduino('e', dict['laserfreqsetpoint'])
        self.WritetoArduino('i', dict['cavoffsetpoint'])
        self.WritetoArduino('g', dict['highthreshold'])
        self.WritetoArduino('f', dict['lowthreshold'])
        

        
        #then update what's displayed in the write boxes with the values from the file
        #this doesn't really do anything, just to show you what you've loaded- the update 
        #to arduino section previous should do all the important stuff
        
        self.cavPgainLE.setText(str(dict['cavPgain']))
        self.cavIgainLE.setText(str(dict['cavIgain']))
        self.laserPgainLE.setText(str(dict['laserPgain']))
        self.laserIgainLE.setText(str(dict['laserIgain'] ))
        self.laserDgainLE.setText(str(dict['laserDgain']))
        if self.swaptoms_btn.isChecked(): #display in ms (won't send to arduino in ms)
            self.laserfreqsetpointLE.setText(str(dict['laserfreqsetpoint']))
            self.cavoffsetpointLE.setText(str(np.round(dict['cavoffsetpoint']/84000,4)))
        else:
            self.laserfreqsetpointLE.setText(str(dict['laserfreqsetpoint']))
            self.cavoffsetpointLE.setText(str(dict['cavoffsetpoint']))
        if self.swaptomV_btn.isChecked(): #display in mV (won't send to arduino in mV)
            self.highthresholdLE.setText(str(np.round(dict['highthreshold']/100,4)))
            self.lowthresholdLE.setText(str(np.round(dict['lowthreshold']/100,4)))
        else:
            self.highthresholdLE.setText(str(dict['highthreshold']))
            self.lowthresholdLE.setText(str(dict['lowthreshold']))
        
        #then change colour of write boxes to show that there's been an update that hasn't been transferred to the read boxes
        #should then press read values to pull the now updated values from the arduino directly into the read boxes
        self.cavPgainLE.setStyleSheet("border: 1px solid black; background-color : lightcoral")
        self.cavIgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        self.laserPgainLE.setStyleSheet("border: 1px solid black; background-color : peachpuff")
        self.laserIgainLE.setStyleSheet("border: 1px solid black; background-color : lemonchiffon")
        self.laserDgainLE.setStyleSheet("border: 1px solid black; background-color : palegreen")
        self.laserfreqsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightcyan")
        self.cavoffsetpointLE.setStyleSheet("border: 1px solid black; background-color : paleturquoise")
        self.highthresholdLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.lowthresholdLE.setStyleSheet("border: 1px solid black; background-color : plum")
        
        
        
    def cavPgainChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            print('cavPgain change whilst tracker running')
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.cavPgainLE.text())
            self.ctrl['key'] = 'a'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('a', self.cavPgainLE.text())

        #change colour to alert to an edit
        self.cavPgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def cavIgainChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.cavIgainLE.text())
            self.ctrl['key'] = 'b'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('b', self.cavIgainLE.text())
        
        #change colour to alert to an edit
        self.cavIgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserPgainChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.laserPgainLE.text())
            self.ctrl['key'] = 'c'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('c', self.laserPgainLE.text())
        
        #change colour to alert to an edit
        self.laserPgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserIgainChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.laserIgainLE.text())
            self.ctrl['key'] = 'd'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('d', self.laserIgainLE.text())
        
        #change colour to alert to an edit
        self.laserIgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    def laserDgainChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.laserDgainLE.text())
            self.ctrl['key'] = 'k'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('k', self.laserDgainLE.text())
        
        #change colour to alert to an edit
        self.laserDgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserfreqsetpointChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.tempstorageLFSP) #using temp storage to ensure that only values in AU are sent to arduino
            self.ctrl['key'] = 'e'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('e', self.tempstorageLFSP)
        #change colour to alert to an edit
        self.laserfreqsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def cavoffsetpointChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.tempstorageCOSP) #using temp storage to ensure that only values in AU are sent to arduino
            self.ctrl['key'] = 'i'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('i', self.tempstorageCOSP) 
        #change colour to alert to an edit
        self.cavoffsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    
    def highthresholdChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.tempstorageHT) #using temp storage to ensure that only values in AU are sent to arduino
            self.ctrl['key'] = 'g'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('g', self.tempstorageHT)
        
        #change colour to alert to an edit
        self.highthresholdLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    
    def lowthresholdChangeText(self):
        #this occurs when enter pressed in this LE
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(self.tempstorageLT) #using temp storage to ensure that only values in AU are sent to arduino
            self.ctrl['key'] = 'f'
        else:
        #want to send the new value to arduino
            self.WritetoArduino('f', self.tempstorageLT)
        
        #change colour to alert to an edit
        self.lowthresholdLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    

    def WhenmsChecked(self):
        #this occurs when the ms swap units box is checked
        #just changes how the value is displayed, doesn't alter the actual value being stored and sent to arduino
        if self.swaptoms_btn.isChecked():
            #swapping to ms
            self.label_cavoffsetpointLE.setStyleSheet("color : deeppink")
            
            #change the units that things are displayed in:
            #read boxes 
            self.laserfreqsetpointMS = float(self.laserfreqsetpoint)#/84000
            self.laserfreqsetpointvalue.setText(str(np.round(self.laserfreqsetpointMS,3)))
            #write box
            self.tempstorageLFSP = self.laserfreqsetpointLE.text()
            LFSPinms = float(self.tempstorageLFSP)#/84000
            self.laserfreqsetpointLE.setText(str(np.round(LFSPinms,3)))
           
            #read boxes
            self.cavoffsetpointMS = float(self.cavoffsetpoint)/84000
            self.cavoffsetpointvalue.setText(str(np.round(self.cavoffsetpointMS,3)))
            #write box
            self.tempstorageCOSP = self.cavoffsetpointLE.text()
            COSPinms = float(self.tempstorageCOSP)/84000
            self.cavoffsetpointLE.setText(str(np.round(COSPinms,3)))
            
                
        else:
            #swap to AU
            self.label_laserfreqsetpointLE.setStyleSheet("color : black")
            self.label_cavoffsetpointLE.setStyleSheet("color : black")
            
            #read boxes
            self.laserfreqsetpointvalue.setText(str(np.round(float(self.laserfreqsetpoint),3)))
            self.cavoffsetpointvalue.setText(str(np.round(float(self.cavoffsetpoint),3)))
        
            #write box
            self.laserfreqsetpointLE.setText(str(np.round(float(self.tempstorageLFSP),3)))
            self.cavoffsetpointLE.setText(str(np.round(float(self.tempstorageCOSP),3)))
        
    def TextEditmsUnitSortOut(self):
        #this should take care of units when you're typing the value in in ms
        #will set the AU version to the tempstorage variable that is actually sent to arduino etc
        if self.swaptoms_btn.isChecked():
            #then we're writing in ms
            placeholder = self.laserfreqsetpointLE.text()
            self.tempstorageLFSP = float(placeholder)#*84000
            placeholder2 = self.cavoffsetpointLE.text()
            self.tempstorageCOSP = float(placeholder2)*84000
        else:
            #we're writing in AU
            self.tempstorageLFSP = self.laserfreqsetpointLE.text()
            self.tempstorageCOSP = self.cavoffsetpointLE.text()
            
    def TextEditmVUnitSortOut(self):
        #this should take care of units when you're typing the value in in mV
        #will set the AU version to the tempstorage variable that is actually sent to arduino etc
       
        if self.swaptomV_btn.isChecked():
            #then we're writing in mV
            placeholder = self.highthresholdLE.text()
            self.tempstorageHT = float(placeholder)*100
            placeholder2 = self.lowthresholdLE.text()
            self.tempstorageLT = float(placeholder2)*100
        else:
            #we're writing in AU
            self.tempstorageHT = self.highthresholdLE.text()
            self.tempstorageLT = self.lowthresholdLE.text()
        
        
    def WhenmVChecked(self):
        #this occurs when the mV swap units box is checked
        #just changes how the value is displayed, doesn't alter the actual value being stored and sent to arduino
        if self.swaptomV_btn.isChecked():
            #in mV
            self.label_highthresholdLE.setStyleSheet("color : deeppink")
            self.label_lowthresholdLE.setStyleSheet("color : deeppink")
            
            #change the units that things are displayed in:
            #read boxes
            self.highthresholdMS = float(self.highthreshold)/100
            self.highthresholdvalue.setText(str(np.round(self.highthresholdMS,3)))
            #write box
            self.tempstorageHT = self.highthresholdLE.text()
            HTinms = float(self.tempstorageHT)/100
            self.highthresholdLE.setText(str(np.round(HTinms,3)))
           
            #read boxes
            self.lowthresholdMS = float(self.lowthreshold)/100
            self.lowthresholdvalue.setText(str(np.round(self.lowthresholdMS,3)))
            #write box
            self.tempstorageLT = self.lowthresholdLE.text()
            LTinms = float(self.tempstorageLT)/100
            self.lowthresholdLE.setText(str(np.round(LTinms,3)))
            
                
        else:
            #in AU
            self.label_lowthresholdLE.setStyleSheet("color : black")
            self.label_highthresholdLE.setStyleSheet("color : black")
            
            #read boxes
            self.highthresholdvalue.setText(str(np.round(float(self.highthreshold),3)))
            self.lowthresholdvalue.setText(str(np.round(float(self.lowthreshold),3)))
        
            #write box
            self.highthresholdLE.setText(str(np.round(float(self.tempstorageHT),3)))
            self.lowthresholdLE.setText(str(np.round(float(self.tempstorageLT),3)))
            
            
            
    def WritetoArduino(self, key, value):
        #updates parameters in the arduino
        #key here should specify which value you're trying to send to arduino
        #value is the new value you want to send 
        
        comport = self.parameter_loop_comboBox.currentText()
        
        message = 'm' + str(key) + str(value) + '!' #encode given data into a message the arduino can understand
        
        try:
            arduino = serial.Serial(comport, self.baudrate, timeout=.1)
            
            arduino.write(str.encode(message)) #send this message to the arduino, activates the message_parser function
            
            arduino.close()
        except (OSError, serial.SerialException):
            print('whoops the arduino is not there') 


    def LockBtn(self):
        #set the bump variable to low/high depending on what we want to do
        comport = self.parameter_loop_comboBox.currentText()
        if self.startloopbtn.isChecked(): #if we're running the loop, gotta do comm in worker thread
            self.ctrllock['break'] = True #signal that this worker comm needs to happen
            
            if self.lock_btn.isChecked(): #depending on what the lock btn is doing, send instructions
                self.ctrllock['value'] = 'nolock'
            else:
                self.ctrllock['value'] = 'lock' 
                
        else:
            if self.lock_btn.isChecked():
                #ie if button is unpressed - no lock
                print(f'no lock: {self.lock_btn.isChecked()}')
                try:
                    arduino = serial.Serial(comport, self.baudrate, timeout=.1) 
                    arduino.write(str.encode('mh0!'))
                    
                    arduino.close()
                    
    
                except (OSError, serial.SerialException):
                    print('whoops the arduino is not there')
            else:
                #button pressed- lock engaged
                print(f'thats a lock folks: {self.lock_btn.isChecked()}')
                try:
                    arduino = serial.Serial(comport, self.baudrate, timeout=.1) 
                    arduino.write(str.encode('mh1!'))
                    
                    arduino.close()
                    
    
                except (OSError, serial.SerialException):
                    print('whoops the arduino is not there')
            
            
            
            
################################################################################
           #readout related functions
################################################################################








    def ExtractPeakPos(self):
      #Extract the values of the peak postions being stored in the arduino
      comport = self.parameter_loop_comboBox.currentText()

      try:
          arduino = serial.Serial(comport, self.baudrate, timeout=.1)
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
      #talk to the arduino, get the peak pos
      if self.startloopbtn.isChecked() == False:
          self.ExtractPeakPos()
      
      #update the labels here- taking care to use the selected units
      if self.swaptoms_btn.isChecked(): #ie if we want ms
          newunitpeak1pos = float(self.peak1pos)/(84*1000000*10**-3)
          newunitpeak2pos = float(self.peak2pos)/(84*1000000*10**-3)
          newunitpeak3pos = float(self.peak3pos)/(84*1000000*10**-3)
          self.peak1posvalue.setText(str(round(newunitpeak1pos,3)))
          self.peak2posvalue.setText(str(round(newunitpeak2pos,3)))
          self.peak3posvalue.setText(str(round(newunitpeak3pos,3)))
      else: #in AU
          self.peak1posvalue.setText(str(round(float(self.peak1pos),3)))
          self.peak2posvalue.setText(str(round(float(self.peak2pos),3)))
          self.peak3posvalue.setText(str(round(float(self.peak3pos),3)))
          
    
    def UpdateInternalPeakPos(self, peakvalues):
        #should update the internal peak values as the loop is occuring
        self.peak1pos = peakvalues[0]
        self.peak2pos = peakvalues[1]
        self.peak3pos = peakvalues[2]
        
        
          
     
    def ExtractError(self):
      #talk to the arduino and extract the values of the error
      comport = self.parameter_loop_comboBox.currentText()
    
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
      #occurs when the 'errors?' button is pressed
      #talk to arduino and get the values out
      self.ExtractError()
      #update the display
      self.laser_error.setText(str(self.currentlasererror))
      self.cav_error.setText(str(self.currentcaverror))
      
    
    def PlotPeaks(self):
    #this occurs when the 'peaks?' button is pressed, and plots the current peak positions in the little 
    #horizontal graph
    
      self.ExtractPeakPos()
      
    # clearing old figure
      self.figure.clear()
      
    # create an axis
      ax = self.figure.add_subplot(111)
      self.figure.subplots_adjust(0.05, 0.4, 0.95, 0.95) # left,bottom,right,top 
      ax.tick_params(left = False, labelleft=False)
      
      #take care of the units
      if self.swaptoms_btn.isChecked():
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
      

          
    def UpdatePeakTracker(self):
      #starts the worker thread, so will start the data taking loop and then plot the data if requested
      
      if self.startloopbtn.isChecked():
          #clear the graphs to allow new data to be plotted
          self.axPPOT.clear()
          self.axEOT.clear()
          self.axEOT2.clear()
          self.lasererrorvalues.clear()
          self.caverrorvalues.clear()
          
          #setting something to check whether we should be plotting in ms or AU
          if self.swaptoms_btn.isChecked():
              self.plotinms = True
          else:
              self.plotinms = False
          
          #generate the worker thread 
          self.thread = QtCore.QThread()
          self.worker = PeakPosTrackerThread(self.ctrl, self.readctrl, self.ctrllock, self.stopctrl, self.ctrllocklaser, self.ctrllockcav, self.ctrlpeakdisplay, self.parameter_loop_comboBox.currentText())
          self.worker.moveToThread(self.thread)
          
          
          #this should ensure the data loop task will be called automatically when the function is called
          self.thread.started.connect(self.worker.TASK)
          
          #then plot data if the associated button is pressed
          if self.peaktrackerbtn.isChecked():
              self.worker.updated.connect(self.PlotPeakTrackerGraph)
              self.axPPOT.set_xlabel('Time (s)')
              if self.plotinms:
                  self.axPPOT.set_ylabel('Peak pos (ms)')
              else:
                  self.axPPOT.set_ylabel('Peak pos (AU)')
          if self.errortrackerbtn.isChecked():
              self.worker.updated.connect(self.PlotErrorTrackerGraph)
              self.axEOT.set_xlabel('Time (s)')
              self.axEOT.set_ylabel('Laser error')
              self.axEOT2.set_xlabel('Time (s)')
              self.axEOT2.set_ylabel('Cavity error')
              
              
          #update the internal peak params
          self.worker.updated.connect(self.UpdateInternalPeakPos)
          #save the data each time the loop comes round
          self.worker.updated.connect(self.SavePeakPosAndError)
          #calculate and display the cumulative RMS errors
          self.worker.updated.connect(self.CalcRMSErrors)
          #when the parameter values from the arduino have been extracted,
          #trigger the function that displays them 
          self.worker.readvalues.connect(self.UpdateAfterRead)
          
          #when the thread is finished, quit and delete
          self.worker.finished.connect(self.thread.quit)
          self.worker.finished.connect(self.worker.deleteLater)
          self.thread.finished.connect(self.thread.deleteLater)
          
          
          
          #start the thread
          self.thread.start()
      else:
          pass
      
    def PlotPeakTrackerGraph(self, peakvalues):
      #takes the peak position values from the worker thread and plots them
        
        print('try to plot')
        toplot1 = peakvalues[0]
        toplot2 = peakvalues[1]
        toplot3 = peakvalues[2]
        time = peakvalues[3]
        print(f'{[toplot1, toplot2, toplot3, time]}')
        
        #take care of units
        if self.plotinms: 
            self.axPPOT.scatter(time, float(toplot1)/84000, color='deeppink', s=0.7)
            self.axPPOT.scatter(time, float(toplot2)/84000, color='darkturquoise', s=0.7)
            self.axPPOT.scatter(time, float(toplot3)/84000, color='orange', s=0.7)
        else:
            self.axPPOT.scatter(time, toplot1, color='deeppink', s=0.7)
            self.axPPOT.scatter(time, toplot2, color='darkturquoise', s=0.7)
            self.axPPOT.scatter(time, toplot3, color='orange', s=0.7)
            
        #refresh the canvas
        self.canvasPPOT.draw()
        
    def PlotErrorTrackerGraph(self, errorvalues):
        #takes the error values from the worker thread and plots them
        time = errorvalues[3]
        lasererr = errorvalues[4]
        caverr = errorvalues[5]
        
        print(f'to plot {[lasererr, caverr, time]}')
        
        self.axEOT.scatter(time, lasererr, color='deeppink', s=0.7)
        self.axEOT2.scatter(time, caverr, color='darkturquoise', s=0.7)
        self.canvasEOT.draw()
        self.canvasEOT2.draw()
        
      

      
      
    def SavePeakPosAndError(self, peakvalues):
        #this should be activated when the tracker button is activated, if the save function is toggled on
        #saves the values in order  time, peak pos, errors, to the filename given in the textbox
        
        if self.savereadouttoggle.isChecked():
            filename = self.filenametosave.text()
            toplot1 = peakvalues[0]
            toplot2 = peakvalues[1]
            toplot3 = peakvalues[2]
            time = peakvalues[3]
            lasererr = peakvalues[4]
            caverr = peakvalues[5]
            with open(filename, 'a') as f :
                msg = str(time) + '\n'
                msg += str(toplot1) 
                msg += str(toplot2) 
                msg += str(toplot3) 
                msg += str(lasererr)
                msg += str(caverr)
                f.write(msg)
                print(f'saving this: {msg}')
            f.close()
        else:
            pass
    

        
    
    def SetFilePathToSave(self):
        #occurs when enter is pressed in the filename box, allows you to choose the file
        #where the data will be saved as it is taken
        param_file = QtGui.QFileDialog.getSaveFileName(self, 'Save Params', DIR_READOUT) 
        self.filenametosave.setText(param_file[0])
        
    def StopTracker(self):
        #occurs when the stop loop button called, sends a signal to worker thread to break the loop
        self.stopctrl['break'] = True
        print('set stop to break')
        
        #saving the various graphs if the save data toggle is on
        if  self.savereadouttoggle.isChecked():
            param_file = QtGui.QFileDialog.getSaveFileName(self, 'Save Params', DIR_PEAKPOSPLOT) 
            
            if param_file:
                self.figurePPOT.savefig(param_file[0])
                
            param_fileE = QtGui.QFileDialog.getSaveFileName(self, 'Save Params', DIR_LASERRORPLOT) 
            
            if param_fileE:
                self.figureEOT.savefig(param_fileE[0])
                
            param_fileE2 = QtGui.QFileDialog.getSaveFileName(self, 'Save Params', DIR_CAVERRORPLOT) 
            
            if param_fileE2:
                self.figureEOT2.savefig(param_fileE2[0])

        
        
    def CopyFirstPeakPos(self):
        #transfer the value of the first peak pos from the box to the associated value box
        #ie lock the cavity where it currently is
        firstpeakpos = self.peak1pos
        
        #then just update the display
        if self.swaptoms_btn.isChecked():
            self.cavoffsetpointLE.setText(str(np.round(float(firstpeakpos)/84000,4)))
        else:
            self.cavoffsetpointLE.setText(str(np.round(float(firstpeakpos),4)))
        
        self.cavoffsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(firstpeakpos) 
            self.ctrl['key'] = 'i'
        else:
            #send this new value to arduino 
            self.WritetoArduino('i', firstpeakpos)
    
    def CopyFollowerLaserPos(self):
        #transfer the value of the r calc from current peak pos from the box to the associated value box
        #ie lock the laser where it currently is
        peak1pos = float(self.peak1pos)
        peak2pos = float(self.peak2pos)
        peak3pos = float(self.peak3pos)
        r = (peak2pos-peak1pos)/(peak3pos-peak1pos)
        scaledr = r*10**6
        
        #update the display
        self.laserfreqsetpointLE.setText(str(scaledr))
        self.laserfreqsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
        if self.startloopbtn.isChecked(): #if the peak cycling is active, gotta update the parameter in the loop
            self.ctrl['break'] = True
            self.ctrl['value'] = str(scaledr) 
            self.ctrl['key'] = 'e'
        else:
            #send this value to the arduino
            self.WritetoArduino('e', scaledr)
            
            
        
    def LockJustLaser(self):
        #For locking just the laser - artifically send zero cav gains to the arduino then lock
        
        if self.lockjustlaserbtn.isChecked():
            print('locking')
            #set the storage values to the current internal ones
            self.storagecavIgain = self.cavIgain
            self.storagecavPgain = self.cavPgain
            #send arduino some zero values for cav gain
            if self.startloopbtn.isChecked():
                print('locked while looping')
                #should set the ctrl value
                self.ctrllocklaser['value'] = 'lock'
                self.ctrllocklaser['cavPgain'] = '0'
                self.ctrllocklaser['cavIgain'] = '0'
                self.ctrllocklaser['break'] = True
                
            else:
                self.WritetoArduino('a', 0)
                self.WritetoArduino('b', 0)
                #then send the locking message
                self.WritetoArduino('h', 1)
        else:
            print('unlokcing')
            #set the internal values and the displayed ones to the storage values
            self.cavIgain = self.storagecavIgain 
            self.cavPgain = self.storagecavPgain 
            #read boxes
            self.cavPgainvalue.setText(str(round(float(self.cavPgain),3)))
            self.cavIgainvalue.setText(str(round(float(self.cavIgain),3)))
            #write boxes
            self.cavPgainLE.setText(str(round(float(self.cavPgain),3)))
            self.cavIgainLE.setText(str(round(float(self.cavIgain),3)))
            if self.startloopbtn.isChecked():
                #should set ctrl value
                print('unlocking while looped')
                self.ctrllocklaser['value'] = 'nolock'
                self.ctrllocklaser['cavPgain'] = str(self.cavPgain)
                self.ctrllocklaser['cavIgain'] = str(self.cavIgain)
                self.ctrllocklaser['break'] = True
            else:
                #unlock the arduino
                self.WritetoArduino('h', 0)
                #send new values to arduino
                self.WritetoArduino('a', self.cavPgain)
                self.WritetoArduino('b', self.cavIgain)
            
            
    def LockJustCavity(self):      
        #locking just the cavity by setting the laser gains to 0
    
        if self.lockjustcavbtn.isChecked():
            print('locking')
            #set the storage values to the current internal ones
            self.storagelaserPgain = self.laserPgain
            self.storagelaserIgain = self.laserIgain
            self.storagelaserDgain = self.laserDgain
            #send arduino some zero values for cav gain
            if self.startloopbtn.isChecked():
                print('locked while looping')
                #should set the ctrl value
                self.ctrllockcav['value'] = 'lock'
                self.ctrllockcav['laserPgain'] = '0'
                self.ctrllockcav['laserIgain'] = '0'
                self.ctrllockcav['laserDgain'] = '0'
                self.ctrllockcav['break'] = True
                
            else:
                self.WritetoArduino('c', 0)
                self.WritetoArduino('d', 0)
                self.WritetoArduino('k', 0)
                #then send the locking message
                self.WritetoArduino('h', 1)
        else:
            print('unlokcing')
            #set the internal values and the displayed ones to the storage values
            self.laserPgain = self.storagelaserPgain
            self.laserIgain = self.storagelaserIgain
            self.laserDgain = self.storagelaserDgain
            
            #read boxes
            self.laserPgainvalue.setText(str(round(float(self.laserPgain),3)))
            self.laserIgainvalue.setText(str(round(float(self.laserIgain),3)))
            self.laserDgainvalue.setText(str(round(float(self.laserDgain),3)))
            #write boxes
            self.laserPgainLE.setText(str(round(float(self.laserPgain),3)))
            self.laserIgainLE.setText(str(round(float(self.laserIgain),3)))
            self.laserDgainLE.setText(str(round(float(self.laserDgain),3)))
            
            if self.startloopbtn.isChecked():
                #should set ctrl value
                print('unlocking while looped')
                self.ctrllockcav['value'] = 'nolock'
                self.ctrllockcav['laserPgain'] = str(self.laserPgain)
                self.ctrllockcav['laserIgain'] = str(self.laserIgain)
                self.ctrllockcav['laserDgain'] = str(self.laserDgain)
                self.ctrllockcav['break'] = True
            else:
                #unlock the arduino
                self.WritetoArduino('h', 0)
                #send new values to arduino
                self.WritetoArduino('c', self.laserPgain)
                self.WritetoArduino('d', self.laserIgain)
                self.WritetoArduino('k', self.laserDgain)
                
                
                
    def CalcRMSErrors(self, peakvalues): 
        #calulating the cumulative RMS errors
        
        lasererr = peakvalues[4]
        caverr = peakvalues[5]
        self.lasererrorvalues.append(float(lasererr.strip()))
        self.caverrorvalues.append(float(caverr.strip()))
        
        print(self.lasererrorvalues)
        rmslasererr = np.sqrt((np.sum(np.array(self.lasererrorvalues)**2))/len(self.lasererrorvalues))
        rmscaverr = np.sqrt((np.sum(np.array(self.caverrorvalues)**2))/len(self.caverrorvalues))
        
        print(rmslasererr)
        #then want to display then somewhere in the GUi
        self.laserRMSvalue.setText(str(rmslasererr))
        self.cavRMSvalue.setText(str(rmscaverr))