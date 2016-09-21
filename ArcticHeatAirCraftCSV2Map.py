#!/usr/bin/env python

"""
ArcticHeatAirCraftCSV2Map.py

Takes parsed aircraft data and plots it
"""

#System Stack
import datetime
import pandas as pd
import argparse
import pygeoj

#Science Stack
import numpy as np

# Plotting Stack
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.mlab import bivariate_normal
import matplotlib.ticker as ticker
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 06, 01)
__modified__ = datetime.datetime(2016, 06, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'arctic heat mapping', 'wood', 'kevin'


# Example of making your own norm.  Also see matplotlib.colors.
# From Joe Kington: This one gives two different linear ramps:

class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

"""----------------------------- Main -------------------------------------"""

# parse incoming command line options
parser = argparse.ArgumentParser(description='Map')
parser.add_argument('sourcedir', metavar='sourcedir', type=str, help='full path to file')
parser.add_argument('mapdir', metavar='mapdir', type=str, help='full path to file')
parser.add_argument('maxalt', metavar='maxalt', type=float, help='altitude above which data is ignored')
parser.add_argument('--stations', type=str, help='optional full path to geojson file')
args = parser.parse_args()

## read data in
data = pd.read_csv(args.sourcedir,names=['lat','lon','alt','sst','pyro'],header=0)

if args.stations:
    geo_data = pygeoj.load(filepath=args.stations)

range_int = 1.
extent = [data['lat'].min()-range_int, data['lat'].max()+range_int, \
          data['lon'].min()-range_int, data['lon'].max()+range_int]
data['sst'][data['alt'] > args.maxalt] = np.nan

maptype='cartopy'
if maptype == 'cartopy':
    
    fig = plt.figure()
    plt.subplot(1,1,1)
    ax = plt.axes(projection=ccrs.Mercator())
    ax.set_extent(extent)

    
    print "Adding Land"
    shp = cfeature.shapereader.Reader(args.mapdir)
    for record, geometry in zip(shp.records(), shp.geometries()):
        ax.add_geometries([geometry], ccrs.PlateCarree(), facecolor='white',
                          edgecolor='black', zorder=2)
    
    print "Plotting data"
    plt.scatter(data['lat'],data['lon'],20,marker='.', edgecolors='none', c=data['sst'], 
        norm=MidpointNormalize(midpoint=0.),
        vmin=-5, vmax=10, 
        cmap='seismic', transform=ccrs.PlateCarree(), zorder=2)
    c = plt.colorbar(extend='both', shrink=0.50)

    if args.stations:
        for feature in geodata:
            (glat,glon) = feature.geometry.coordinates
            plt.scatter(glat,glon,10,
                marker='+', edgecolors='none', color='black', 
                transform=ccrs.PlateCarree(),zorder=3)
    #plt.show()
    g1 = ax.gridlines(crs=ccrs.PlateCarree(),
                  linewidth=.25, color='gray', alpha=0.5, linestyle='--')
    g1.xlocator = ticker.FixedLocator([-156, -160, -164, -168, -172, -176, 180])
    g1.ylocator = ticker.FixedLocator([64, 66, 68, 70, 72, 74, 76])
    g1.xformatter = LONGITUDE_FORMATTER
    g1.yformatter = LATITUDE_FORMATTER
    g1.ylabels_left = True
    g1.xlabels_top = True

    plt.savefig('ArcticHeat_SST.png', dpi = (300))
    plt.close()