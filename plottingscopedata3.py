# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 17:32:08 2022

@author: mcwt12
"""


import csv
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import scipy.optimize
import scipy.stats

def plotdata(filename):
    x=[]
    
    with open(filename,'r', encoding='utf-8-sig') as csvfile:
    
        plots = csv.reader(csvfile, delimiter = ',')
          
        for each_row in plots:
            #print(each_row)
                x.append(each_row[0])
                
        x = x[14:]
        
        for i in range(len(x)):
            x[i] = float(x[i])

    return np.array(x)

def get_std_dev(ls):
    n = len(ls)
    mean = sum(ls) / n
    var = sum((x - mean)**2 for x in ls) / (n-1)
    std_dev = var ** 0.5
    return std_dev

def plothist(data, label):
   # data = data[49:]
   # print(data)
    result = ax.hist(data, bins=15, alpha=0.6, label= str(label))
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
    
    
def line(x, m,c):
    return m*x + c

m = -0.1
c = 5

data = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/multiplexscopedata21.10.22/ALL0000/A0000CH1.csv')
data1 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/multiplexscopedata21.10.22/ALL0000/A0000CH4.csv')
data3 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/multiplexscopedata21.10.22/ALL0001/A0001CH1.csv')
data4 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/multiplexscopedata21.10.22/ALL0001/A0001CH4.csv')


data = data*0.008 #from plottingscopedata.py yesterday - vertical scale/25
data1 = data1*0.008
data4 = data4*0.008
data3 = data3*0.04


time = np.array(range(len(data)))*4*10**-2
#from sampling period*10**3 to convert to ms

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Time (ms)', fontsize='18')
ax.set_ylabel('Analog output (V)', fontsize='18')

#ax.plot(time, (data3), label='Digital A out ', color='#aa2c4b')
#ax.plot(time, data, label='Input from DAC')
ax.plot(time, data1, label='A0 output')
#ax.plot(time, data4, label='A1 output')
ax.axhline(y=1.61, xmin=0, xmax=1, color='k')
ax.axhline(y=1.6, xmin=0, xmax=1, color='k')


ax.set_xlim(0,100)

#ax.plot(time, data)
#ax.plot(time[2670:], data1[2670:])

#ax.plot(time[210:320], data1[210:320])
#ax.plot(time[0:1000], data[0:1000])

def plotrunningavg(data):
    window = 50
    average_y = []
    for ind in range(len(data) - window + 1):
         average_y.append(np.mean(data[ind:ind+window]))
    for ind in range(window - 1):
         average_y.insert(0, np.nan)
    return average_y

ax.plot(time, plotrunningavg(data1), color='k')
#ax.plot(time, plotrunningavg(data4), color='k')


enddata = data1[0:2350]
endtime = time[0:2350]
startdata = data1[2670:]
starttime = time[2670:]
middledata = data1[2400:2630]
middletime = time[2400:2630]


#ax.plot(endtime, enddata, label='A0 output')
#ax.plot(starttime, startdata, label='A0 output')
#ax.plot(middletime, middledata, label='A0 output')


'''enddata = data1[0:210]
endtime = time[0:210]
startdata = data1[210:320]
starttime = time[210:320]
middledata = data1[330:]
middletime = time[330:]

fitparams, pcov = scipy.optimize.curve_fit(line, endtime, enddata, p0=[m, c])
ax.plot(endtime, line(endtime, fitparams[0], fitparams[1]), label=f'A0 H delay, m:{fitparams[0]*10**6:.3} mV/s, c:{fitparams[1]:.5}V', color='k')

fitparams1, pcov1 = scipy.optimize.curve_fit(line, starttime, startdata, p0=[m, c])
ax.plot(starttime, line(starttime, fitparams1[0], fitparams1[1]), label=f'A0 H, m:{fitparams1[0]*10**6:.3} mV/s, c:{fitparams1[1]:.5}V', color='k')

fitparams2, pcov2 = scipy.optimize.curve_fit(line, middletime, middledata, p0=[m, c])
ax.plot(middletime, line(middletime, fitparams2[0], fitparams2[1]), label=f'A0 S, m:{fitparams2[0]*10**6:.3} mV/s, c:{fitparams2[1]:.5}V', color='k')
'''
ax.legend()


#HISTOGRAMS

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Analog output (V)')
plothist(enddata, 'A0 H after 2000ms')
plothist(startdata, 'A0 H')
plothist(middledata, 'A0 S')



'''
#checking step sizes

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Analog output (V)')




ax.plot(time, data*2*10**-3, color = '#785EF0', label='A0 2000, A1 1000')
ax.plot(time, data2*2*10**-3, color = '#DC267F', label='A0 3000, A1 1000')
ax.plot(time, data3*2*10**-3, color= '#FE6100', label='A0 4000, A1 1000')

ax.plot(time, data4*2*10**-3, color='#FE6100', label='A0 4000, A1 1000')
ax.plot(time, data5*2*10**-3, color = '#DC267F', label='A0 3000, A1 1000')
ax.plot(time, data6*2*10**-3, color = '#785EF0', label='A0 2000, A1 1000')

def plotrunningavg(data):
    window = 50
    average_y = []
    for ind in range(len(data) - window + 1):
         average_y.append(np.mean(data[ind:ind+window]))
    for ind in range(window - 1):
         average_y.insert(0, np.nan)
    return average_y

ax.plot(time, plotrunningavg(data3*2*10**-3), color='#67391C', label='A0 4000 mov.avg.')
ax.plot(time, plotrunningavg(data2*2*10**-3), color='#8E707F', label='A0 3000 mov.avg.')
ax.plot(time, plotrunningavg(data*2*10**-3), color='#20193E', label='A0 2000 mov.avg.')
ax.legend()


fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Analog output - moving average (V)')

ax.plot(time, (data3*2*10**-3)-plotrunningavg(data3*2*10**-3), color='#FE6100', label='A0 4000, A1 1000')
ax.plot(time, (data2*2*10**-3)-plotrunningavg(data2*2*10**-3), color = '#DC267F', label='A0 3000, A1 1000')
ax.plot(time, (data*2*10**-3)-plotrunningavg(data*2*10**-3), color = '#785EF0', label='A0 2000, A1 1000')
ax.legend()

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Analog output - moving average (V)')
plothist((data3*2*10**-3)-plotrunningavg(data3*2*10**-3), 'A0 4000, A1 1000')
plothist((data2*2*10**-3)-plotrunningavg(data2*2*10**-3), 'A0 3000, A1 1000')
plothist((data*2*10**-3)-plotrunningavg(data*2*10**-3), 'A0 2000, A1 1000')

'''

'''
def line(x, m,c):
    return m*x + c

m = -0.1
c = 5

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Analog output (V)')


ax.plot(time, data, label='A0')
#ax.plot(time, data1, label='A1')


fitparams, pcov = scipy.optimize.curve_fit(line, time, data, p0=[m, c])

ax.plot(time, line(time, fitparams[0], fitparams[1]), label=f'A0, m:{fitparams[0]*10**3:.3} mV/s, c:{fitparams[1]:.5}', color='k')

#fitparams1, pcov1 = scipy.optimize.curve_fit(line, time, data1, p0=[m, c])

#ax.plot(time, line(time, fitparams1[0], fitparams1[1]), label=f'A1, m:{fitparams1[0]*10**3:.3} mV/s, c:{fitparams1[1]:.5}', color='k', linestyle='--')


ax.legend()
'''