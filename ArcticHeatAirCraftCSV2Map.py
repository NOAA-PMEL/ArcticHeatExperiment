#!/usr/bin/env python

"""
ArcticHeatAirCraftCSV2Map.py

Takes parsed aircraft data and plots it
"""

#System Stack
import datetime
import pandas as pd
import argparse

#Science Stack
import numpy as np

# Plotting Stack
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import cartopy.crs as ccrs


__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 06, 01)
__modified__ = datetime.datetime(2016, 06, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'arctic heat mapping', 'wood', 'kevin'


"""----------------------------- Main -------------------------------------"""

# parse incoming command line options
parser = argparse.ArgumentParser(description='Map')
parser.add_argument('sourcedir', metavar='sourcedir', type=str, help='full path to file')
parser.add_argument('mapdir', metavar='mapdir', type=str, help='full path to file')
args = parser.parse_args()

## read data in
data = pd.read_csv(args.sourcedir,names=['lat','lon','alt','sst','pyro'],header=0)


range_int = 1.
extent = [data['lat'].min()-range_int, data['lat'].max()+range_int, \
          data['lon'].min()-range_int, data['lon'].max()+range_int]

maptype='cartopy'
if maptype == 'cartopy':
    
    fig = plt.figure()
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(extent)

    
    print "Adding Land"
    shp = cfeature.shapereader.Reader(args.mapdir)
    for record, geometry in zip(shp.records(), shp.geometries()):
        ax.add_geometries([geometry], ccrs.PlateCarree(), facecolor='white',
                          edgecolor='black', zorder=2)
    
    print "Plotting data"
    plt.scatter(data['lat'],data['lon'],20,marker='.', edgecolors='none', c=data['sst'], vmin=data['sst'].min(), vmax=data['sst'].max(), cmap='seismic', transform=ccrs.PlateCarree(), zorder=2)
    c = plt.colorbar()

    #plt.show()
    plt.savefig('ArcticHeat_SST.png', dpi = (300))
    plt.close()