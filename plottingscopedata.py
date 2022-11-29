# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:05:06 2022

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
    data = data[49:]
    #print(data[49])
    #for i in range(len(data)):
    #    if data[i] == 'nan':
     #       print('t')
     #       np.delete(data, i)
    print(data)
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

data = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/DS0022.csv')
data2 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/DS0021.csv')
data3 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/DS0018.csv')

data4 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/DS0019.csv')
data5 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/DS0020.csv')
data6 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/DS0023.csv')

data7 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/A0002CH2.csv')
data8 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/A0002CH1.csv')

data9 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/A0003CH2.csv')
data10 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/A0004CH2.csv')
data11 = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/A0004CH1.csv')

time = np.array(range(len(data)))*8*10**-3

#data = plotdata(r'//homeblue02/mcwt12/My_Documents/phd yr1/STCL GUI/multiplextest/multiplexscopedata21.10.22/ALL0000/A0000CH1.csv')


#checking step sizes

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Time (ms)', fontsize=18)
ax.set_ylabel('Analog output (V)', fontsize=18)




#ax.plot(time, data*2*10**-3, color = '#785EF0', label='A0 2000, A1 1000')
#ax.axhline(y=1.61, xmin=0, xmax=1, color='k')
#ax.axhline(y=1.65, xmin=0, xmax=1, color='k')


#ax.plot(time, data2*2*10**-3, color = '#DC267F', label='A0 3000, A1 1000')
#ax.plot(time, data3*2*10**-3, color= '#FE6100', label='A0 4000, A1 1000')

#ax.plot(time, data4*2*10**-3, color='#FE6100', label='A0 4000, A1 1000')
#ax.plot(time, data5*2*10**-3, color = '#DC267F', label='A0 3000, A1 1000')
#ax.plot(time, data6*2*10**-3, color = '#785EF0')

ax.plot(time, data9*2*10**-3)
ax.plot(time, data10*2*10**-3)
ax.plot(time, data11*2*10**-3)

def plotrunningavg(data):
    window = 50
    average_y = []
    for ind in range(len(data) - window + 1):
         average_y.append(np.mean(data[ind:ind+window]))
    for ind in range(window - 1):
         average_y.insert(0, np.nan)
    return average_y

ax.legend()
#ax.plot(time, plotrunningavg(data3*2*10**-3), color='#67391C', label='A0 4000 mov.avg.')
#ax.plot(time, plotrunningavg(data2*2*10**-3), color='#8E707F', label='A0 3000 mov.avg.')
#ax.plot(time, plotrunningavg(data*2*10**-3), color='#20193E', label='A0 2000 mov.avg.')
#ax.plot(time, plotrunningavg(data6*2*10**-3), color='#20193E', label='A0 2000 mov.avg.')



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


def line(x, m,c):
    return m*x + c

m = -0.1
c = 5

fig = plt.figure(figsize=(10,7))
ax = fig.add_subplot()
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Analog output (V)')

time = time[400:2700]
data = data9[400:2700]*2*10**-3
data1 = data10[400:2700]*2*10**-3

ax.plot(time, data, label='A0')
ax.plot(time, data1, label='A1')


fitparams, pcov = scipy.optimize.curve_fit(line, time, data, p0=[m, c])

ax.plot(time, line(time, fitparams[0], fitparams[1]), label=f'A0, m:{fitparams[0]*10**3:.3} mV/s, c:{fitparams[1]:.5}', color='k')

fitparams1, pcov1 = scipy.optimize.curve_fit(line, time, data1, p0=[m, c])

ax.plot(time, line(time, fitparams1[0], fitparams1[1]), label=f'A1, m:{fitparams1[0]*10**3:.3} mV/s, c:{fitparams1[1]:.5}', color='k', linestyle='--')


ax.legend()'''