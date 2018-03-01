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

#Empty Dates are missing GPS feeds
matfile = '/Volumes/WDC_internal/Users/bell/Downloads/9119_traj.mat'
data = loadmat(matfile)

header = ['DIVE_NUMBER','JULIAN_DATE','PRESSURE','LATITUDE','LONGITUDE']
traj_data = pd.DataFrame(data['traj'],columns=header)


traj_data['LATFILL'] = traj_data['LATITUDE'].fillna(method='ffill')
traj_data['LATFILL'][np.isnan(traj_data['JULIAN_DATE'])] = np.nan
traj_data['LONFILL'] = traj_data['LONGITUDE'].fillna(method='ffill')
traj_data['LONFILL'][np.isnan(traj_data['JULIAN_DATE'])] = np.nan
traj_data['DATEFILL'] = ((traj_data['LONGITUDE']/traj_data['LONGITUDE'])*traj_data['JULIAN_DATE']).fillna(0)

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
        
        traj_data['delta_m2'][index] = Geodesic.WGS84.Inverse(traj_data['LATFILL'][index],traj_data['LONFILL'][index],traj_data['LATFILL'][index+1],traj_data['LONFILL'][index+1])['s12']
        traj_data['delta_cog'][index] = Geodesic.WGS84.Inverse(traj_data['LATFILL'][index],traj_data['LONFILL'][index],traj_data['LATFILL'][index+1],traj_data['LONFILL'][index+1])['azi1']
        
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
                                     traj_data['delta_cog'][index-1],traj_data['velocity'][index-1],traj_data['JULIAN_DATE'][index]]),ignore_index=True)
    if np.isnan(traj_data['JULIAN_DATE'][index]) and (index != 0):
        traj = traj.append(pd.Series([traj_data['DIVE_NUMBER'][index],traj_data['LATITUDE'][index],traj_data['LONGITUDE'][index],
                                     traj_data['delta_cog'][index-1],traj_data['velocity'][index-1],traj_data['JULIAN_DATE'][index]]),ignore_index=True)
        
traj.rename(columns={0:'DIVE_NUMBER',1:'LATITUDE',2:'LONGITUDE',3:'delta_cog',4:'velocity',5:'time'},inplace=True)
traj['angle'] = 90-traj['delta_cog']
traj['u'] = np.cos(np.deg2rad(traj['angle'])) * traj['velocity']
traj['v'] = np.sin(np.deg2rad(traj['angle'])) * traj['velocity']

traj.drop(index=0,inplace=True) #skips cast -1

# vector addition
ucomp = traj.iloc[1::2, :]['u'].values-traj.iloc[::2, :]['u'].values
vcomp = traj.iloc[1::2, :]['v'].values-traj.iloc[::2, :]['v'].values

angle = np.rad2deg(np.arctan2(vcomp,ucomp))


#clean misssing data
traj['u'][np.isnan(traj['LATITUDE'])] = np.nan
traj['v'][np.isnan(traj['LATITUDE'])] = np.nan
traj['velocity'][np.isnan(traj['LATITUDE'])] = np.nan
"""-------------------------------------------------------------------------"""
#%% plots
#cartopy is the slow replacement for basemap (and gmt tools are being wrapped)

import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import urllib

def erddap_etopo1():
    """get subset of etopo1 data from erddap"""
    
    urllib.urlretrieve("http://coastwatch.pfeg.noaa.gov/erddap/griddap/etopo180.nc?altitude[(65):1:(75)][(-170):1:(-155)]","data/etopo1_tmp.nc")
    
def etopo1_subset(file='etopo1.nc', region=None):
    """ read in ardemV2 topography/bathymetry. """
    
    bathydata = Dataset(file)
    
    topoin = bathydata.variables['altitude'][:]
    lons = bathydata.variables['longitude'][:]
    lats = bathydata.variables['latitude'][:]
    bathydata.close()
    
    return(topoin, lats, lons)

land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                        edgecolor='face',
                                        facecolor='1.0')    
    
extent = [-170, -155, 69, 74]
erddap_etopo1()
(topoin, lats, lons) = etopo1_subset(file='data/etopo1_tmp.nc')

## vector plot
fig = plt.figure()
plt.subplot(1,1,1)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(extent)


print "Adding Land"
shp = cfeature.shapereader.Reader('ArcticHeat_coastlines/chukchi.shp')
for record, geometry in zip(shp.records(), shp.geometries()):
    ax.add_geometries([geometry], ccrs.PlateCarree(), facecolor='white',
                      edgecolor='black', zorder=2)


print "Plotting data"
## bathymetry contours
CS = plt.contour(lons, lats, topoin, [-1000, -100, -50, -25,], 
                 colors='k', alpha=0.4, linestyle='--', linewidths=1, zorder=2,
                 transform=ccrs.PlateCarree())
CS = plt.contourf(lons, lats, topoin, [-1000, -100, -50, -25,], 
                 colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', zorder=1,
                 transform=ccrs.PlateCarree())

ax.add_feature(land_50m)
ax.coastlines(resolution='50m')
ax.set_extent(extent)



#evens are bottom
gv = ax.quiver(traj['LONGITUDE'].iloc[1::2], traj['LATITUDE'].iloc[::2], traj['u'].iloc[::2], traj['v'].iloc[::2], color='red', transform=ccrs.PlateCarree())
#odds are surface vecotrs
gv = ax.quiver(traj['LONGITUDE'].iloc[::2], traj['LATITUDE'].iloc[1::2], traj['u'].iloc[1::2], traj['v'].iloc[1::2], color='black', transform=ccrs.PlateCarree())

g1 = ax.gridlines(crs=ccrs.PlateCarree(),
              linewidth=.25, color='gray', alpha=0.5, linestyle='--')
g1.xlocator = ticker.FixedLocator([-156, -160, -164, -168, -172, -176, 180])
g1.ylocator = ticker.FixedLocator([64, 66, 68, 70, 72, 74, 76])
g1.xformatter = LONGITUDE_FORMATTER
g1.yformatter = LATITUDE_FORMATTER
g1.ylabels_left = True
g1.xlabels_top = True


#%% dive location plot
fig = plt.figure()
plt.subplot(1,1,1)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(extent)


print "Adding Land"
shp = cfeature.shapereader.Reader('ArcticHeat_coastlines/chukchi.shp')
for record, geometry in zip(shp.records(), shp.geometries()):
    ax.add_geometries([geometry], ccrs.PlateCarree(), facecolor='white',
                      edgecolor='black', zorder=2)


print "Plotting data"
## bathymetry contours
CS = plt.contour(lons, lats, topoin, [-1000, -100, -50, -25,], 
                 colors='k', alpha=0.4, linestyle='--', linewidths=1, zorder=2,
                 transform=ccrs.PlateCarree())
CS = plt.contourf(lons, lats, topoin, [-1000, -100, -50, -25,], 
                 colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', zorder=1,
                 transform=ccrs.PlateCarree())

ax.add_feature(land_50m)
ax.coastlines(resolution='50m')
ax.set_extent(extent)

gv = plt.plot(traj['LONGITUDE'].iloc[1::2], traj['LATITUDE'].iloc[::2],
         linestyle=None, linewidth=0, color='black', marker='+', markersize=.5,
         transform=ccrs.PlateCarree(),
         )
for i in range(1,1203,10): #surface vectors
    gt = plt.text(traj['LONGITUDE'].iloc[i], traj['LATITUDE'].iloc[i], traj['DIVE_NUMBER'].iloc[i].astype(str),
         horizontalalignment='right', fontsize=6,
         transform=ccrs.PlateCarree())
    
g1 = ax.gridlines(crs=ccrs.PlateCarree(),
              linewidth=.25, color='gray', alpha=0.5, linestyle='--')
g1.xlocator = ticker.FixedLocator([-156, -160, -164, -168, -172, -176, 180])
g1.ylocator = ticker.FixedLocator([64, 66, 68, 70, 72, 74, 76])
g1.xformatter = LONGITUDE_FORMATTER
g1.yformatter = LATITUDE_FORMATTER
g1.ylabels_left = True
g1.xlabels_top = True
#%%
print "plotting data in polar coordinates with 25 cm/s concentric circles"

for i in range(1,1203,2): #surface vectors
    try:
        plt.figure(1, figsize=(6, 6), facecolor='w', edgecolor='w')
        ax = plt.subplot(111, projection='polar')
        #sfc flow
        ax.arrow(traj['angle'].iloc[i]/180.*np.pi, 0, 0, traj['velocity'].iloc[i],
                 edgecolor = 'red', facecolor = 'red', width=0.015,lw=1,length_includes_head=True,zorder = 5)
        #black is bottom of period before red
        ax.arrow(traj['angle'].iloc[i-1]/180.*np.pi,0, 0, traj['velocity'].iloc[i-1],
                 edgecolor = 'black', facecolor = 'black', width = 0.015,lw=1,length_includes_head=True, zorder = 4)
        #grey is bottom period after red
        ax.arrow(traj['angle'].iloc[i+1]/180.*np.pi,0, 0, traj['velocity'].iloc[i+1],
                 edgecolor = 'grey', facecolor = 'grey', width = 0.015, lw=1,length_includes_head=True, zorder = 4)
        ax.set_rmax(1)
        ax.set_rticks([0.25, 0.5, 0.75, 1])  # less radial ticks
        #ax.set_rticks([0.0625, 0.125, 0.1875, 0.25])  # less radial ticks
        ax.set_rlabel_position(-22.5)  # get radial labels away from plotted line
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.grid(True)
        plt.title('Lat: {0}, Lon: {1}, Dive:{2}'.format(traj['LATITUDE'][i],traj['LONGITUDE'][i],traj['DIVE_NUMBER'][i]),size=10)
        plt.savefig('images/ALAMO_9119_SFCvBTM_DiveNum'+ str(traj['DIVE_NUMBER'].iloc[i]) + '.jpg',dpi=300)
        plt.close()
    except ValueError:
        print "profile at index {0} has no data".format(i)