#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 13:16:48 2017

@author: bell
"""

import datetime

import pandas as pd
from netCDF4 import Dataset

import mysql.connector
import urllib

import cmocean


def manual_connect_to_DB(host='localhost', user='viewer', 
                         password=None, database='ecofoci', port=3306):
    """Try to establish database connection

    Parameters
    ----------
    host : str
        ip or domain name of host
    user : str
        account user
    password : str
        account password
    database : str
        database name to connect to
    port : int
        database port

    """
    db_config = {}     
    db_config['host'] = host
    db_config['user'] = user
    db_config['password'] = password
    db_config['database'] = database
    db_config['port'] = port

    try:
        db = mysql.connector.connect(**db_config)
    except:
        print "db error"
        
    # prepare a cursor object using cursor() method
    cursor = db.cursor(dictionary=True)
    return(db,cursor)

def get_profile(alamoid,startdate,enddate):
    db, cursor = manual_connect_to_DB(database='arcticheat_alamo_floats', port=8889)
    sql = "Select * from `{table}` WHERE ProfileTime BETWEEN '{startdate}' AND '{enddate}'".format(
                          table=alamoid,
                          startdate=startdate,
                          enddate=enddate)
    print sql
    data = pd.read_sql(sql,db)
    cursor.close()
    db.close()
    
    return data



#%% Plotting Routines

#using Cartopy for mapping
import matplotlib as mpl
#mpl.use('Agg') 
import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

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

def make_map(projection=ccrs.PlateCarree()):
    fig, ax = plt.subplots(figsize=(13, 8),
                           subplot_kw=dict(projection=projection))
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax

land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                        edgecolor='face',
                                        facecolor='1.0')


#%% make maps
### Region Wide


extent = [-170, -155, 69, 72]
erddap_etopo1()
(topoin, lats, lons) = etopo1_subset(file='data/etopo1_tmp.nc')

numdays = 90*12
counter = 0
for time_increment in range(0, numdays,2):
    
    basedate_2016 = datetime.datetime(2016,9,16)
    basedate_2017 = datetime.datetime(2017,9,16)
    
    endtime_2016 = basedate_2016 + datetime.timedelta(hours = time_increment)
    endtime_2017 = basedate_2017 + datetime.timedelta(hours = time_increment)

    af_9119 = get_profile(9119,'2017-09-16',endtime_2017.strftime('%Y-%m-%d %H:%M'))
    af_9085 = get_profile(9085,'2016-09-16',endtime_2016.strftime('%Y-%m-%d %H:%M'))
    af_9076 = get_profile(9076,'2016-09-16',endtime_2016.strftime('%Y-%m-%d %H:%M'))
    
    try:
        af_9119gbc = af_9119.groupby('CycleNumber').mean()
        af_9085gbc = af_9085.groupby('CycleNumber').mean()
        af_9076gbc = af_9076.groupby('CycleNumber').mean()
    except:
        continue
    
    try:
        fig,ax = make_map(projection=ccrs.PlateCarree(-160))
        
        ax.scatter([af_9076gbc['Longitude']],[af_9076gbc['Latitude']],
                15, c=[af_9076gbc['Temperature']], linewidth=0, edgecolors='none', marker='o', vmin=-2, vmax=7,
                cmap=cmocean.cm.thermal, transform=ccrs.PlateCarree(), zorder=3
                )
        ax.scatter([af_9085gbc['Longitude']],[af_9085gbc['Latitude']],
                15, c=[af_9085gbc['Temperature']], linewidth=0, edgecolors='none', marker='o', vmin=-2, vmax=7,
                cmap=cmocean.cm.thermal, transform=ccrs.PlateCarree(), zorder=3
                )
        ax.scatter([af_9119gbc['Longitude']],[af_9119gbc['Latitude']],
                15, c=[af_9119gbc['Temperature']], linewidth=0.2, edgecolors='k', marker='o', vmin=-2, vmax=7,
                cmap=cmocean.cm.thermal, transform=ccrs.PlateCarree(), zorder=3
                )
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
        
        fig.savefig('images/'+ str(counter).zfill(4) + '.png', bbox_inches='tight', dpi = (300))
        plt.close(fig)
    except KeyError:
        continue
    counter+=1
    