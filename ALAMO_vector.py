#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 08:11:58 2018

@author: bell
"""

from scipy.io import loadmat
import pandas as pd
import numpy as np
from netCDF4 import Dataset

from geopy.distance import great_circle
from geographiclib.geodesic import Geodesic



"""-------------------------------------------------------------------------"""

matfile = '/Volumes/WDC_internal/Users/bell/Downloads/9119_traj.mat'

data = loadmat(matfile)

header = ['DIVE_NUMBER','JULIAN_DATE','PRESSURE','LATITUDE','LONGITUDE']
traj_data = pd.DataFrame(data['traj'],columns=header)

traj_data['LATFILL'] = traj_data['LATITUDE'].fillna(method='ffill')
traj_data['LONFILL'] = traj_data['LONGITUDE'].fillna(method='ffill')
traj_data['DATEFILL'] = ((traj_data['LONGITUDE']/traj_data['LONGITUDE'])*traj_data['JULIAN_DATE']).fillna(method='ffill')

traj_data['delta_m'] = np.nan
traj_data['delta_m2'] = np.nan
traj_data['delta_cog'] = np.nan
traj_data['delta_t'] = np.nan
traj_data['delta_tb'] = np.nan
traj_data['delta_tf'] = np.nan
traj_data['velocity'] = np.nan
traj_data['delta_p'] = np.nan

for index, row in traj_data.iterrows():
    if index == 0:
        traj_data['delta_p'][index] = 0
    elif index == len(traj_data)-1:
        break
    else:
        traj_data['delta_p'][index] = (traj_data['PRESSURE'][index+1] - traj_data['PRESSURE'][index])                


#getting just the time on bottom without the falltime
traj_data['DATEFILL2'] = (((traj_data['delta_p'].where(traj_data['delta_p'] > 1)) / traj_data['delta_p'].where(traj_data['delta_p'] > 1)) * traj_data['JULIAN_DATE']).fillna(method='ffill')
traj_data['DATEFILL3'] = (((traj_data['delta_p'].where(traj_data['delta_p'] < -1)) / traj_data['delta_p'].where(traj_data['delta_p'] < -1)) * traj_data['JULIAN_DATE']).fillna(method='bfill')
traj_data['delta_tb'] = (traj_data['DATEFILL3'] - traj_data['DATEFILL2']) * 86400.

#bottom time
median_bottom_time = traj_data.groupby('DIVE_NUMBER').median()['delta_tb']

for index, row in traj_data.iterrows():
    if index == 0:
        traj_data['delta_m'][index] = 0
        traj_data['delta_m2'][index] = 0
        traj_data['delta_cog'][index] = 0
        traj_data['delta_t'][index] = 0
        traj_data['velocity'][index] = 0
        
    elif index == len(traj_data)-1:
        break
    else:
        traj_data['delta_m'][index] = great_circle((traj_data['LATFILL'][index+1],traj_data['LONFILL'][index+1]), 
                                                  (traj_data['LATFILL'][index],traj_data['LONFILL'][index])).meters
        
        traj_data['delta_m2'][index] = Geodesic.WGS84.Inverse(traj_data['LATFILL'][index+1],traj_data['LONFILL'][index+1],traj_data['LATFILL'][index],traj_data['LONFILL'][index])['s12']
        traj_data['delta_cog'][index] = Geodesic.WGS84.Inverse(traj_data['LATFILL'][index+1],traj_data['LONFILL'][index+1],traj_data['LATFILL'][index],traj_data['LONFILL'][index])['azi1']
        
        #this provides surface time
        traj_data['delta_t'][index] = (traj_data['DATEFILL'][index+1] - traj_data['DATEFILL'][index]) * 86400.
        if traj_data['delta_t'][index] > median_bottom_time[traj_data['DIVE_NUMBER'][index]]:
            traj_data['delta_t'][index] = median_bottom_time[traj_data['DIVE_NUMBER'][index]]
        traj_data['velocity'][index] = traj_data['delta_m'][index] / traj_data['delta_t'][index]        

### LAT/LON INDEX IS +1 LARGER THAN THE SPEED/COG INDEX, FIRST OF PAIRED VALUES IS FROM BOTTOM, SECOND IS FROM TOP

traj = pd.DataFrame()

for index, row in traj_data.iterrows():
    if not np.isnan(traj_data['LATITUDE'][index]):
        traj = traj.append(pd.Series([traj_data['DIVE_NUMBER'][index],traj_data['LATITUDE'][index],traj_data['LONGITUDE'][index],
                                     traj_data['delta_cog'][index-1],traj_data['velocity'][index-1]]),ignore_index=True)
    
traj.rename(columns={0:'DIVE_NUMBER',1:'LATITUDE',2:'LONGITUDE',3:'delta_cog',4:'velocity'},inplace=True)
traj['angle'] = 90-traj['delta_cog']
traj['u'] = np.cos(np.deg2rad(traj['angle'])) * traj['velocity']
traj['v'] = np.sin(np.deg2rad(traj['angle'])) * traj['velocity']

"""-------------------------------------------------------------------------"""
#%% plots

from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import Basemap, shiftgrid
import matplotlib.pyplot as plt

def etopo5_data():
    """ read in etopo5 topography/bathymetry. """
    file = 'data/etopo5.nc'
    etopodata = Dataset(file)
    
    topoin = etopodata.variables['bath'][:]
    lons = etopodata.variables['X'][:]
    lats = etopodata.variables['Y'][:]
    etopodata.close()
    
    topoin,lons = shiftgrid(0.,topoin,lons,start=False) # -360 -> 0
    
    #lons, lats = np.meshgrid(lons, lats)
    
    return(topoin, lats, lons)

def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx

#(topoin_tot, elats_tot, elons_tot) = etopo5_data()
(topoin, elats, elons) = etopo5_data()

#build regional subset of data
topoin = topoin[find_nearest(elats,55):find_nearest(elats,75),find_nearest(elons,180):find_nearest(elons,130)]
elons = elons[find_nearest(elons,180):find_nearest(elons,130)]
elats = elats[find_nearest(elats,55):find_nearest(elats,75)]


fig = plt.figure()
ax = plt.subplot(111)
m = Basemap(resolution='i',projection='merc', llcrnrlat=55, \
    urcrnrlat=75,llcrnrlon=180,urcrnrlon=130,\
    lat_ts=45)

elons, elats = np.meshgrid(elons, elats)
ex, ey = m(elons, elats)