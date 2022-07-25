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

from PyQt5.QtGui import QFont

import upkeep
USUAL_DIR = os.getcwd()
print(USUAL_DIR)

DIR_PARAMS = USUAL_DIR+'//lock_params'

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
            self.label_laserfreqsetpointLE = QtGui.QLabel('Laser setpoint')
            self.laserfreqsetpointvalue = QtGui.QLabel(str(self.laserfreqsetpoint))
            self.laserfreqsetpointvalue.setStyleSheet("border: 1px solid black")
            
            self.cavoffsetpointLE = QtGui.QLineEdit(str(self.cavoffsetpoint))
            self.cavoffsetpointLE.returnPressed.connect(self.cavoffsetpointChangeText)
            self.label_cavoffsetpointLE = QtGui.QLabel('Cavity setpoint')
            self.cavoffsetpointvalue = QtGui.QLabel(str(self.cavoffsetpoint))
            self.cavoffsetpointvalue.setStyleSheet("border: 1px solid black")
            
            self.highthresholdLE = QtGui.QLineEdit(str(self.highthreshold))
            self.highthresholdLE.returnPressed.connect(self.highthresholdChangeText)
            self.label_highthresholdLE = QtGui.QLabel('High threshold')
            self.highthresholdvalue = QtGui.QLineEdit(str(self.highthreshold))
            self.highthresholdvalue.setStyleSheet("border: 1px solid black")
            
            self.lowthresholdLE = QtGui.QLineEdit(str(self.lowthreshold))
            self.lowthresholdLE.returnPressed.connect(self.lowthresholdChangeText)
            self.label_lowthresholdLE = QtGui.QLabel('Low threshold')
            self.lowthresholdvalue = QtGui.QLabel(str(self.lowthreshold))
            self.lowthresholdvalue.setStyleSheet("border: 1px solid black")
            
            self.blankspace= QtGui.QLabel('')
            
            self.saveparamsbtn = QtGui.QPushButton('Save parameters?')
            self.saveparamsbtn.setStyleSheet(':hover { background: papayawhip }')
    
    
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
            
            
            self.w1.addWidget(self.blankspace, row = 12, col= 0, colspan= 4) #this is literally just to help with the spacing
            
          
            self.d1.addWidget(self.w1, row=0, col=0)
           # self.d1.addWidget(self.w2, row=0, col=2)
           
           ############################################################################
           
           #reading data from the arduino
    #def Readfromarduino():
    #    comport = upkeep.parameter_loop_comboBox.currentText()
    #    print(comport)
               #arduino = serial.Serial('COM1', self.baudrate, timeout=.1)
#while True:
#	data = arduino.readline()[:-2] #the last bit gets rid of the new-line chars
#	if data:
#		print data
   # Readfromarduino()
   
   
    def GenerateParamDict(self):
        #should read the values and then put them into a dictionary, ready to be saved
        #not sure whether I should just commit to storing them as a dictionary normally?
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
        print(dict) ##WAIT!! want to be able to read the values from the read boxes!!
        

        

    def SaveParameters(self): #this will happen after the talking to the arduino bit, and updating the values- so the dict part should be actively saving the new values
        #want this to happen when you click the button, and also when you press lock if the box is checked
        dict = self.GenerateParamDict() 

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
            f.close()
       
        
    def WhenValuesBtnPress(self):
        #should talk to the arduino and update the interal gain values from what we have
        #PUT THIS IN LATER
        
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
       # self.lowthresholdvalue.setStyleSheet("border: 1px solid black, background : None")
        
       
    def LoadParameters(self):
    # occurs when load parameters button is opened
    #choose a file with parameters, then unpack from dictionary
    #set variables to be these new values, send to arduino
    #display new values in the write boxes and change colour of write boxes
        dict = {}
    
        param_file = QtGui.QFileDialog.getOpenFileName(self, 'Open file',DIR_PARAMS)
        
        #this part is just writing the parameters into an empty dictionary, dict
        with open(param_file[0] ,'r') as f:
            for line in f :
                #strip() removes the \n, split('\t') return a list whose elements where separated by a \t
                line = line.strip().split('\t')
                key = line[0]
                word = float(line[1])
                dict[key] = word
        f.close()
        
        print('yup')
        
        #now want to send these new values to arduino
        #PUT THIS IN LATER
        
        #for now, update the internal values directly instead
        self.cavPgain = dict['cavPgain']
        print(f'Updated cav P gain is {self.cavPgain}')
        self.cavIgain = dict['cavIgain']
        self.laserPgain = dict['laserPgain']
        self.laserIgain = dict['laserIgain'] 
        self.laserDgain = dict['laserDgain']
        self.laserfreqsetpoint = dict['laserfreqsetpoint']
        self.cavoffsetpoint = dict['cavoffsetpoint']
        self.highthreshold = dict['highthreshold']
        self.lowthreshold = dict['lowthreshold']
        
        #then update what's displayed in the write boxes with the values from the file
        #this doesn't really do anything, just to show you what you've loaded- the update to arduino section previous should do all the important stuff
        print(f'What should be in the box = {str(dict["cavPgain"])}')
        self.cavPgainLE.setText(str(dict['cavPgain']))
        self.cavIgainLE.setText(str(dict['cavIgain']))
        self.laserPgainLE.setText(str(dict['laserPgain']))
        self.laserIgainLE.setText(str(dict['laserIgain'] ))
        self.laserDgainLE.setText(str(dict['laserDgain']))
        self.laserfreqsetpointLE.setText(str(dict['laserfreqsetpoint']))
        self.cavoffsetpointLE.setText(str(dict['cavoffsetpoint']))
        self.highthresholdLE.setText(str(dict['highthreshold']))
        self.lowthresholdLE.setText(str(dict['lowthreshold']))
        
        #then change colour of write boxes to show that there's been an update that hasn't been transferred to the read boxes
        #should then press read values to pull the now updated values from the arduino directly into the read boxes
        self.cavPgainLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.cavIgainLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.laserPgainLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.laserIgainLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.laserDgainLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.laserfreqsetpointLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.cavoffsetpointLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.highthresholdLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        self.lowthresholdLE.setStyleSheet("border: 1px solid black; background-color : thistle")
        
        
        
    def cavPgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.cavPgain = self.cavPgainLE.text()
        #print(self.cavPgain)
        #change colour to alert to an edit
        self.cavPgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def cavIgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.cavIgain = self.cavIgainLE.text()
        #print(self.cavPgain)
        #change colour to alert to an edit
        self.cavIgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserPgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.laserPgain = self.laserPgainLE.text()
        #print(self.cavPgain)
        #change colour to alert to an edit
        self.laserPgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserIgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.laserIgain = self.laserIgainLE.text()
        #print(self.cavPgain)
        #change colour to alert to an edit
        self.laserIgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    def laserDgainChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.laserDgain = self.laserDgainLE.text()
        #print(self.cavPgain)
        #change colour to alert to an edit
        self.laserDgainLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def laserfreqsetpointChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.laserfreqsetpoint = self.laserfreqsetpointLE.text()
        #print(self.cavPgain)
        #change colour to alert to an edit
        self.laserfreqsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
        
    def cavoffsetpointChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.cavoffsetpoint = self.cavoffsetpointLE.text()
        #print(self.cavPgain)
        #change colour to alert to an edit
        self.cavoffsetpointLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    
    def highthresholdChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.highthreshold = self.highthresholdLE.text()
        #print(self.cavPgain)
        #change colour to alert to an edit
        self.highthresholdLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    
    def lowthresholdChangeText(self):
        #this occurs when enter pressed in this LE
        
        #want to send the new value to arduino
        #PUT THIS IN LATER
        #for now, update the internal value myself
        self.lowthreshold = self.lowthresholdLE.text()
        
        #change colour to alert to an edit
        self.lowthresholdLE.setStyleSheet("border: 1px solid black; background-color : lightsalmon")
    
    