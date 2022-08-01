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
from datetime import date

import serial
import serial.tools.list_ports

from PyQt5.QtGui import QFont

import upkeep
USUAL_DIR = os.getcwd()
print(USUAL_DIR)
DATEMARKER = str(date.today())

DIR_PARAMS = USUAL_DIR+f'//({DATEMARKER})_lock_params'

'''This bit will allow you to type in new values for the gains etc, and then write them to the arduino'''

class ModifyandRead_variable(QtGui.QMainWindow):

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
        
        self.laserfreqsetpointMS = 0.6
        self.cavoffsetpointMS = 0.7
        self.highthresholdMV = 0.8
        self.lowthresholdMV = 0.9
        
        self.tempstorageLFSP = 10 
        self.tempstorageCOSP = 13
        
        self.tempstorageHT = 100
        self.tempstorageLT = 130
        
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
            ## w1: modify variables
            #######################################################################
    
            self.w1 = pg.LayoutWidget()
            self.label_w1 = QtGui.QLabel('Locking parameters')
            self.label_w1.setFont(QFont('Helvetica', 10))
            self.label_w1.setAlignment(QtCore.Qt.AlignCenter)
            
            #button to load values from a file
            self.load_files_btn = QtGui.QPushButton('Load parameters')
            self.load_files_btn.clicked.connect(self.LoadParameters)
            self.load_files_btn.setStyleSheet(':hover { background: aquamarine }')
            #button to read the values and update them
            self.read_values_btn = QtGui.QPushButton('Values?')
            self.read_values_btn.clicked.connect(self.WhenValuesBtnPress)
            self.read_values_btn.setStyleSheet(':hover { background: lightpink }')
            #checkbox to see if you want to save the parameters
            self.save_params_checkbox = QtGui.QCheckBox('Save parameters?')
    
            
            #creating the boxes to put the values in
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
            
            self.saveparamsbtn = QtGui.QPushButton('Save parameters?')
            self.saveparamsbtn.setStyleSheet(':hover { background: papayawhip }')
    
            self.swapunits_label= QtGui.QLabel('Swap units')
            self.swaptoms_btn = QtGui.QCheckBox('ms?')
            self.swaptoms_btn.stateChanged.connect(self.WhenmsChecked)
            self.swaptomV_btn = QtGui.QCheckBox('mV?')
            self.swaptomV_btn.stateChanged.connect(self.WhenmVChecked)
            
            #test to see if I can get an error message to display
            #self.errordetailtest = QtGui.QLabel('error details here')
    
    
            #buttons at the top
            self.w1.addWidget(self.label_w1, row=0, col=0,colspan = 3)
            self.w1.addWidget(self.load_files_btn, row = 1,col=0, colspan=3)
            self.w1.addWidget(self.read_values_btn, row = 1, col= 3)
            self.w1.addWidget(self.save_params_checkbox, row = 2, col= 1)
            
            #adding in line edit boxes
            self.w1.addWidget(self.cavPgainLE, row = 3, col = 2)
            self.w1.addWidget(self.cavIgainLE, row = 4, col = 2)
            self.w1.addWidget(self.laserPgainLE, row = 5, col = 2)
            self.w1.addWidget(self.laserIgainLE, row = 6, col = 2)
            self.w1.addWidget(self.laserDgainLE, row = 7, col = 2)
            self.w1.addWidget(self.laserfreqsetpointLE, row = 8, col = 2)
            self.w1.addWidget(self.cavoffsetpointLE, row = 9, col = 2)
            self.w1.addWidget(self.highthresholdLE, row = 10, col = 2)
            self.w1.addWidget(self.lowthresholdLE, row = 11, col = 2)
            #labels
            self.w1.addWidget(self.label_cavPgainLE, row = 3, col = 1)
            self.w1.addWidget(self.label_cavIgainLE, row = 4, col = 1)
            self.w1.addWidget(self.label_laserPgainLE, row = 5, col = 1)
            self.w1.addWidget(self.label_laserIgainLE, row = 6, col = 1)
            self.w1.addWidget(self.label_laserDgainLE, row = 7, col = 1)
            self.w1.addWidget(self.label_laserfreqsetpointLE, row = 8, col = 1)
            self.w1.addWidget(self.label_cavoffsetpointLE, row = 9, col = 1)
            self.w1.addWidget(self.label_highthresholdLE, row = 10, col = 1)
            self.w1.addWidget(self.label_lowthresholdLE, row = 11, col = 1)
            # values
            self.w1.addWidget(self.cavPgainvalue, row = 3, col = 3)
            self.w1.addWidget(self.cavIgainvalue, row = 4, col = 3)
            self.w1.addWidget(self.laserPgainvalue, row = 5, col = 3)
            self.w1.addWidget(self.laserIgainvalue, row = 6, col = 3)
            self.w1.addWidget(self.laserDgainvalue, row = 7, col = 3)
            self.w1.addWidget(self.laserfreqsetpointvalue, row = 8, col = 3)
            self.w1.addWidget(self.cavoffsetpointvalue, row = 9, col = 3)
            self.w1.addWidget(self.highthresholdvalue, row = 10, col = 3)
            self.w1.addWidget(self.lowthresholdvalue, row = 11, col = 3)
            
            
            self.w1.addWidget(self.blankspace2, row = 12, col= 0, colspan= 1) #this is literally just to help with the spacing
            
            self.w1.addWidget(self.swaptoms_btn, row = 13, col= 2, colspan= 1) #this is literally just to help with the spacing
            
            self.w1.addWidget(self.swaptomV_btn, row = 13, col= 3, colspan= 1) #this is literally just to help with the spacing
            self.w1.addWidget(self.swapunits_label, row = 13, col= 1, colspan= 1) #this is literally just to help with the spacing
          
            
            self.w1.addWidget(self.blankspace, row = 14, col= 0, colspan= 4) #this is literally just to help with the spacing
            
           # self.w1.addWidget(self.errordetailtest, row = 15, col=0)
          
            self.d1.addWidget(self.w1, row=0, col=0)
           # self.d1.addWidget(self.w2, row=0, col=2)
           
           ############################################################################
           

   
   
    def GenerateParamDict(self):
        #should read the values and then put them into a dictionary, ready to be saved
        #not sure whether I should just commit to storing them as a dictionary normally?
        dict = {}
        dict['cavPgain'] = self.cavPgain
        #dict['lowthreshold'] = self.lowthreshold
        dict['cavIgain'] = self.cavIgain
        dict['laserPgain'] = self.laserPgain
        dict['laserIgain'] = self.laserIgain
        dict['laserDgain'] = self.laserDgain
        dict['laserfreqsetpoint'] = self.laserfreqsetpoint
        dict['cavoffsetpoint'] = self.cavoffsetpoint
        dict['highthreshold'] = self.highthreshold
        dict['lowthreshold'] = self.lowthreshold
        return dict
        print(dict) ##WAIT!! want to be able to read the values from the read boxes!!
        

        

    def SaveParameters(self): #this will happen after the talking to the arduino bit, and updating the values- so the dict part should be actively saving the new values
        #want this to happen when you click the button, and also when you press lock if the box is checked
        dict = self.GenerateParamDict()  #saves the values in arduino units, not ms or mV

        #then need to actually save the parameters
        param_file = QtGui.QFileDialog.getSaveFileName(self, 'Save Params', DIR_PARAMS) 

        if param_file:
            #print('stcl save test')
            #print(param_file)
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
        #choose the COM port to set up for serial communication using the drop down menu
        comport = self.general_things.parameter_loop_comboBox.currentText()

        try:
            arduino = serial.Serial(comport, self.baudrate, timeout=.1)#should hopefully open the serial communication?
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
            #this line isn't doing what it's supposed to :(
            print(self.general_things.errordetails.text())
            #self.errordetailtest.setText('whoops the arduino is not there TEST')
            #self.general_things.errordetails.setText('whoops the arduino is not there UPKEEP')
            print(self.general_things.errordetails.text())
            print(self.errordetailtest.text())
            #upkeep.Upkeep.errordetails.setText('whoops the arduino is not there')
            print('whoops the arduino is not there') 
            
            
 
    
        
    def WhenValuesBtnPress(self):
        #should talk to the arduino and update the interal gain values from what we have
        self.TalktoArduino()
        
        #then present all the updated values in the nice read boxes
        #self.laserfreqsetpointvalue = QtGui.QLabel(str(self.laserfreqsetpoint))
        
        self.cavPgainvalue.setText(str(round(float(self.cavPgain),3)))
        self.cavIgainvalue.setText(str(round(float(self.cavIgain),3)))
        self.laserPgainvalue.setText(str(round(float(self.laserPgain),3)))
        self.laserIgainvalue.setText(str(round(float(self.laserIgain),3)))
        self.laserDgainvalue.setText(str(round(float(self.laserDgain),3)))
        if self.swaptoms_btn.isChecked(): #should these values be loaded in ms or AU
            self.laserfreqsetpointMS = float(self.laserfreqsetpoint)/84000
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
        #self.cavPgainvalue.setStyleSheet("border: 1px solid black")
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
    #choose a file with parameters, then unpack from dictionary
    #set variables to be these new values, send to arduino
    #display new values in the write boxes and change colour of write boxes
        dict = {}
    
        param_file = QtGui.QFileDialog.getOpenFileName(self, 'Open file',DIR_PARAMS)
        #print(f'param_file is {param_file}')
        
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
        
        #for now, update the internal values directly instead
       # self.cavPgain = dict['cavPgain']
       # self.cavIgain = dict['cavIgain']
       # self.laserPgain = dict['laserPgain']
       # self.laserIgain = dict['laserIgain'] 
       # self.laserDgain = dict['laserDgain']
       # self.laserfreqsetpoint = dict['laserfreqsetpoint']
        #self.cavoffsetpoint = dict['cavoffsetpoint']
       # self.highthreshold = dict['highthreshold']
       # self.lowthreshold = dict['lowthreshold']
        print(f'Loaded parameters from {param_file[0]}')
        
        #then update what's displayed in the write boxes with the values from the file
        #this doesn't really do anything, just to show you what you've loaded- the update to arduino section previous should do all the important stuff
        
        self.cavPgainLE.setText(str(dict['cavPgain']))
        self.cavIgainLE.setText(str(dict['cavIgain']))
        self.laserPgainLE.setText(str(dict['laserPgain']))
        self.laserIgainLE.setText(str(dict['laserIgain'] ))
        self.laserDgainLE.setText(str(dict['laserDgain']))
        if self.swaptoms_btn.isChecked(): #display in ms (won't send to arduino in ms)
            self.laserfreqsetpointLE.setText(str(np.round(dict['laserfreqsetpoint']/84000,4)))
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
        
        #want to send the new value to arduino
        self.WritetoArduino('a', self.cavPgainLE.text())

        #change colour to alert to an edit
        self.cavPgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def cavIgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        self.WritetoArduino('b', self.cavIgainLE.text())
        
        #change colour to alert to an edit
        self.cavIgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserPgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        self.WritetoArduino('c', self.laserPgainLE.text())
        
        #change colour to alert to an edit
        self.laserPgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserIgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        self.WritetoArduino('d', self.laserIgainLE.text())
        
        #change colour to alert to an edit
        self.laserIgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    def laserDgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        self.WritetoArduino('k', self.laserDgainLE.text())
        
        #change colour to alert to an edit
        self.laserDgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserfreqsetpointChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        #self.laserfreqsetpoint = self.tempstorageLFSP#self.laserfreqsetpointLE.text()
        #print(self.laserfreqsetpoint)
        self.WritetoArduino('e', self.tempstorageLFSP)
        #change colour to alert to an edit
        self.laserfreqsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def cavoffsetpointChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        self.WritetoArduino('i', self.tempstorageCOSP)
        #change colour to alert to an edit
        self.cavoffsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    
    def highthresholdChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        self.WritetoArduino('g', self.tempstorageHT)
        
        #change colour to alert to an edit
        self.highthresholdLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    
    def lowthresholdChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        self.WritetoArduino('f', self.tempstorageLT)
        
        #change colour to alert to an edit
        self.lowthresholdLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    

    def WhenmsChecked(self):
        #this occurs when the ms swap units box is checked
        #just changes how the value is displayed, doesn't alter the actual value being stored and sent to arduino
        if self.swaptoms_btn.isChecked():
            self.label_laserfreqsetpointLE.setStyleSheet("color : deeppink")
            self.label_cavoffsetpointLE.setStyleSheet("color : deeppink")
            
            #change the units that things are displayed in:
            #read boxes
            self.laserfreqsetpointMS = float(self.laserfreqsetpoint)/84000
            self.laserfreqsetpointvalue.setText(str(np.round(self.laserfreqsetpointMS,3)))
            #write box
            self.tempstorageLFSP = self.laserfreqsetpointLE.text()
            LFSPinms = float(self.tempstorageLFSP)/84000
            self.laserfreqsetpointLE.setText(str(np.round(LFSPinms,3)))
           
            #read boxes
            self.cavoffsetpointMS = float(self.cavoffsetpoint)/84000
            self.cavoffsetpointvalue.setText(str(np.round(self.cavoffsetpointMS,3)))
            #write box
            self.tempstorageCOSP = self.cavoffsetpointLE.text()
            COSPinms = float(self.tempstorageCOSP)/84000
            self.cavoffsetpointLE.setText(str(np.round(COSPinms,3)))
            
                
        else:
            self.label_laserfreqsetpointLE.setStyleSheet("color : black")
            self.label_cavoffsetpointLE.setStyleSheet("color : black")
            
            #read boxes
            self.laserfreqsetpointvalue.setText(str(np.round(float(self.laserfreqsetpoint),3)))
            self.cavoffsetpointvalue.setText(str(np.round(float(self.cavoffsetpoint),3)))
        
            #write box
            self.laserfreqsetpointLE.setText(str(np.round(float(self.tempstorageLFSP),3)))
            self.cavoffsetpointLE.setText(str(np.round(float(self.tempstorageCOSP),3)))
        
    def TextEditmsUnitSortOut(self):
        if self.swaptoms_btn.isChecked():
            #then we're writing in ms
            placeholder = self.laserfreqsetpointLE.text()
            self.tempstorageLFSP = float(placeholder)*84000
            placeholder2 = self.cavoffsetpointLE.text()
            self.tempstorageCOSP = float(placeholder2)*84000
        else:
            #we're writing in AU
            self.tempstorageLFSP = self.laserfreqsetpointLE.text()
            self.tempstorageCOSP = self.cavoffsetpointLE.text()
            
    def TextEditmVUnitSortOut(self):
        if self.swaptomV_btn.isChecked():
            #then we're writing in ms
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
            self.label_lowthresholdLE.setStyleSheet("color : black")
            self.label_highthresholdLE.setStyleSheet("color : black")
            
            #read boxes
            self.highthresholdvalue.setText(str(np.round(float(self.highthreshold),3)))
            self.lowthresholdvalue.setText(str(np.round(float(self.lowthreshold),3)))
        
            #write box
            self.highthresholdLE.setText(str(np.round(float(self.tempstorageHT),3)))
            self.lowthresholdLE.setText(str(np.round(float(self.tempstorageLT),3)))
            
            
            
    def WritetoArduino(self, key, value):
        #key here should specify which value you're trying to send to arduino
        #value is the new value you want to send 
        
        comport = self.general_things.parameter_loop_comboBox.currentText()
        
        message = 'm' + str(key) + str(value) + '!' #encode given data into a message the arduino can understand
        #print(f'message is {message}')
        try:
            arduino = serial.Serial(comport, self.baudrate, timeout=.1)#should hopefully open the serial communication?
            #print('COM port open in talking')
            
            #
            arduino.write(str.encode(message)) #send this message to the arduino, activates the message_parser function
            
            arduino.close()
            #print('port closed in talking')
        except (OSError, serial.SerialException):
            print('whoops the arduino is not there') 