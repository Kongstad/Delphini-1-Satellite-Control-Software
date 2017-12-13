#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 10:57:27 2017

@author: maria
"""

import ephem as ep
import datetime as dt
from string import rstrip
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

#Get the TLE you want in whitelist from a list of many TLEs
def tle(white_list,all_list):
    #Open whitelist and make names similar to all
    with open(white_list,"r") as files:
        whitelist = map(rstrip,files)

    #Open all list:
    with open(all_list,"r") as files:
        all_tle = files.read().replace("\r","")
        
    #Make list and input all of the names in all which matches in whitelist
    TLE = [0]*len(whitelist)
    for i in range(0,len(whitelist)):
        if whitelist[i] in all_tle:
            ind = all_tle.index(whitelist[i])
            TLE[i] = all_tle[ind:(ind+164)].split('\n')
    
    return TLE[0]

#Split the TLE into its name and two lines to use for the ephem package
def lines(TLE):
    line0 = TLE[0].strip()
    line1 = TLE[1].strip()
    line2 = TLE[2].strip()
    
    return line0, line1, line2

#Plot the figures on maps (normal and projected)
def plot_fig(td,N,white_list):

    #Open all list to get TLE of given satellite in white_list:
    all_list = 'all.txt'
    TLE = tle(white_list,all_list)
    line0, line1, line2 = lines(TLE)
    tle_rec = ep.readtle(line0, line1, line2)

    #Current time    
    tle_time = dt.datetime.now()
    
    Per = 90. #approx period of orbit for LEO
    Tot = int(round(Per/td*N)) #total timesteps to calculate N numbers of orbits with a time increase of td
    Delta_t = dt.timedelta(minutes=td)
    times = [tle_time+i*Delta_t for i in range(0,Tot)]
    lat = [0]*Tot; lon = [0]*Tot; el = [0]*Tot
    for i in range(0,len(times)):
        tle_rec.compute(times[i])
        lon[i] = tle_rec.sublong; lat[i] = tle_rec.sublat; el[i] = tle_rec.elevation #longitude (radians), latitude (radians), elevation of satellite above sea level (meters)
    
    M = int(round(Per/td))
    past_times = [tle_time-i*Delta_t for i in range(0,M)]
    past_lat = [0]*M; past_lon = [0]*M; past_el = [0]*M
    for i in range(0,len(past_times)):
        tle_rec.compute(past_times[i])
        past_lon[i] = tle_rec.sublong; past_lat[i] = tle_rec.sublat; past_el[i] = tle_rec.elevation #longitude (radians), latitude (radians), elevation of satellite above sea level (meters)
    
    #Make map (round Earth)
    earth = Basemap(projection='ortho',lat_0=lat[0]*180./np.pi,lon_0=lon[0]*180./np.pi,resolution='l')
    earth.bluemarble()
    x,y = earth([i*180./np.pi for i in lon],[i*180./np.pi for i in lat])
    earth.plot(x,y,'bo', markersize=2,color='grey')
    x2,y2 = earth([i*180./np.pi for i in past_lon],[i*180./np.pi for i in past_lat])
    earth.plot(x2,y2,'bo', markersize=2,color='maroon')
    earth.plot(x[0],y[0],'bo', markersize=4,color='r')
    plt.show()
    
    #Make map (projected 2d)
    #earth2 = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
    #earth2.bluemarble()
    earth2=Basemap(projection='merc',llcrnrlat=-80,llcrnrlon=-179.,urcrnrlat=80,urcrnrlon=179.,lat_ts=20,resolution='c')
    earth2.bluemarble()
    x,y = earth2([i*180./np.pi for i in lon],[i*180./np.pi for i in lat])
    earth2.plot(x,y,'bo', markersize=2,color='grey')
    x2,y2 = earth2([i*180./np.pi for i in past_lon],[i*180./np.pi for i in past_lat])
    earth2.plot(x2,y2,'bo', markersize=2,color='maroon')
    earth2.plot(x[0],y[0],'bo', markersize=4,color='r')
    plt.show()

#Make figure of past (1) and future (N) orbits of satellite in whitelist file with timesteps td using the TLE
white_list = 'whitelist_test.txt'
td = 1 #timesteps in minutes
N = 5 #number of future orbits we want to display
plot_fig(td,N,white_list)