#!/usr/bin/env python

"""

 Background:
 --------
 ArcticHeat_ALAMOplotting.py
 
 Purpose:
 --------
 Various routines for visualizing ALAMO data

 History:
 --------

"""

#System Stack
import datetime
import argparse

import numpy as np
import pandas as pd

# Visual Stack
import matplotlib as mpl
mpl.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.dates import YearLocator, WeekdayLocator, MonthLocator, DayLocator, HourLocator, DateFormatter
import matplotlib.ticker as ticker
import cmocean

from io_utils.EcoFOCI_db_io import EcoFOCI_db_ALAMO

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 9, 22)
__modified__ = datetime.datetime(2016, 9, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'arctic heat','ctd','FOCI', 'wood', 'kevin', 'alamo'

### Plot settings
mpl.rcParams['axes.grid'] = False
mpl.rcParams['axes.edgecolor'] = 'white'
mpl.rcParams['axes.linewidth'] = 0.25
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['xtick.major.size'] = 4
mpl.rcParams['xtick.minor.size'] = 3.75
mpl.rcParams['xtick.major.width'] = 2
mpl.rcParams['xtick.minor.width'] = 1.75
mpl.rcParams['ytick.major.size'] = 4
mpl.rcParams['ytick.minor.size'] = 3.75
mpl.rcParams['ytick.major.width'] = 2
mpl.rcParams['ytick.minor.width'] = 1.75
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.color'] = 'k'
mpl.rcParams['xtick.color'] = 'k'
mpl.rcParams['font.size'] = 24
mpl.rcParams['font.sans-serif'] = "Arial"
mpl.rcParams['font.family'] = "sans-serif"
mpl.rcParams['font.weight'] = 'medium'
mpl.rcParams['svg.fonttype'] = 'none'

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

parser = argparse.ArgumentParser(description='ArcticHeat ctd datafile parser ')
parser.add_argument('filepath', metavar='filepath', type=str,
			   help='full path to file')
parser.add_argument('--maxdepth', type=float, default=70, 
	help="known bathymetric depth at location")
parser.add_argument('--paramspan', nargs='+', type=float, 
	help="max,min of parameter")
parser.add_argument('-alamo','--alamofloats', type=str,
	help='work with alamo float data in sql database')
parser.add_argument('-alamocycle','--alamofloats_cycle', type=int, nargs=2,
	help='start and stop range for cycle number')
parser.add_argument('-plot_cbz','--plot_cb_zero', type=float, 
	help='Colorbar inflection value for divergent color scheme')
parser.add_argument('-c','--contour_plot', action="store_true",
	help='create a contour plot')
args = parser.parse_args()

#####
# alamo floats
#
if args.alamofloats and (args.alamofloats_cycle[0] ==args.alamofloats_cycle[1] ) and not args.contour_plot:

	startcycle=args.alamofloats_cycle[0]
	endcycle=args.alamofloats_cycle[1]

	#get information from local config file - a json formatted file
	config_file = 'EcoFOCI_config/db_config/db_config_alamofloats.pyini'


	EcoFOCI_db = EcoFOCI_db_ALAMO()
	(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

	#get db meta information for mooring
	table = '9085'
	Profile = EcoFOCI_db.read_profile(table=table, CycleNumber=startcycle, verbose=True)
	EcoFOCI_db.close()

	Pressure = np.array(sorted(Profile.keys()))
	Temperature = np.array([Profile[x]['Temperature'] for x in sorted(Profile.keys()) ])

	figscale = 3.

	fig = plt.figure(1, figsize=(1, 3), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)
	p1 = ax1.scatter(Temperature,Pressure,8,marker='.', edgecolors='none', c=Temperature, 
		norm=MidpointNormalize(midpoint=0.),
		vmin=args.paramspan[0], vmax=args.paramspan[1], 
		cmap='seismic')

	p1 = ax1.plot(np.zeros_like(Pressure),Pressure,'grey',linewidth=.15)
	ax1.set_yticks(np.arange(0.,args.maxdepth + 25.,10.))

	if args.maxdepth:
		ax1.set_ylim([0,args.maxdepth])

	if args.paramspan:
		ax1.set_xlim([args.paramspan[0],args.paramspan[1]])

	ax1.invert_yaxis()

	fmt=mpl.ticker.ScalarFormatter(useOffset=False)
	fmt.set_scientific(False)
	ax1.xaxis.set_major_formatter(fmt)
	ax1.tick_params(axis='both', which='major', bottom='off', top='off',labelbottom='off')
	ax1.yaxis.set_ticklabels([])
	plt.tight_layout()
	plt.savefig(args.filepath + '.png', transparent=True, dpi = (150))
	plt.close()

if args.alamofloats and not (args.alamofloats_cycle[0] == args.alamofloats_cycle[1] ) and not args.contour_plot:

	startcycle=args.alamofloats_cycle[0]
	endcycle=args.alamofloats_cycle[1]

	#get information from local config file - a json formatted file
	config_file = 'EcoFOCI_config/db_config/db_config_alamofloats.pyini'


	EcoFOCI_db = EcoFOCI_db_ALAMO()
	(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

	figscale = endcycle-startcycle

	fig = plt.figure(1, figsize=(figscale/3, 3), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)
	#plt.hold(True)

	for cycle in range(startcycle,endcycle+1,1):
		offset = cycle - startcycle
		#get db meta information for mooring
		table = args.alamofloats
		Profile = EcoFOCI_db.read_profile(table=table, CycleNumber=cycle, verbose=True)

		Pressure = np.array(sorted(Profile.keys()))
		Temperature = np.array([Profile[x]['Temperature'] for x in sorted(Profile.keys()) ])


		p1 = ax1.scatter(Temperature+1*offset,Pressure,45,marker='.', edgecolors='none', c=Temperature, 
			norm=MidpointNormalize(midpoint=args.plot_cb_zero),
			vmin=args.paramspan[0], vmax=args.paramspan[1], 
			cmap=cmocean.cm.thermal)#seismic or RdBu_r

	#p1 = ax1.plot(np.zeros_like(Pressure),Pressure,'grey',linewidth=.15)
	#ax1.set_yticks(np.arange(0.,args.maxdepth + 25.,10.))

	if args.maxdepth:
		ax1.set_ylim([0,args.maxdepth])

	ax1.set_xlim([args.paramspan[0],args.paramspan[1]+1*figscale+1])

	plt.colorbar(p1)
	ax1.invert_yaxis()

	fmt=mpl.ticker.ScalarFormatter(useOffset=False)
	fmt.set_scientific(False)
	ax1.xaxis.set_major_formatter(fmt)
	ax1.tick_params(axis='both', which='major', bottom='off', top='off',labelbottom='off')
	#ax1.yaxis.set_ticklabels([])
	plt.tight_layout()
	plt.savefig(args.filepath + '.png', transparent=False, dpi = (300))
	plt.close()

	EcoFOCI_db.close()

if args.contour_plot:

	startcycle=args.alamofloats_cycle[0]
	endcycle=args.alamofloats_cycle[1]

	#get information from local config file - a json formatted file
	config_file = 'EcoFOCI_config/db_config/db_config_alamofloats.pyini'


	EcoFOCI_db = EcoFOCI_db_ALAMO()
	(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

	depth_array = np.arange(0,args.maxdepth+1,0.5) 
	num_cycles = EcoFOCI_db.count(table=args.alamofloats, start=startcycle, end=endcycle)
	temparray = np.ones((num_cycles,len(depth_array)))*np.nan
	salarray = np.ones((num_cycles,len(depth_array)))*np.nan
	ProfileTime = []
	cycle_col=0

	fig = plt.figure(1, figsize=(18,6), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)		
	for cycle in range(startcycle,endcycle+1,1):
		#get db meta information for mooring
		Profile = EcoFOCI_db.read_profile(table=args.alamofloats, CycleNumber=cycle, verbose=True)

		try:
			temp_time =  Profile[sorted(Profile.keys())[0]]['ProfileTime']
			ProfileTime = ProfileTime + [temp_time]
			Pressure = np.array(sorted(Profile.keys()))
			Temperature = np.array([Profile[x]['Temperature'] for x in sorted(Profile.keys()) ])
			Salinity = np.array([Profile[x]['PSAL'] for x in sorted(Profile.keys()) ])
			Salinity[Salinity<30.] = np.nan

			temparray[cycle_col,:] = np.interp(depth_array,Pressure,Temperature,left=np.nan,right=np.nan)
			salarray[cycle_col,:] = np.interp(depth_array,Pressure,Salinity,left=np.nan,right=np.nan)
			cycle_col +=1
	
			xtime = np.ones_like(np.array(sorted(Profile.keys()))) * mpl.dates.date2num(temp_time)
			#turn off below and set zorder to 1 for no scatter plot colored by points
			#plt.scatter(x=xtime, y=np.array(sorted(Profile.keys())),s=1,marker='.', edgecolors='none', c='k', zorder=3, alpha=1) 
			
			plt.scatter(x=xtime, y=np.array(sorted(Profile.keys())),s=45,marker='.', edgecolors='none', c=Temperature, 
			vmin=args.paramspan[0], vmax=args.paramspan[1], 
			cmap=cmocean.cm.thermal, zorder=2)
		except IndexError:
			pass


	#cbar = plt.colorbar()
	#cbar.set_label('Temperature (C)',rotation=0, labelpad=90)
	plt.contourf(ProfileTime,depth_array,temparray.T, 
		extend='both', cmap=cmocean.cm.thermal, levels=np.arange(args.paramspan[0],args.paramspan[1],0.25), alpha=.95, zorder=1)
	CS=plt.contour(ProfileTime,depth_array,salarray.T,[32,32.5,33,33.5,34],linewidths=1.0,colors='#00FF00',zorder=4)
	plt.clabel(CS, inline=1, fontsize=18, fontweight='bold', fmt='%1.1f', manual=[(datetime.datetime(2016,6,9).toordinal(),30),(datetime.datetime(2016,6,8).toordinal(),50),(datetime.datetime(2016,6,9).toordinal(),40),(datetime.datetime(2016,6,9).toordinal()+0.75,35)])

	ax1.invert_yaxis()
	ax1.set_ylim([args.maxdepth,0])
	ax1.yaxis.set_minor_locator(ticker.MultipleLocator(5))
	ax1.xaxis.set_major_locator(DayLocator(bymonthday=range(1,31,2)))
	ax1.xaxis.set_minor_locator(DayLocator(bymonthday=range(1,31,1)))
	ax1.xaxis.set_minor_formatter(DateFormatter(''))
	ax1.xaxis.set_major_formatter(DateFormatter('%d'))
	ax1.xaxis.set_tick_params(which='major', pad=25)
	ax1.xaxis.set_tick_params(which='minor', pad=5)
	ax1.set_xlim([datetime.datetime(2016,06,7),datetime.datetime(2016,06,21)])

	plt.tight_layout()
	#plt.savefig(args.filepath + '.svg', transparent=False, dpi = (300))
	plt.savefig(args.filepath + '.png', transparent=False, dpi = (300))
	plt.close()