# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 10:48:49 2022

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
from PyQt5.QtWidgets import QMessageBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import time
import datetime
from random import randint


import serial
import serial.tools.list_ports
current_time = datetime.datetime.now()  
USUAL_DIR = os.getcwd()

DATEMARKER = str(current_time.day) + '-' + str(current_time.month) + '-' + str(current_time.year) + '-' + str(current_time.hour) + 'h' + str(current_time.minute) 

from PyQt5.QtGui import QFont
DIR_READOUT = USUAL_DIR+f'//({DATEMARKER})_channeldata'

# using now() to get current time



class PeakPosTrackerThread(QtCore.QObject):
    #signals here- emitted to the main thread to alert to something going on here
    updated = QtCore.pyqtSignal(list)
    readvalues = QtCore.pyqtSignal(list)
    finished = QtCore.pyqtSignal()
    updatederr = QtCore.pyqtSignal(list)
    
    
    def __init__(self, ctrl, comport, channelctrl):
        QtCore.QThread.__init__(self)
        
        #various control parameters that allow control from the main thread 
        #ie will switch communication to the arduino to this worker thread when the loop is running
        #stops issues that come up when you try to speak to the arduino when it's speaking
        self.ctrl = ctrl
        self.channelctrl = channelctrl
        
        
        
        self.comport = comport

        self.arduino = serial.Serial(comport, 230400, timeout=.1) #open the serial communication
        
    
    def TASK(self):
        self.ctrl['break'] = False
        
        #the data taking loop
        
        try:
            print('COM port open in talking')
            
            starttime = time.time() #find the time at which the data taking starts
            
            while time.time()< (starttime+480): 
               # print("tick")
                time.sleep(0.01)
                
                self.arduino.write(str.encode('pl!'))
                while self.arduino.inWaiting() == 0:
                    pass #print('nothing yet')
                if self.arduino.inWaiting() > 0:
                    alldata = self.arduino.readline()
                    alldata = alldata.decode().strip().split(',')
                    print(f'( {alldata} )')
                
                
                #emit a signal to the main thread that has the peak position, error and time data
                #triggers the plotting/saving functions
                self.updated.emit([float(alldata[0]), float(alldata[1]), float(alldata[2]), float(alldata[3]), time.time()-starttime]) #emit a signal to say it's been updated!
                
                #controls how often the data is sampled- here it's every second
                time.sleep(0.01 - ((time.time() - starttime) % 0.01))
                
                if self.channelctrl['break']:
                    message = 'o' + 'a' + self.channelctrl['chnl'] + self.channelctrl['value'] + '!' #encode given data into a message the arduino can understand
                    #time.sleep(10**-25)
                    #message2 = 'm' + 'b' + self.channelctrl['value'] + '!'
                    
                    try:
                        self.arduino.write(str.encode(message)) #send this message to the arduino, activates the message_parser function
                        #self.arduino.write(str.encode(message2))
                        print(f'yep we wrote a message: {message}')
                        print(time.time()-starttime)
                        #print(f'yep we wrote a message: {message2}')
                        
                    except (OSError, serial.SerialException):
                        print('whoops the arduino is not there test edition')
                    
                    self.channelctrl['break'] = False
                
                    
                if self.ctrl['break']:
                    #if the stop loop button is pressed, or the window is closed, break from the loop
                    print('finished loop bc flag raised')
                    break                    
                            
            #once exited the loop, close the serial connection and emit the finished signal so thread etc can be deleted
            self.arduino.close()
            print('port closed in talking')
            self.finished.emit()
        except (OSError, serial.SerialException):
            print('LOOP version whoops the arduino is not there')



class PlotOutputs(QtGui.QMainWindow):

    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)
        self.parentGui = parent
        #self.sampling_rate = 250
        self.initUI()

    def initUI(self):
        
        #setting placeholder values for the various parameters
        self.w = None
        
        self.A0 = 0
        self.A1 = 1
        self.A2 = 2
        self.A3 = 3
        self.A4 = 4
        self.A5 = 5
        self.A6 = 6
        self.A7 = 7
        
        self.ctrl = {'break': False, 'value': '120', 'key': 'b'}
        self.channelctrl = {'break': False, 'value': '0', 'chnl': '0'}
        

        
        #baudrate for serial communication over the native port of the arduino
        self.baudrate = 230400
        
        
        
        #self.general_things = upkeep.Upkeep(self)
        


        
        self.peakpos1storage = []
        self.peakpos2storage = []
        self.peakpos3storage = []
        self.highthresholdstorage = []
        


        
        #GUI
        self.area = dockarea.DockArea()
        self.setCentralWidget(self.area)
        self.resize(100,100)
        self.setWindowTitle('Adiabatic')
        self.createDocks()
        
    def createDocks(self):
            self.d1 = dockarea.Dock("AWG", size=(300,200))
            self.d1.hideTitleBar()
            
            
            
            
            
            
            self.w3 = pg.LayoutWidget()

            self.figure = plt.figure(facecolor='ghostwhite', frameon = True, figsize=(10,2))
            self.canvas = FigureCanvas(self.figure)
            self.ax = self.figure.add_subplot(111)
            self.figure.subplots_adjust(0.15, 0.15, 0.95, 0.95) # left,bottom,right,top 
            self.ax.set_ylabel('Analog output')
            self.ax.set_xlabel('Time (s)')
            
            self.startloopbtn = QtGui.QPushButton('Start record')
            self.startloopbtn.setCheckable(True)
            self.startloopbtn.clicked.connect(self.UpdatePeakTracker)
            
            
            self.parameter_loop_comboBox = QtGui.QComboBox() 
            #finding all the available COM ports and adding their names to the drop down menu
            list_serialports = serial.tools.list_ports.comports()
            for n in range(len(list_serialports)):
                test = list_serialports[n][0]
                self.parameter_loop_comboBox.addItem(str(test)) 
                
                
            self.choosechannel = QtGui.QComboBox()
            for n in range(8):
                self.choosechannel.addItem(str(n))
            self.chooseoutput = QtGui.QLineEdit()
            self.chooseoutput.returnPressed.connect(self.ChangeChannel)
            
            self.filenamebox = QtGui.QLineEdit('filename')
            self.filenamebox.returnPressed.connect(self.SetFilePathToSave)

            self.w3.addWidget(self.canvas, row=3, col=0, colspan=2)
            self.w3.addWidget(self.startloopbtn, row=0, col=0)
            self.w3.addWidget(self.parameter_loop_comboBox, row=0, col=1)
            self.w3.addWidget(self.choosechannel, row=1, col=0)
            self.w3.addWidget(self.chooseoutput, row=1,col=1)
            self.w3.addWidget(self.filenamebox, row =2, col=0, colspan=2)
            
            self.d1.addWidget(self.w3, row=0, col=0)
            
            
    def OutputGraph(self, values):
      #takes the peak position values from the worker thread and plots them
      
        '''comport = self.parameter_loop_comboBox.currentText()
        self.arduino = serial.Serial(comport, 230400, timeout=.1)
      
        if self.startloopbtn.isChecked():
            print('try to plot')
            starttime = time.time() #find the time at which the data taking starts
            
            while time.time()< (starttime+360): 
                print("tick")
                
                #set peak 1
                self.arduino.write(str.encode('pa!'))
                self.A0 = self.arduino.readline()
                self.A0 = float(self.A0.decode().strip())
                
                #set peak 2
                self.arduino.write(str.encode('pb!'))
                self.A1 = self.arduino.readline()
                
                #set peak 3
                self.arduino.write(str.encode('pc!'))
                self.A2 = self.arduino.readline()
                
                #getting the error data
                self.arduino.write(str.encode('pd!'))
                self.A3 = self.arduino.readline()
                
                self.arduino.write(str.encode('pe!'))
                self.A4 = self.arduino.readline()
                            
                #set peak 3
                self.arduino.write(str.encode('pf!'))
                self.A5 = self.arduino.readline()
                
                #getting the error data
                self.arduino.write(str.encode('pg!'))
                self.A6 = self.arduino.readline()
                
                self.arduino.write(str.encode('ph!'))
                self.A7 = self.arduino.readline()
                
                #emit a signal to the main thread that has the peak position, error and time data
                #triggers the plotting/saving functions
                #self.updated.emit([peak1pos.decode(), peak2pos.decode(), peak3pos.decode(), time.time()-starttime, lasererror.decode(), caverror.decode()]) #emit a signal to say it's been updated!
                t = time.time()-starttime
                #controls how often the data is sampled- here it's every second
                time.sleep(1 - ((time.time() - starttime) % 1))'''
                
        self.SaveOutputs(values) 
            
            #take care of units
        #print(values)   
        '''self.A0 = values[0]
        self.A1 = values[1]
        self.A2 = values[2]
        self.A3 = values[3]
        self.A4 = values[4]
        self.A5 = values[5]
        self.A6 = values[6]
        self.A7 = values[7]
        t = values[8]'''
            
        '''self.ax.scatter(t, float(self.A0), color='lightcoral')
        self.ax.scatter(t, float(self.A1), color='lightsalmon')
        self.ax.scatter(t, float(self.A2), color='peachpuff')
        self.ax.scatter(t, float(self.A3), color='lemonchiffon', s=0.7)
        self.ax.scatter(t, float(self.A4), color='palegreen', s=0.7)
        self.ax.scatter(t, float(self.A5), color='lightcyan', s=0.7)
        self.ax.scatter(t, float(self.A6), color='paleturquoise', s=0.7)
        self.ax.scatter(t, float(self.A7), color='plum', s=0.7)'''
            
            #print(t)
        #print([self.A0, self.A1, self.A2, self.A3, self.A4, self.A5, self.A6, self.A7])
                
          
            
        #refresh the canvas
        self.canvas.draw()
        
            
    def UpdatePeakTracker(self):
      #starts the worker thread, so will start the data taking loop and then plot the data if requested
      
      if self.startloopbtn.isChecked():
          #clear the graphs to allow new data to be plotted
          self.ax.clear()


          
          #generate the worker thread 
          self.thread = QtCore.QThread()
          self.worker = PeakPosTrackerThread(self.ctrl, self.parameter_loop_comboBox.currentText(), self.channelctrl)
          self.worker.moveToThread(self.thread)
          
          
          #this should ensure the data loop task will be called automatically when the function is called
          self.thread.started.connect(self.worker.TASK)
          
          #then plot data if the associated button is pressed
          #if self.peaktrackerbtn.isChecked():
          self.worker.updated.connect(self.OutputGraph)
             # self.axPPOT.set_xlabel('Time (s)')
             # if self.plotinms:
             #     self.axPPOT.set_ylabel('Peak pos (ms)')
             # else:
             #     self.axPPOT.set_ylabel('Peak pos (AU)')
         
              
              
          #update the internal peak params
          #self.worker.updated.connect(self.UpdateInternalPeakPos)
          #save the data each time the loop comes round
          #self.worker.updated.connect(self.SavePeakPosAndError)
          #calculate and display the cumulative RMS errors
          #self.worker.updated.connect(self.CalcRMSErrors)
          #when the parameter values from the arduino have been extracted,
          #trigger the function that displays them 
          #self.worker.readvalues.connect(self.UpdateAfterRead)
          
          #when the thread is finished, quit and delete
          self.worker.finished.connect(self.thread.quit)
          self.worker.finished.connect(self.worker.deleteLater)
          self.thread.finished.connect(self.thread.deleteLater)
          
          
          
          #start the thread
          self.thread.start()
      else:
          pass
      
    def StopTracker(self):
        #occurs when the stop loop button called, sends a signal to worker thread to break the loop
        self.ctrl['break'] = True
        print('set stop to break')
        
    def ChangeChannel(self):
        channel = self.choosechannel.currentText()
        value = self.chooseoutput.text()
        
        #move communication to the loop
        if self.startloopbtn.isChecked():
            self.channelctrl['break'] = True
            self.channelctrl['chnl'] = channel
            self.channelctrl['value'] = value
            
            
    def SaveOutputs(self, values):
        #this should be activated when the tracker button is activated, if the save function is toggled on
        #saves the values in order  time, peak pos, errors, to the filename given in the textbox
        
        #if self.savereadouttoggle.isChecked():
        filename = self.filenamebox.text()
        A0 = values[0]
        A1 = values[1]
        A0status = values[2]
        A1status = values[3]
        time = values[4]
        
        with open(filename, 'a') as f :
            msg = str(A0) + '\n'
            msg += str(A1) + '\n'
            msg += str(A0status) + '\n'
            msg += str(A1status) + '\n'
            msg += str(time) + '\n'
            f.write(msg)
            print(f'saving this: {msg}')
        f.close()
    #else:
     #   pass
    
    
        
    
    def SetFilePathToSave(self):
        #occurs when enter is pressed in the filename box, allows you to choose the file
        #where the data will be saved as it is taken
        param_file = QtGui.QFileDialog.getSaveFileName(self, 'Save Params', DIR_READOUT) 
        self.filenamebox.setText(param_file[0])
                        
                    
                    