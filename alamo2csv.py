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

def IBCAO_data():
    """ read in IBCAO topography/bathymetry. """
    file_in = '/Volumes/WDC_internal/Users/bell/in_and_outbox/MapGrids/ARDEMv2.0.nc'
    IBCAOtopodata = Dataset(file_in)
    
    topoin = IBCAOtopodata.variables['z'][:]
    lons = IBCAOtopodata.variables['lon'][:] #degrees east
    lats = IBCAOtopodata.variables['lat'][:]
    IBCAOtopodata.close()
    
 
    return(topoin, lats, lons)

def find_nearest(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx

"""---------------------------------- Main --------------------------------------------"""

parser = argparse.ArgumentParser(description='Convert .nc to .csv screen output')
#parser.add_argument('infile', metavar='infile', type=str, help='input file path')
parser.add_argument("-csv_out","--csv_out", action="store_true",
        help='output non-epic formatted netcdf as csv')
args = parser.parse_args()

path = '/Volumes/WDC_internal/Users/bell/in_and_outbox/2016/wood/ArcticHeat/AlamoFloats/'
infile = ['arctic_heat_alamo_profiles_9058_9f75_d5e5_f5f9.nc',
		  'arctic_heat_alamo_profiles_9076_6c2c_4984_d7e4.nc',
		  'arctic_heat_alamo_profiles_9085_a189_de6c_cb81.nc',
		  'arctic_heat_alamo_profiles_9115_bb97_cc7e_a9c0.nc',
		  'arctic_heat_alamo_profiles_9116_5d1b_e525_f403.nc']
###nc readin/out
df = EcoFOCI_netCDF(path+infile[0])
global_atts = df.get_global_atts()
vars_dic = df.get_vars()
data0 = df.ncreadfile_dic()

df = EcoFOCI_netCDF(path+infile[1])
global_atts = df.get_global_atts()
vars_dic = df.get_vars()
data1 = df.ncreadfile_dic()

df = EcoFOCI_netCDF(path+infile[2])
global_atts = df.get_global_atts()
vars_dic = df.get_vars()
data2 = df.ncreadfile_dic()

df = EcoFOCI_netCDF(path+infile[3])
global_atts = df.get_global_atts()
vars_dic = df.get_vars()
data3 = df.ncreadfile_dic()

df = EcoFOCI_netCDF(path+infile[4])
global_atts = df.get_global_atts()
vars_dic = df.get_vars()
data4 = df.ncreadfile_dic()
"""---"""

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

dtime = num2date(data0['time'],'seconds since 1970-01-01')
doy0 = [x.timetuple().tm_yday for x in dtime]
dtime = num2date(data1['time'],'seconds since 1970-01-01')
doy1 = [x.timetuple().tm_yday for x in dtime]
dtime = num2date(data2['time'],'seconds since 1970-01-01')
doy2 = [x.timetuple().tm_yday for x in dtime]
dtime = num2date(data3['time'],'seconds since 1970-01-01')
doy3 = [x.timetuple().tm_yday for x in dtime]
dtime = num2date(data4['time'],'seconds since 1970-01-01')
doy4 = [x.timetuple().tm_yday for x in dtime]

#### plot
etopo_levels=[-1000, -100, -50, -25, ]  #chuckchi

(topoin, elats, elons) = etopo1_subset()
#(topoin, elats, elons) = etopo5_data()



#determine regional bounding
y1 = np.floor(data0['latitude'].min()-2.5)
y2 = np.ceil(data0['latitude'].max()+2.5)
x1 = np.ceil((data0['longitude'].min()-5))
x2 = np.floor((data0['longitude'].max()+5))

fig = plt.figure()
ax = plt.subplot(111)
        
m = Basemap(resolution='i',projection='merc', llcrnrlat=y1, \
            urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,\
            lat_ts=45)

elons, elats = np.meshgrid(elons, elats)
ex, ey = m(elons, elats)
xd0,yd0 = m(data0['longitude'],data0['latitude'])
xd1,yd1 = m(data1['longitude'],data1['latitude'])
xd2,yd2 = m(data2['longitude'],data2['latitude'])
xd3,yd3 = m(data3['longitude'],data3['latitude'])
xd4,yd4 = m(data4['longitude'],data4['latitude'])

#CS = m.imshow(topoin, cmap='Greys_r') #
CS_l = m.contour(ex,ey,topoin, levels=etopo_levels, linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
CS = m.contourf(ex,ey,topoin, levels=etopo_levels, colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75) 
plt.clabel(CS_l, inline=1, fontsize=8, fmt='%1.0f')

m.scatter(xd0,yd0,40,marker='.', edgecolors='none', c=doy0, vmin=120, vmax=300, cmap='viridis')
m.scatter(xd1,yd1,40,marker='.', edgecolors='none', c=doy1, vmin=120, vmax=300, cmap='viridis')
m.scatter(xd2,yd2,40,marker='.', edgecolors='none', c=doy2, vmin=120, vmax=300, cmap='viridis')
m.scatter(xd3,yd3,40,marker='.', edgecolors='none', c=doy3, vmin=120, vmax=300, cmap='viridis')
m.scatter(xd4,yd4,40,marker='.', edgecolors='none', c=doy4, vmin=120, vmax=300, cmap='viridis')
c = plt.colorbar()
c.set_label("Julian Day")

m.plot(xd0[0],yd0[0], '+', markersize=10, color='k')
m.plot(xd1[0],yd1[0], '+', markersize=10, color='k')
m.plot(xd2[0],yd2[0], '+', markersize=10, color='k')
m.plot(xd3[0],yd3[0], '+', markersize=10, color='k')
m.plot(xd4[0],yd4[0], '+', markersize=10, color='k')

#m.drawcountries(linewidth=0.5)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(y1-10,y2+10,2.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
m.drawmeridians(np.arange(x1-10,x2+10,4.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
m.fillcontinents(color='white')

#

DefaultSize = fig.get_size_inches()
fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )
plt.savefig('images/ArcticHeat_Alamo_etopo1.png', bbox_inches='tight', dpi=300)
plt.close()