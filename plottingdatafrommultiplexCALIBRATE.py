# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 16:44:21 2022

@author: mcwt12
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import scipy.stats


def plotdata(filename):
    x=[]
    
    with open(filename,'r', encoding='utf-8-sig') as csvfile:
    
        plots = csv.reader(csvfile, delimiter = ',')
          
        for each_row in plots:
            #print(each_row)
            x.append(float(each_row[0]))
    outputvalue = []
    A0 =[]
    time = []

   
    
    for i in range(int(len(x)/3)):
        outputvalue.append(x[i*3])
        A0.append(x[i*3 +1])
        time.append(x[i*3 +2])


        
    return [np.array(outputvalue), np.array(A0)]


def get_std_dev(ls):
    n = len(ls)
    mean = sum(ls) / n
    var = sum((x - mean)**2 for x in ls) / (n-1)
    std_dev = var ** 0.5
    return std_dev


fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()

testdata = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/(10-10-2022-12h58)_channeldataCalibratetest1.csv')
testdata2 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/(10-10-2022-13h7)_channeldataCalibratetest2.csv')





analoginput = np.linspace(0,4000,41) 
analoginput = np.append(analoginput, 4095)
#analoginput = np.delete(analoginput, np.where(analoginput == 2200))
#+ [4096]

analogoutput = []
analogoutputerr = []

allinput = np.append(testdata[0], testdata2[0])
alloutput = np.append(testdata[1], testdata2[1])



for i in range(len(analoginput)):
    temp = []
    for n in range(len(allinput)):
        if allinput[n] == analoginput[i]:
            temp.append(alloutput[n])
    analogoutput.append(np.mean(temp))
    err = get_std_dev(temp)/len(temp)
    analogoutputerr.append(err)
    


ax.set_xlabel('Scaled analog input (V)')
ax.set_ylabel('DAC output (V)')

#ax.errorbar(analoginput, (np.array(analogoutput)*3.3)/4096, yerr = analogoutputerr, fmt ='o', label='scaled DAC output (*3.3/4096)')

analoginput = analoginput*3.3/4096



voltages = [0.543,0.597,0.65,0.703,0.757,0.81,0.863,0.916,0.969,1.022,1.075,1.129,1.182,1.235,1.289,1.342,1.395,1.448,1.501,1.555,1.608,1.661,1.715,1.768,1.821,1.875,1.927,1.981,2.03,2.08,2.13,2.19,2.24,2.29,2.35,2.4,2.45,2.51,2.56,2.61,2.67,2.72]
ax.scatter(analoginput, voltages, color='plum', label='DAC output, measured directly')


#ax.legend()
'''
ax.scatter(testdataslow[0], testdataslow[1], label='A0, pulse 1000ms' )
ax.scatter(testdataslow[0], testdataslow[2], label='A1, pulse 1000ms' )

ax.scatter(testdataA[0], testdataA[1], label='A0, pulse 5000ms' )
ax.scatter(testdataA[0], testdataA[2], label='A1, pulse 5000ms' )'''


#ax.set_xlim(0, 5)
#ax.set_ylim(1300, 1400)

'''
timesep = []

for i in range(len(testdataslow[8])-1):
    timesep.append(testdataslow[8][i+1]-testdataslow[8][i])
   
timesep2 = []

for i in range(len(testdata[8])-1):
    timesep2.append(testdata[8][i+1]-testdata[8][i])
    
   
    
fig = plt.figure(figsize=(9,5))
ax = fig.add_subplot()
ax.plot(timesep)
ax.plot(timesep2)'''

def line(x, m,c):
    return m*x + c

m = -0.1
c = 5


fitparams, pcov = scipy.optimize.curve_fit(line, analoginput, voltages, p0=[m, c])
err = np.sqrt(np.diag(pcov))



#ax.plot(analoginput, line(analoginput, fitparams[0], fitparams[1]), label=f'm:{fitparams[0]:.3}, c:{fitparams[1]:.5}', color='k')
#ax.plot(testdata[0], line(testdata[0], fitparams2[0], fitparams2[1]), label=f'A1, pulse 100ms, m:{fitparams2[0]:.3}, c:{fitparams2[1]:.5}')

'''
fitparams3, pcov3 = scipy.optimize.curve_fit(line, testdataslow[0][1:], testdataslow[1][1:], p0=[m, c])
fitparams4, pcov4 = scipy.optimize.curve_fit(line, testdataslow[0], testdataslow[2], p0=[m, c])

ax.plot(testdataslow[0], line(testdataslow[0], fitparams3[0], fitparams3[1]), label=f'A0, pulse 1000ms, m:{fitparams3[0]:.3}, c:{fitparams3[1]:.4}')
ax.plot(testdataslow[0], line(testdataslow[0], fitparams4[0], fitparams4[1]), label=f'A1, pulse 1000ms, :{fitparams4[0]:.3}, c:{fitparams4[1]:.4}')

fitparams5, pcov5 = scipy.optimize.curve_fit(line, testdataA[0][1:], testdataA[1][1:], p0=[m, c])
fitparams6, pcov6 = scipy.optimize.curve_fit(line, testdataA[0], testdataA[2], p0=[m, c])

ax.plot(testdataA[0], line(testdataA[0], fitparams5[0], fitparams5[1]), label=f'A0, pulse 5000ms, m:{fitparams5[0]:.3}, c:{fitparams5[1]:.4}')
ax.plot(testdataA[0], line(testdataA[0], fitparams6[0], fitparams6[1]), label=f'A1, pulse 5000ms, m:{fitparams6[0]:.3}, c:{fitparams6[1]:.4}')
'''


#print(testdata[1][1:])

ax.legend()



####################################################################################
'''
fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
#
ax.set_xlabel('Analog output')




def get_std_dev(ls):
    n = len(ls)
    mean = sum(ls) / n
    var = sum((x - mean)**2 for x in ls) / (n-1)
    std_dev = var ** 0.5
    return std_dev

def plothist(data, label):
    result = ax.hist(data, bins=50, alpha=0.6, label= str(label))
    mean = np.mean(data)
    sd = get_std_dev(data)
    x1 = np.linspace(min(data), max(data), 100)
    dx1 = result[1][1] - result[1][0]
    scale1 = len(data)*dx1 #scaling the curves to match the histogram
    fwhm = 2*np.sqrt(2*np.log(2))*sd
    ax.plot(x1, scipy.stats.norm.pdf(x1, mean, sd)*scale1, label=f'FWHM: {fwhm:.3}, mean: {mean:.5}')
    ax.legend()

plothist(testdata[1], 'A0')
plothist(testdata[2], 'A1')
#plothist(testdataslow[1], 'A0')
#plothist(testdataslow[2], 'A1')

ax.legend()'''