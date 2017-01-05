#!/usr/bin/env python

"""

 Background:
 --------
 ArcticHeatCTDsparklines.py
 
 Purpose:
 --------
 Create miniature sparkline CTD plots for XBT/AXCTD data

 History:
 --------
 2016-09-27 - add AXCTD code
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

from io_utils.EcoFOCI_db_io import EcoFOCI_db_ALAMO

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 9, 22)
__modified__ = datetime.datetime(2016, 9, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'arctic heat','ctd','FOCI', 'wood', 'kevin'

mpl.rcParams['axes.grid'] = False
mpl.rcParams['axes.edgecolor'] = 'white'
mpl.rcParams['axes.linewidth'] = 0.25
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['grid.linestyle'] = '--'
mpl.rcParams['xtick.major.size'] = 2
mpl.rcParams['xtick.minor.size'] = 1
mpl.rcParams['xtick.major.width'] = 0.25
mpl.rcParams['xtick.minor.width'] = 0.25
mpl.rcParams['ytick.major.size'] = 2
mpl.rcParams['ytick.minor.size'] = 1
mpl.rcParams['xtick.major.width'] = 0.25
mpl.rcParams['xtick.minor.width'] = 0.25
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.color'] = 'grey'
mpl.rcParams['xtick.color'] = 'grey'
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
parser.add_argument('-xbt','--xbt', action="store_true",
	help='work with xbt data')
parser.add_argument('-axctd','--axctd', action="store_true",
	help='work with axctd data')
parser.add_argument('--save_excel', action="store_true", 
	help="save profile to excel - excel filename")
parser.add_argument('--maxdepth', type=float, 
	help="known bathymetric depth at location")
parser.add_argument('--paramspan', nargs='+', type=float, 
	help="max,min of parameter")
parser.add_argument('-alamo','--alamofloats', type=str,
	help='work with alamo float data in sql database')
parser.add_argument('-alamocycle','--alamofloats_cycle', type=int, nargs=2,
	help='start and stop range for cycle number')
parser.add_argument('-plot_cbz','--plot_cb_zero', type=float, 
	help='Colorbar inflection value for divergent color scheme')
args = parser.parse_args()

#TODO: Duplicate code in xbt/axctd data can be combined to a more simpler routine

#######
# axctd
#
if args.axctd:
	axctddata = pd.read_csv(args.filepath, delim_whitespace=True, skiprows=4, na_values='*****')

	if args.maxdepth:
		figscale = args.maxdepth / 15. #makes most of the chukchi a 1x3 inch image
	else:
		figscale = 3.

	fig = plt.figure(1, figsize=(1, 3), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)

	p1 = ax1.scatter(axctddata['Temp'],axctddata['Depth'],8,marker='.', edgecolors='none', c=axctddata['Temp'], 
        norm=MidpointNormalize(midpoint=0.),
        vmin=args.paramspan[0], vmax=args.paramspan[1], 
        cmap='seismic')

	p1 = ax1.plot(np.zeros_like(axctddata['Depth']),axctddata['Depth'],'grey',linewidth=.15)
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
	plt.savefig(args.filepath.split('.')[0] + '.png', transparent=True, dpi = (150))
	plt.close()

	if args.save_excel:
		writer = pd.ExcelWriter(args.filepath.split('.')[0] + '.xlsx')
		axctddata.to_excel(writer,sheet_name=args.filepath.split('/')[-1].split('_')[0])



#####
# xbt
#
if args.xbt:
	xbtdata = pd.read_csv(args.filepath, delim_whitespace=True, skiprows=3, na_values='******')

	if args.maxdepth:
		figscale = args.maxdepth / 15. #makes most of the chukchi a 1x3 inch image
	else:
		figscale = 3.

	fig = plt.figure(1, figsize=(1, 3), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)
	#p1 = ax1.plot(xbtdata['(C)'],xbtdata['Depth'],'r')
	p1 = ax1.scatter(xbtdata['(C)'],xbtdata['Depth'],8,marker='.', edgecolors='none', c=xbtdata['(C)'], 
        norm=MidpointNormalize(midpoint=0.),
        vmin=args.paramspan[0], vmax=args.paramspan[1], 
        cmap='seismic')

	p1 = ax1.plot(np.zeros_like(xbtdata['Depth']),xbtdata['Depth'],'grey',linewidth=.15)
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
	plt.savefig(args.filepath.split('.')[0] + '.png', transparent=True, dpi = (150))
	plt.close()

	if args.save_excel:
		writer = pd.ExcelWriter(args.filepath.split('.')[0] + '.xlsx')
		xbtdata.to_excel(writer,sheet_name=args.filepath.split('/')[-1])

#####
# alamo floats
#
if args.alamofloats and (args.alamofloats_cycle[0] ==args.alamofloats_cycle[1] ):

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

if args.alamofloats and not (args.alamofloats_cycle[0] == args.alamofloats_cycle[1] ):

	startcycle=args.alamofloats_cycle[0]
	endcycle=args.alamofloats_cycle[1]

	#get information from local config file - a json formatted file
	config_file = 'EcoFOCI_config/db_config/db_config_alamofloats.pyini'


	EcoFOCI_db = EcoFOCI_db_ALAMO()
	(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

	figscale = endcycle-startcycle

	fig = plt.figure(1, figsize=(figscale/3, 3), facecolor='w', edgecolor='w')
	ax1 = fig.add_subplot(111)
	plt.hold(True)

	for cycle in range(startcycle,endcycle+1,1):
		offset = cycle - startcycle
		offset = 0
		#get db meta information for mooring
		table = args.alamofloats
		Profile = EcoFOCI_db.read_profile(table=table, CycleNumber=cycle, verbose=True)

		Pressure = np.array(sorted(Profile.keys()))
		Temperature = np.array([Profile[x]['Temperature'] for x in sorted(Profile.keys()) ])


		p1 = ax1.scatter(Temperature+3*offset,Pressure,45,marker='.', edgecolors='none', c=Temperature, 
	        norm=MidpointNormalize(midpoint=args.plot_cb_zero),
	        vmin=args.paramspan[0], vmax=args.paramspan[1], 
	        cmap='RdBu_r')#seismic or RdBu_r

	#p1 = ax1.plot(np.zeros_like(Pressure),Pressure,'grey',linewidth=.15)
	#ax1.set_yticks(np.arange(0.,args.maxdepth + 25.,10.))

	if args.maxdepth:
		ax1.set_ylim([0,args.maxdepth])

	ax1.set_xlim([args.paramspan[0],args.paramspan[1]+3*figscale+1])

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
