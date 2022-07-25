# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 12:38:18 2022

@author: mcwt12
"""
import sys
import glob
import serial
import os
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

import serial.tools.list_ports
#print((serial.tools.list_ports.comports()[0][1]))

USUAL_DIR = os.getcwd()
print(USUAL_DIR)

DIR_PARAMS = USUAL_DIR+'//params_dir'


def listSerialPorts():
	# http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
	
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    print(result)
    return result

listSerialPorts()

def listCOMports():
    list_serialports = serial.tools.list_ports.comports()
    list_comports = []
    for n in range(len(list_serialports)):
        try:
            test = list_serialports[n][0]
            s = serial.Serial(test)
            s.close()
            list_comports.append(test)
        except (OSError, serial.SerialException):
            print('oh no an error')
            pass
    print(list_comports)
    return list_comports
    
listCOMports()
        
def listCOMports(self):
    list_serialports = serial.tools.list_ports.comports()
    for n in range(len(list_serialports)):
        try:
            test = list_serialports[n][0]
            s = serial.Serial(test)
            s.close()
            self.list_comports.append(test)
        except (OSError, serial.SerialException):
            print('oh no an error')
            pass
    print(self.list_comports)
    return self.list_comports


cavPgain = 1
cavIgain = 2
laserPgain = 3
laserIgain = 4
laserDgain = 5
laserfreqsetpoint = 6
cavoffsetpoint = 7
highthreshold = 8
lowthreshold = 9


#testing dictionary making
def GenerateParamDict():
    #should read the values and then put them into a dictionary, ready to be saved
    dict = {}
    dict['cavPgain'] = cavPgain
    dict['cavIgain'] = cavIgain
    dict['laserPgain'] = laserPgain
    dict['laserIgain'] = laserIgain
    dict['laserDgain'] = laserDgain
    dict['laserfreqsetpoint'] = laserfreqsetpoint
    dict['cavoffsetpoint'] = cavoffsetpoint
    dict['highthreshold'] = highthreshold
    dict['lowthreshold'] = lowthreshold
    print(dict)
    
dict = GenerateParamDict()


def SaveParameters(dict): #this will happen after the talking to the arduino bit, and updating the values- so the dict part should be actively saving the new values
    #want this to happen when you click the button, and also when you press lock if the box is checked
    #dict = self.GenerateParamDict() #do I need a input here??

    #then need to actually save the parameters
    param_file = QtGui.QFileDialog.getSaveFileName(self, 'Save Params', DIR_PARAMS, selectedFilter='*.txt') 

    if param_file:
        print(param_file)
        with open(param_file, 'w') as f :
            for key in dict:
                msg = ''
                msg += key
                msg += '\t' #this is just a big space
                msg += str(dict[key])
                msg += '\n'
                f.write(msg)
        f.close()
   
list_serialports = serial.tools.list_ports.comports()
list_comports = []
for n in range(len(list_serialports)):
    try:
        test = list_serialports[n][0]
        s = serial.Serial(test)
        s.close()
        list_comports.append(test)
    except (OSError, serial.SerialException):
        print('oh no an error')
        
comport = list_comports[0]
print(f' The selected COM port is: {comport}') #okay, so this does print out the COM port okay! (tested in testzone in STCLGUI page)

arduino = serial.Serial(comport)#should hopefully open the serial communication?
arduino.close()
