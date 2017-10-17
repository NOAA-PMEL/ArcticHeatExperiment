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
import cmocean

#%%
#User Stack
from io_utils.EcoFOCI_netCDF_read import EcoFOCI_netCDF

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2016, 8, 10)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header', 'csv'


### Plot settings
mpl.rcParams['axes.grid'] = False
mpl.rcParams['axes.edgecolor'] = 'black'
mpl.rcParams['axes.linewidth'] = 0.5
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['xtick.major.size'] = 4
mpl.rcParams['xtick.minor.size'] = 2
mpl.rcParams['xtick.major.width'] = 2
mpl.rcParams['xtick.minor.width'] = 1
mpl.rcParams['ytick.major.size'] = 6
mpl.rcParams['ytick.minor.size'] = 2
mpl.rcParams['ytick.major.width'] = 2
mpl.rcParams['ytick.minor.width'] = 1
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.color'] = 'k'
mpl.rcParams['xtick.color'] = 'k'
mpl.rcParams['font.size'] = 18
mpl.rcParams['font.sans-serif'] = "Arial"
mpl.rcParams['font.family'] = "sans-serif"
mpl.rcParams['font.weight'] = 'medium'
mpl.rcParams['svg.fonttype'] = 'none'

def etopo1_subset(file='etopo1.nc', region=None):
    """ read in ardemV2 topography/bathymetry. """
    
    file='/Volumes/WDC_internal/Users/bell/in_and_outbox/Ongoing_Analysis/MapGrids/etopo_subsets/etopo1_chukchi.nc'
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
parser.add_argument('infile', metavar='infile', type=str, help='input file path')
parser.add_argument("-csv","--csv", action="store_true",
        help='output non-epic formatted netcdf as csv')
parser.add_argument("-is_whoi","--is_whoi", action="store_true",
        help='flag if is directly from WHOI')
parser.add_argument("-plots","--plots", action="store_true",
        help='generate plots')
args = parser.parse_args()



###nc readin/out
file1 = '/Volumes/WDC_internal/Users/bell/ecoraid/2016/Additional_FieldData/ArcticHeat/AlamoFloats/netcdf/arctic_heat_alamo_profiles_9058_9f75_d5e5_f5f9.nc'
df = EcoFOCI_netCDF(file1)
global_atts = df.get_global_atts()
vars_dic = df.get_vars()
dims = df.get_dims()
data0 = df.ncreadfile_dic()
df.close()

file2 = '/Volumes/WDC_internal/Users/bell/ecoraid/2016/Additional_FieldData/ArcticHeat/AlamoFloats/netcdf/arctic_heat_alamo_profiles_9115_bb97_cc7e_a9c0.nc'
df = EcoFOCI_netCDF(file2)
global_atts = df.get_global_atts()
vars_dic = df.get_vars()
dims = df.get_dims()
data1 = df.ncreadfile_dic()

if args.is_whoi:
    timestr = 'days since 1950-01-01T00:00:00Z'
else:
    timestr = 'seconds since 1970-01-01'

skipped_vars = ['STATION_PARAMETERS','FLOAT_SERIAL_NO',
                'REFERENCE_DATE_TIME','time', 'profileid',
                'PLATFORM_NUMBER','JULD','JULD_LOCATION']

if args.csv:
    if args.is_whoi:

        line = 'time, CycleNumber'
        for k in vars_dic.keys():
            if k in ['PRES','TEMP','PSAL']:
                line = line + ', ' + str(k)
        print line

        for j in range(0,dims['N_LEVELS'].size):
            line = num2date(data1['JULD'][0],timestr).strftime('%Y-%m-%d %H:%M:%S')
            line = line + ', ' + str(data1['CYCLE_NUMBER'][0])
            for k in vars_dic.keys():
                if k in ['PRES','TEMP','PSAL']:
                    line = line + ', ' + str(data1[k][0][j])
            print line
    else:
        line = 'time'
        for k in vars_dic.keys():
            if k not in ['FLOAT_SERIAL_NO','REFERENCE_DATE_TIME','time', 'profileid']:
                line = line + ', ' + str(k)
        print line

        for i, val in enumerate(data1['time']):
            line = num2date(val,timestr).strftime('%Y-%m-%d %H:%M:%S')
            for k in vars_dic.keys():
                if k not in ['FLOAT_SERIAL_NO','REFERENCE_DATE_TIME','time', 'profileid']:
                    line = line + ', ' + str(data1[k][i])
            print line


df.close()

#--

if args.plots:
    doy_plt = False
    if doy_plt:
        dtime = num2date(data0['time'],timestr)
        doy0 = [x.timetuple().tm_yday for x in dtime]
        dtime = num2date(data1['time'],timestr)
        doy1 = [x.timetuple().tm_yday for x in dtime]

    mono_col_plt = True
    if doy_plt:
        dtime = num2date(data0['time'],timestr)
        doy0 = [x.timetuple().tm_yday for x in dtime]
        dtime = num2date(data1['time'],timestr)
        doy1 = [x.timetuple().tm_yday for x in dtime]


    sfc_tmp_plt = False
    if sfc_tmp_plt:
        temp_data0,lat_data0, lon_data0 = [],[],[]
        for ind in list(set(data0['CYCLE_NUMBER'])):
            temp_data0 = temp_data0 + [max(data0['TEMP'][data0['CYCLE_NUMBER'] == ind])]
            lat_data0 = lat_data0 + [max(data0['latitude'][data0['CYCLE_NUMBER'] == ind])]
            lon_data0 = lon_data0 + [max(data0['longitude'][data0['CYCLE_NUMBER'] == ind])]
        temp_data1,lat_data1, lon_data1 = [],[],[]
        for ind in list(set(data1['CYCLE_NUMBER'])):
            temp_data1 = temp_data1 + [max(data1['TEMP'][data1['CYCLE_NUMBER'] == ind])]
            lat_data1 = lat_data1 + [max(data1['latitude'][data1['CYCLE_NUMBER'] == ind])]
            lon_data1 = lon_data1 + [max(data1['longitude'][data1['CYCLE_NUMBER'] == ind])]

    btm_tmp_plt = False
    if btm_tmp_plt:
        temp_data0,lat_data0, lon_data0 = [],[],[]
        for ind in list(set(data0['CYCLE_NUMBER'])):
            temp_data0 = temp_data0 + [min(data0['TEMP'][data0['CYCLE_NUMBER'] == ind])]
            lat_data0 = lat_data0 + [min(data0['latitude'][data0['CYCLE_NUMBER'] == ind])]
            lon_data0 = lon_data0 + [min(data0['longitude'][data0['CYCLE_NUMBER'] == ind])]
        temp_data1,lat_data1, lon_data1 = [],[],[]
        for ind in list(set(data1['CYCLE_NUMBER'])):
            temp_data1 = temp_data1 + [min(data1['TEMP'][data1['CYCLE_NUMBER'] == ind])]
            lat_data1 = lat_data1 + [min(data1['latitude'][data1['CYCLE_NUMBER'] == ind])]
            lon_data1 = lon_data1 + [min(data1['longitude'][data1['CYCLE_NUMBER'] == ind])]

    ave_tmp_plt = False
    if ave_tmp_plt:
        temp_data0,lat_data0, lon_data0 = [],[],[]
        for ind in list(set(data0['CYCLE_NUMBER'])):
            temp_data0 = temp_data0 + [np.mean(data0['TEMP'][np.where((data0['PRES'][data0['CYCLE_NUMBER'] == ind] > 0.5) & (data0['PRES'][data0['CYCLE_NUMBER'] == ind] <= 35))])]
            lat_data0 = lat_data0 + [min(data0['latitude'][data0['CYCLE_NUMBER'] == ind])]
            lon_data0 = lon_data0 + [min(data0['longitude'][data0['CYCLE_NUMBER'] == ind])]
        temp_data1,lat_data1, lon_data1 = [],[],[]
        for ind in list(set(data1['CYCLE_NUMBER'])):
            temp_data1 = temp_data1 + [np.mean(data1['TEMP'][np.where((data1['PRES'][data1['CYCLE_NUMBER'] == ind] > 0.5) & (data1['PRES'][data1['CYCLE_NUMBER'] == ind] <= 35))])]
            lat_data1 = lat_data1 + [min(data1['latitude'][data1['CYCLE_NUMBER'] == ind])]
            lon_data1 = lon_data1 + [min(data1['longitude'][data1['CYCLE_NUMBER'] == ind])]

    plot_moorings = False
    if plot_moorings:
        #2015
        mlat = [71.23013333,72.46685,71.04641667,71.23075,70.8385,71.04785,71.23048333,70.83565,71.24101667]
        mlon = -1.*np.array([164.2206167,156.5496167,160.5148667,164.2158833,163.10535,160.51155,164.21015,163.12385,164.30135])
    #### plot
    etopo_levels=[-1000, -100, -50, -25, ]  #chuckchi

    (topoin, elats, elons) = etopo1_subset()
    #(topoin, elats, elons) = etopo5_data()



    #determine regional bounding
    y1 = np.floor(data0['latitude'].min()-2.5)
    y2 = np.ceil(data0['latitude'].max()+2.5)
    x1 = np.ceil((data0['longitude'].min()-5))
    x2 = np.floor((data0['longitude'].max()+5))
    print y1,y2,x1,x2
    y1=64.0
    y2=76.0
    x1=-173.0
    x2=-137.0


    fig = plt.figure()
    ax = plt.subplot(111)
            
    m = Basemap(resolution='i',projection='merc', llcrnrlat=66, \
                urcrnrlat=74,llcrnrlon=-170,urcrnrlon=-150,\
                lat_ts=45)

    elons, elats = np.meshgrid(elons, elats)
    ex, ey = m(elons, elats)
    if doy_plt:
        xd0,yd0 = m(data0['longitude'],data0['latitude'])
        xd1,yd1 = m(data1['longitude'],data1['latitude'])
    if sfc_tmp_plt:
        xd0,yd0 = m(lon_data0,lat_data0)
        xd1,yd1 = m(lon_data1,lat_data1)
    if btm_tmp_plt:
        xd0,yd0 = m(lon_data0,lat_data0)
        xd1,yd1 = m(lon_data1,lat_data1)
    if ave_tmp_plt:
        xd0,yd0 = m(lon_data0,lat_data0)
        xd1,yd1 = m(lon_data1,lat_data1)
    if plot_moorings:
        mx, my = m(mlon, mlat)
    if mono_col_plt:
        xd0,yd0 = m(data0['longitude'],data0['latitude'])
        #manually add another point
        #xd0,yd0 = m(np.hstack([data0['longitude'],[-156.6]]),np.hstack([data0['latitude'],[71.6]]))
        xd1,yd1 = m(data1['longitude'],data1['latitude'])

    #CS = m.imshow(topoin, cmap='Greys_r') #
    CS_l = m.contour(ex,ey,topoin, levels=etopo_levels, linestyle='--', linewidths=0.2, colors='black', alpha=.75) 
    CS = m.contourf(ex,ey,topoin, levels=etopo_levels, colors=('#737373','#969696','#bdbdbd','#d9d9d9','#f0f0f0'), extend='both', alpha=.75) 
    plt.clabel(CS_l, inline=1, fontsize=8, fmt='%1.0f')

    if doy_plt:
        m.scatter(xd0,yd0,100,marker='.', edgecolors='none', c=doy0, vmin=245, vmax=360, cmap='viridis')
        m.scatter(xd1,yd1,100,marker='.', edgecolors='none', c=doy1, vmin=245, vmax=360, cmap='viridis')
        c = plt.colorbar()
        c.set_label("DOY")
    if sfc_tmp_plt:
        m.scatter(xd0,yd0,100,marker='.', edgecolors='none', c=temp_data0, vmin=-4, vmax=10, cmap=cmocean.cm.thermal)
        m.scatter(xd1,yd1,100,marker='.', edgecolors='none', c=temp_data1, vmin=-4, vmax=10, cmap=cmocean.cm.thermal)
        c = plt.colorbar()
        c.set_label("~SFC Temperature")
    if btm_tmp_plt:
        m.scatter(xd0,yd0,100,marker='.', edgecolors='none', c=temp_data0, vmin=-4, vmax=10, cmap=cmocean.cm.thermal)
        m.scatter(xd1,yd1,100,marker='.', edgecolors='none', c=temp_data1, vmin=-4, vmax=10, cmap=cmocean.cm.thermal)
        c = plt.colorbar()
        c.set_label("~BTM Temperature")
    if ave_tmp_plt:
        m.scatter(xd0,yd0,100,marker='.', edgecolors='none', c=temp_data0, vmin=-4, vmax=10, cmap=cmocean.cm.thermal)
        m.scatter(xd1,yd1,100,marker='.', edgecolors='none', c=temp_data1, vmin=-4, vmax=10, cmap=cmocean.cm.thermal)
        c = plt.colorbar()
        c.set_label("~BTM Temperature")
    if mono_col_plt:
        m.scatter(xd0,yd0,60,marker='.', edgecolors='none', c='#004499')
        m.scatter(xd1,yd1,60,marker='.', edgecolors='none', c='#299387')


    m.plot(xd0[0],yd0[0], '+', markersize=10, color='k')
    m.plot(xd1[0],yd1[0], '+', markersize=10, color='k')

    if plot_moorings:
        m.plot(mx,my,'o', markersize=8, markerfacecolor='None', color='k',markeredgewidth=2)

    #m.drawcountries(linewidth=0.5)
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(y1-10,y2+10,2.),labels=[1,0,0,0],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw parallels
    m.drawmeridians(np.arange(x1-10,x2+10,4.),labels=[0,0,0,1],color='black',dashes=[1,1],labelstyle='+/-',linewidth=0.2) # draw meridians
    m.fillcontinents(color='white')

    #

    DefaultSize = fig.get_size_inches()
    fig.set_size_inches( (DefaultSize[0]*1.5, DefaultSize[1]*1.5) )
    plt.savefig('images/ArcticHeat_Alamo_etopo1_temp_doy.png', bbox_inches='tight', dpi=300)
    plt.close()