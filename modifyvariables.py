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


'''This bit will allow you to type in new values for the gains etc, and then write them to the arduino'''

class Modify_variable(QtGui.QMainWindow):

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
            ## w1: AWG Steady state settings
            #######################################################################
    
            self.w1 = pg.LayoutWidget()
            self.label_w1 = QtGui.QLabel('Modify gains')
            self.label_w1.setFont(QFont('Helvetica', 10))
            self.label_w1.setAlignment(QtCore.Qt.AlignCenter)
            
            #button to load values from a file
            self.load_files_btn = QtGui.QPushButton('Load parameters')
    
            
            #creating the boxes to put the values in
            self.cavPgainLE = QtGui.QLineEdit(str(self.cavPgain))
            self.label_cavPgainLE = QtGui.QLabel('Cavity P gain')
            self.cavIgainLE = QtGui.QLineEdit(str(self.cavIgain))
            self.label_cavIgainLE = QtGui.QLabel('Cavity I gain')
            self.laserPgainLE = QtGui.QLineEdit(str(self.laserPgain))
            self.label_laserPgainLE = QtGui.QLabel('Laser P gain')
            self.laserIgainLE = QtGui.QLineEdit(str(self.laserIgain))
            self.label_laserIgainLE = QtGui.QLabel('Laser I gain')
            self.laserDgainLE = QtGui.QLineEdit(str(self.laserDgain))
            self.label_laserDgainLE = QtGui.QLabel('Laser D gain')
            self.laserfreqsetpointLE = QtGui.QLineEdit(str(self.laserfreqsetpoint))
            self.label_laserfreqsetpointLE = QtGui.QLabel('Laser setpoint')
            self.cavoffsetpointLE = QtGui.QLineEdit(str(self.cavoffsetpoint))
            self.label_cavoffsetpointLE = QtGui.QLabel('Cavity setpoint')
            self.highthresholdLE = QtGui.QLineEdit(str(self.highthreshold))
            self.label_highthresholdLE = QtGui.QLabel('High threshold')
            self.lowthresholdLE = QtGui.QLineEdit(str(self.lowthreshold))
            self.label_lowthresholdLE = QtGui.QLabel('Low threshold')
            

    
    
            
            self.w1.addWidget(self.label_w1, row=0, col=0,colspan = 3)
            self.w1.addWidget(self.load_files_btn, row = 1,col=0, colspan=3)
            
            #adding in line edit boxes
            self.w1.addWidget(self.cavPgainLE, row = 2, col = 2)
            self.w1.addWidget(self.cavIgainLE, row = 3, col = 2)
            self.w1.addWidget(self.laserPgainLE, row = 4, col = 2)
            self.w1.addWidget(self.laserIgainLE, row = 5, col = 2)
            self.w1.addWidget(self.laserDgainLE, row = 6, col = 2)
            self.w1.addWidget(self.laserfreqsetpointLE, row = 7, col = 2)
            self.w1.addWidget(self.cavoffsetpointLE, row = 8, col = 2)
            self.w1.addWidget(self.highthresholdLE, row = 9, col = 2)
            self.w1.addWidget(self.lowthresholdLE, row = 10, col = 2)
            #labels
            self.w1.addWidget(self.label_cavPgainLE, row = 2, col = 1)
            self.w1.addWidget(self.label_cavIgainLE, row = 3, col = 1)
            self.w1.addWidget(self.label_laserPgainLE, row = 4, col = 1)
            self.w1.addWidget(self.label_laserIgainLE, row = 5, col = 1)
            self.w1.addWidget(self.label_laserDgainLE, row = 6, col = 1)
            self.w1.addWidget(self.label_laserfreqsetpointLE, row = 7, col = 1)
            self.w1.addWidget(self.label_cavoffsetpointLE, row = 8, col = 1)
            self.w1.addWidget(self.label_highthresholdLE, row = 9, col = 1)
            self.w1.addWidget(self.label_lowthresholdLE, row = 10, col = 1)


          
            self.d1.addWidget(self.w1, row=0, col=0)
            
            