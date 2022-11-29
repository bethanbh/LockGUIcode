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
    decaytime = []
    A0 =[]
    A1 = []
    time = []
   
    
    for i in range(int(len(x)/4)):
        decaytime.append(x[i*4])
        A0.append(x[i*4 +1])
        A1.append(x[i*4 +2])
        time.append(x[i*4 +3])

        
    return [np.array(decaytime), np.array(A0), np.array(A1), np.array(time)]


fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()

testdata = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/(11-10-2022-10h8)_channeldatadelaytest40.csv')
testdataslow = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/(6-10-2022-15h15)_channeldatadelaytest14.csv')
testdataA = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/(5-10-2022-16h0)_channeldataProperdelaytest12.csv')


ax.set_xlabel('Delay time after pulse switched off (ms)')
ax.set_ylabel('Analog output')
ax.scatter(testdata[0]/1000, testdata[1], label='A0')
ax.scatter(testdata[0]/1000, testdata[2], label='A1')
ax.legend()

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
placeholder = range(len(testdata[2]))
#ax.scatter(placeholder, testdata[0]*0.1)
ax.scatter(placeholder, testdata[1], label='A0')
ax.scatter(placeholder, testdata[2], label='A1')
for i in range(len(testdata[2])):
    if testdata[0][i] == 0:
        ax.axvline(x=i, ymin=0, ymax=1, color='k', linestyle='--')
        print(i)
#ax.axvline(x=256*2, ymin=0, ymax=1, color='k', linestyle='--')
#ax.axvline(x=256*3, ymin=0, ymax=1, color='k', linestyle='--')
#ax.axvline(x=256*4, ymin=0, ymax=1, color='k', linestyle='--')
#ax.axvline(x=256*5, ymin=0, ymax=1, color='k', linestyle='--')
ax.set_ylabel('analog output')
ax.legend()



'''
ax.scatter(testdataslow[0], testdataslow[1], label='A0, pulse 1000ms' )
ax.scatter(testdataslow[0], testdataslow[2], label='A1, pulse 1000ms' )

ax.scatter(testdataA[0], testdataA[1], label='A0, pulse 5000ms' )
ax.scatter(testdataA[0], testdataA[2], label='A1, pulse 5000ms' )'''

#ax.plot(testdata[8], testdata[2], label='A2')
'''ax.plot(testdata[8], testdata[3], label='A3')
ax.plot(testdata[8], testdata[4], label='A4')
ax.plot(testdata[8], testdata[5], label='A5')
ax.plot(testdata[8], testdata[6], label='A6')
ax.plot(testdata[8], testdata[7], label='A7')'''
#ax.plot(testdataslow[8], testdataslow[2], label='A2 faster')
#ax.plot(testdataslow[8], testdataslow[1], label='A1')
#ax.plot(testdataslow[8], testdataslow[0], label='A0')
#ax.plot(testdataslow[8], testdataslow[3], label='A3')
#ax.plot(testdataslow[8], testdataslow[4], label='A4')
#ax.plot(testdataslow[8], testdataslow[5], label='A5')
#ax.plot(testdataslow[8], testdataslow[6], label='A6')
#ax.plot(testdataslow[8], testdataslow[7], label='A7')'''

#ax.set_xlim(0, 5)
#ax.set_ylim(1300, 1400)


timesep = []
'''
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


fitparams, pcov = scipy.optimize.curve_fit(line, testdata[0][244:344], testdata[1][244:344], p0=[m, c])
err = np.sqrt(np.diag(pcov))

fitparams2, pcov2 = scipy.optimize.curve_fit(line, testdata[0][244:344], testdata[2][244:344], p0=[m, c])
err2 = np.sqrt(np.diag(pcov2))

#ax.plot(testdata[0], line(testdata[0], fitparams[0], fitparams[1]), label=f'A0, pulse 100ms, m:{fitparams[0]:.3}, c:{fitparams[1]:.5}')
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

ax.legend()