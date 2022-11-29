# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 16:44:21 2022

@author: mcwt12
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize


def plotdata(filename):
    x=[]
    
    with open(filename,'r', encoding='utf-8-sig') as csvfile:
    
        plots = csv.reader(csvfile, delimiter = ',')
          
        for each_row in plots:
            #print(each_row)
            x.append(float(each_row[0]))
    A0 =[]
    A1 = []
    A2 = []
    A3 = []
    A4 =[]
    A5 =[]
    A6  = []
    A7 = []
    time = []
   
    
    for i in range(int(len(x)/9)):
        time.append(x[i*9])
        A0.append(x[i*9 +1])
        A1.append(x[i*9 +2])
        A2.append(x[i*9 +3])
        A3.append(x[i*9 +4])
        A4.append(x[i*9 +5])
        A5.append(x[i*9 +6])
        A6.append(x[i*9 +7])
        A7.append(x[i*9 +8])
        
    return [np.array(A0), np.array(A1), np.array(A2), np.array(A3), np.array(A4), np.array(A5), np.array(A6), np.array(A7), np.array(time)]


fig = plt.figure(figsize=(9,5))
ax = fig.add_subplot()

testdata = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/(4-10-2022-11h13)_channeldataDECAYTESTfaster.csv')
testdataslow = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/(4-10-2022-11h13)_channeldataDECAYTESTfaster.csv')

ax.set_xlabel('Time (s)')
ax.set_ylabel('Analog output')
#ax.plot(testdata[8][1400:], testdata[1][1400:], label='A0')
ax.plot(testdata[8][2050:], testdata[0][2050:], label='A0')
#ax.plot(testdata[8], testdata[1], label='A1')
ax.plot(testdata[8], testdata[2], label='A2')
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


def line(x, m,c):
    return m*x + c

m = -0.1
c = 5


fitparams, pcov = scipy.optimize.curve_fit(line, testdata[8][550:1350], testdata[0][550:1350], p0=[m, c])
fitparams2, pcov2 = scipy.optimize.curve_fit(line, testdata[8][550:1350], testdata[1][550:1350], p0=[m, c])


#ax.plot(testdata[8][550:1350], line(testdata[8][550:1350], fitparams[0], fitparams[1]), label=f'A0, m:{fitparams[0]:.3}, c:{fitparams[1]:.5}')
#ax.plot(testdata[8][550:1350], line(testdata[8][550:1350], fitparams2[0], fitparams2[1]), label=f'A1, m:{fitparams2[0]:.3}, c:{fitparams2[1]:.5}')


#ax.set_xlim(25, 30)
#ax.set_ylim(1250, 1450)
ax.legend()



############################################################

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
#
ax.set_xlabel('Analog output')

#result = ax.hist(testdata[0][550:1350], bins=50, alpha=0.6, label= 'A0 hold')



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




#ax.text(0.18, 0.90, f'FWHM: \n{fwhm:.3}GHz', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
#ax.text(0.18, 0.75, f'max, min: \n {max(volt):.3}, {min(volt):.3}GHz', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

plothist(testdata[2][250:1950], label='A2 sample')
plothist(testdata[0][2050:], label='A0 sample')
plothist(testdata[2][2050:], label='A2 hold')





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