#!/usr/bin/env python

"""
 alamo2csv.py

 [u'TEMP', 
 u'JULD', 
 u'FLOAT_SERIAL_NO', 
 u'PSAL', 
 u'REFERENCE_DATE_TIME', 
 u'longitude', 
 u'time', u'latitude', u'profileid', u'CYCLE_NUMBER', u'PRES']

 History:
 --------
 2016-10-26

"""

#System Stack
import datetime
import os
import argparse

#Science Stack
from netCDF4 import Dataset, date2num, num2date
import numpy as np

# Plotting Stack
import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap, shiftgrid
import matplotlib.pyplot as plt
import matplotlib as mpl

#User Stack
from calc import EPIC2Datetime
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2016, 8, 10)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'csv'


def etopo1_subset(file='etopo1.nc', region=None):
    """ read in ardemV2 topography/bathymetry. """
    
    file='/Volumes/WDC_internal/Users/bell/in_and_outbox/MapGrids/etopo_subsets/etopo1_chukchi.nc'
    bathydata = Dataset(file)
    
    topoin = bathydata.variables['Band1'][:]
    lons = bathydata.variables['lon'][:]
    lats = bathydata.variables['lat'][:]
    bathydata.close()
    
    return(topoin, lats, lons)

def etopo5_data():
    """ read in etopo5 topography/bathymetry. """
    file = '/Volumes/WDC_internal/Users/bell/in_and_outbox/MapGrids/etopo5.nc'
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

"""---------------------------------- Main --------------------------------------------"""

parser = argparse.ArgumentParser(description='Convert .nc to .csv screen output')
parser.add_argument('infile', metavar='infile', type=str, help='input file path')
parser.add_argument("-csv_out","--csv_out", action="store_true",
        help='output non-epic formatted netcdf as csv')
args = parser.parse_args()


###nc readin/out
ncfile = args.infile
df = EcoFOCI_netCDF(ncfile)
global_atts = df.get_global_atts()
vars_dic = df.get_vars()
data = df.ncreadfile_dic()

if args.csv_out:

	line = 'time'
	for k in vars_dic.keys():
		if k not in ['FLOAT_SERIAL_NO','REFERENCE_DATE_TIME','time', 'profileid']:
			line = line + ', ' + str(k)
	print line

	for i, val in enumerate(data['time']):
		line = num2date(val,'seconds since 1970-01-01').strftime('%Y-%m-%d %H:%M:%S')
		for k in vars_dic.keys():
			if k not in ['FLOAT_SERIAL_NO','REFERENCE_DATE_TIME','time', 'profileid']:
				line = line + ', ' + str(data[k][i])
		print line

dtime = num2date(data['time'],'seconds since 1970-01-01')
doy = [x.timetuple().tm_yday for x in dtime]

#### plot
etopo_levels=[-1000, -100, -50, -25, ]  #chuckchi

#(topoin, lats, lons) = etopo1_subset()
#elons, elats = np.meshgrid(lons, lats)
(topoin, elats, elons) = etopo5_data()



#determine regional bounding
y1 = np.floor(data['latitude'].min()-5)
y2 = np.ceil(data['latitude'].max()+5)
x1 = np.ceil((data['longitude'].min()-10))
x2 = np.floor((data['longitude'].max()+10))

fig = plt.figure()
ax = plt.subplot(111)
        
m = Basemap(resolution='i',projection='merc', llcrnrlat=y1, \
            urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,\
            lat_ts=45)

elons, elats = np.meshgrid(elons, elats)
ex, ey = m(elons, elats)
x,y = m(data['longitude'],data['latitude'])

#CS = m.imshow(topoin, cmap='Greys_r') #
CS_l = m.contour(ex,ey,topoin, levels=etopo_levels, linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
CS = m.contourf(ex,ey,topoin, levels=etopo_levels, colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75) 
plt.clabel(CS_l, inline=1, fontsize=8, fmt='%1.0f')

m.scatter(x,y,20,marker='.', edgecolors='none', c=doy, vmin=0, vmax=365, cmap='viridis')
c = plt.colorbar()
c.set_label("Julian Day")

#m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(y1,y2,2.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
m.drawmeridians(np.arange(x1-20,x2,4.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.fillcontinents(color='white')

#

DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )
plt.savefig('images/ArcticHeat_Alamo.png', bbox_inches='tight', dpi=300)
plt.close()