#!/usr/bin/env python

"""

 Background:
 --------
 ArcticHeatCTD_stats.py
 
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



__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2016, 9, 22)
__modified__ = datetime.datetime(2016, 9, 22)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'arctic heat','ctd','FOCI', 'wood', 'kevin'

"""----------------------------- Main -------------------------------------"""

parser = argparse.ArgumentParser(description='ArcticHeat ctd datafile parser ')
parser.add_argument('filepath', metavar='filepath', type=str,
               help='full path to file')
parser.add_argument('-xbt','--xbt', action="store_true",
	help='work with xbt data')
parser.add_argument('-axctd','--axctd', action="store_true",
	help='work with axctd data')
parser.add_argument('-bd','--binned_data', action="store_true",
	help='output binned profile data')
parser.add_argument('--maxdepth', type=float, 
	help="known bathymetric depth at location")


args = parser.parse_args()

#######
# axctd
#
if args.axctd:
	axctddata = pd.read_excel(args.filepath, sheetname=0)

	bins = np.arange(0,args.maxdepth,0.5)
	axctd_0p5m_bin = axctddata.groupby(np.floor(axctddata.Depth *2) / 2).median()
	#groupby makes index the wanted var to  sort by
	axctd_0p5m_bin['Depth']=axctd_0p5m_bin.index

	Tmax = axctd_0p5m_bin['Temp'].where(axctd_0p5m_bin['Depth'] <= args.maxdepth).max()
	Tmin = axctd_0p5m_bin['Temp'].where(axctd_0p5m_bin['Depth'] <= args.maxdepth).min()
	Tave = axctd_0p5m_bin['Temp'].where(axctd_0p5m_bin['Depth'] <= args.maxdepth).mean()
	Tmid = axctd_0p5m_bin['Temp'].where(axctd_0p5m_bin['Depth'] <= args.maxdepth).median()
	Tstd = axctd_0p5m_bin['Temp'].where(axctd_0p5m_bin['Depth'] <= args.maxdepth).std()

	print("{file},{mean},{min},{max},{mid},{std}".format(file=args.filepath,mean=Tave,min=Tmin,max=Tmax,mid=Tmid,std=Tstd))

	if args.binned_data:
		axctd_0p5m_bin.where(axctd_0p5m_bin['Depth'] <= args.maxdepth)[['Depth','Temp','Salinity']].to_csv(args.filepath + '_0p5m_binned.csv', sep=',', encoding='utf-8',  index = False)
#####
# xbt
#
if args.xbt:
	xbtdata = pd.read_csv(args.filepath, delim_whitespace=True, skiprows=3, na_values='******')
	
	bins = np.arange(0,args.maxdepth,0.5)
	xbt_0p5m_bin = xbtdata.groupby(np.floor(xbtdata.Depth *2) / 2).median()
	#groupby makes index the wanted var to  sort by
	xbt_0p5m_bin['Depth']=xbt_0p5m_bin.index

	Tmax = xbt_0p5m_bin['(C)'].where(xbt_0p5m_bin['Depth'] <= args.maxdepth).max()
	Tmin = xbt_0p5m_bin['(C)'].where(xbt_0p5m_bin['Depth'] <= args.maxdepth).min()
	Tave = xbt_0p5m_bin['(C)'].where(xbt_0p5m_bin['Depth'] <= args.maxdepth).mean()
	Tmid = xbt_0p5m_bin['(C)'].where(xbt_0p5m_bin['Depth'] <= args.maxdepth).median()
	Tstd = xbt_0p5m_bin['(C)'].where(xbt_0p5m_bin['Depth'] <= args.maxdepth).std()

	print("{file},{mean},{min},{max},{mid},{std}".format(file=args.filepath,mean=Tave,min=Tmin,max=Tmax,mid=Tmid,std=Tstd))

	if args.binned_data:
		print("Saving file to {path}_0p5m_binned.csv".format(path=args.filepath))
		xbt_0p5m_bin.where(xbt_0p5m_bin['Depth'] <= args.maxdepth)[['Depth','(C)']].to_csv(args.filepath + '_0p5m_binned.csv', sep=',', encoding='utf-8',  index=False)


