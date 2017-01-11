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
from netCDF4 import Dataset, date2num, num2date
import numpy as np

# Plotting Stack
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.mlab import bivariate_normal
import matplotlib.ticker as ticker
import cartopy.feature as cfeature
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from mpl_toolkits.basemap import Basemap, shiftgrid
import cmocean

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 06, 01)
__modified__ = datetime.datetime(2016, 06, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'arctic heat mapping', 'wood', 'kevin'

def etopo1_subset(region=None, file=None):
    """ read in ardemV2 topography/bathymetry. 
    file='/Volumes/WDC_internal/Users/bell/in_and_outbox/MapGrids/etopo_subsets/etopo1_chukchi.nc'

    """
    
    bathydata = Dataset(file)
    
    topoin = bathydata.variables['Band1'][:]
    lons = bathydata.variables['lon'][:]
    lats = bathydata.variables['lat'][:]
    bathydata.close()
    
    return(topoin, lats, lons)

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
parser.add_argument('--xbt', type=str, help='optional full path to excel file')
args = parser.parse_args()

## read data in
data = pd.read_csv(args.sourcedir,names=['lon','lat','alt','sst','pyro'],header=0)

if args.xbt:
    xbt = pd.read_excel(args.xbt,header=0)

range_int = 1.
extent = [data['lat'].min()-range_int, data['lat'].max()+range_int, \
          data['lon'].min()-range_int, data['lon'].max()+range_int]


maptype='basemap'
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

    if args.xbt:
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

elif maptype == 'basemap':
    etopo_levels=[-1000, -100, -50, -25, ]  #chuckchi

    (topoin, elats, elons) = etopo1_subset(file=args.mapdir)
    #(topoin, elats, elons) = etopo5_data()



    #determine regional bounding
    y1 = np.floor(data['lat'].min()-2.5)
    y2 = np.ceil(data['lat'].max()+2.5)
    x1 = np.ceil((data['lon'].min()-5))
    x2 = np.floor((data['lon'].max()+5))
    print y1,y2,x1,x2


    fig = plt.figure()
    ax = plt.subplot(111)
    
    """        
    m = Basemap(resolution='i',projection='merc', llcrnrlat=y1, \
                urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,\
                lat_ts=45)
    """
    m = Basemap(resolution='i',projection='merc', llcrnrlat=66, \
                urcrnrlat=74,llcrnrlon=-170,urcrnrlon=-150,\
                lat_ts=45)

    elons, elats = np.meshgrid(elons, elats)
    ex, ey = m(elons, elats)
    xd0,yd0 = m(data['lon'].values,data['lat'].values)

    #CS = m.imshow(topoin, cmap='Greys_r') #
    CS_l = m.contour(ex,ey,topoin, levels=etopo_levels, linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
    CS = m.contourf(ex,ey,topoin, levels=etopo_levels, colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75) 
    plt.clabel(CS_l, inline=1, fontsize=8, fmt='%1.0f')

    m.scatter(xd0,yd0,5,marker='.', edgecolors='none', color='black',zorder=2)
    data['sst'][data['alt'] > args.maxalt] = np.nan
    m.scatter(xd0,yd0,25,marker='.', edgecolors='none', c=data['sst'].values, vmin=-4, vmax=10, cmap=cmocean.cm.thermal, zorder=2)
    c = plt.colorbar()
    c.set_label("Rad SST / Flight Path")

    if args.xbt:
        """
        m.scatter(xd0,yd0,100,marker='o', edgecolors='none', c=temp_data0, vmin=-4, vmax=10, cmap=cmocean.cm.thermal)
        c = plt.colorbar()
        c.set_label("5m Temp")
        """
        ind =xbt[xbt['Thermocline']==0].index.tolist()
        xd1,yd1=m(xbt.Longitude[ind].values,xbt.Latitude[ind].values)
        m.scatter(xd1,yd1,50,marker='o', facecolors='none', edgecolors='k')
        ind =xbt[xbt['Thermocline']==1].index.tolist()
        xd1,yd1=m(xbt.Longitude[ind].values,xbt.Latitude[ind].values)
        m.scatter(xd1,yd1,50,marker='o', facecolors='k', edgecolors='k')
        ind =xbt[xbt['Thermocline']==-99].index.tolist()
        xd1,yd1=m(xbt.Longitude[ind].values,xbt.Latitude[ind].values)
        m.scatter(xd1,yd1,50,marker='x', facecolors='k', edgecolors='k')

    #m.drawcountries(linewidth=0.5)
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(y1-10,y2+10,2.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
    m.drawmeridians(np.arange(x1-10,x2+10,4.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
    m.fillcontinents(color='white')

    #

    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )
    plt.savefig('images/ArcticHeat_Alamo_etopo1_flight.png', bbox_inches='tight', dpi=300)
    plt.close()