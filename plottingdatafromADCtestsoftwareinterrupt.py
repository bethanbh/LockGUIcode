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
from mpl_toolkits.axes_grid1 import host_subplot

def plotdata(filename):
    x=[]
    
    with open(filename,'r', encoding='utf-8-sig') as csvfile:
    
        plots = csv.reader(csvfile, delimiter = ',')
          
        for each_row in plots:
            #print(each_row)
            x.append(float(each_row[0]))
    A0 = []
    A1 =[]
    A0status = []
    A1status = []
    time = []
   
    
    for i in range(int(len(x)/5)):
        A0.append(x[i*5])
        A1.append(x[i*5 +1])
        A0status.append(x[i*5 +2])
        A1status.append(x[i*5 +3])
        time.append(x[i*5 +4])

        
    return [np.array(A0), np.array(A1), np.array(A0status), np.array(A1status), np.array(time)]




fig = plt.figure(figsize=(8,7))
host = host_subplot(111, figure=fig)
par = host.twinx()

testdata = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/ADCtest/(28-11-2022-16h12)_channeldata.csv')




host.set_xlabel('Time (s)')
host.set_ylabel('Analog output (AU)')
par.set_ylabel("Interrupt indicator")

p1 = host.plot(testdata[4], testdata[0], label='A0 input')
p1 = host.plot(testdata[4], testdata[1], label='A1 input')
p2 = par.plot(testdata[4], testdata[2], label='A0 interrupt', linestyle='--')
p2 = par.plot(testdata[4], testdata[3], label='A1 interrupt', linestyle='--')


host.legend()





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

'''
fitparams, pcov = scipy.optimize.curve_fit(line, placeholder, testdata[1], p0=[m, c])

fitparams2, pcov2 = scipy.optimize.curve_fit(line, placeholder, testdata[2], p0=[m, c])

fitparams3, pcov3 = scipy.optimize.curve_fit(line, placeholder, testdata[3], p0=[m, c])


ax.plot(placeholder, line(placeholder, fitparams[0], fitparams[1]), label=f'A0, m:{fitparams[0]:.3}, c:{fitparams[1]:.5}', color='k')
ax.plot(placeholder, line(placeholder, fitparams2[0], fitparams2[1]), label=f'A1 m:{fitparams2[0]:.3}, c:{fitparams2[1]:.5}', color='k')
ax.plot(placeholder, line(placeholder, fitparams3[0], fitparams3[1]), label=f'A2 m:{fitparams3[0]:.3}, c:{fitparams3[1]:.5}', color='k', linestyle='--')
'''

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






####################################################################################

#fig = plt.figure(figsize=(10,7))
#ax = fig.add_subplot()
#ax.set_xlabel('Analog output')




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
    ax.plot(x1, scipy.stats.norm.pdf(x1, mean, sd)*scale1, label=f'FWHM: {fwhm:.4}, mean: {mean:.5}')
    #ax.set_xlim(1850, 2200)
    #ax.set_ylim(0,40)
    ax.legend()

#plothist(testdata[1], 'A0')
#plothist(testdata[2], 'A1')
#plothist(testdata[3], 'A2')

'''
fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Analog output')

plothist(testdata[1][256:511], 'A0, 2')
plothist(testdata[2][256:511], 'A1')
plothist(testdata[3][256:511], 'A2')

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Analog output')

plothist(testdata[1][512:767], 'A0, 3')
plothist(testdata[2][512:767], 'A1')
plothist(testdata[3][512:767], 'A2')

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Analog output')

plothist(testdata[1][768:1023], 'A0, 4')
plothist(testdata[2][768:1023], 'A1')
plothist(testdata[3][768:1023], 'A2')

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Analog output')

plothist(testdata[1][1024:1279], 'A0, 5')
plothist(testdata[2][1024:1279], 'A1')
plothist(testdata[3][1024:1279], 'A2')


A0mean = [1994.3, 1995.2, 1991.7, 1991.3, 1996.4]
A0fwhm = [114.9, 108.1, 106.5, 105, 96.28]
A1mean = [2033.4,2032.4, 2035.3,2028.6,2035.7]
A1fwhm = [115.3,112.5,102.8,100.6,90.8]
A2mean = [2015, 2015.1, 2014.9, 2015.6,2015.1]
A2fwhm = [27.25,22.26, 22.64,20.61,27.91]

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Run number')
run = [1,2,3,4,5]
ax.set_ylabel('Analog output')

ax.errorbar(run, A0mean, yerr=A0fwhm, fmt ='o', label='A0', capsize=8)
ax.errorbar(run, A1mean, yerr=A1fwhm, fmt ='o', label='A1', capsize=8)
ax.errorbar(run, A2mean, yerr=A2fwhm, fmt ='o', label='A2', capsize=8)
ax.legend()'''
