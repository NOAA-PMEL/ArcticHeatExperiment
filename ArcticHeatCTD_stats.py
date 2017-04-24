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
parser.add_argument('--maxdepth', type=float, 
	help="known bathymetric depth at location")


args = parser.parse_args()

#TODO: Duplicate code in xbt/axctd data can be combined to a more simpler routine

#######
# axctd
#
if args.axctd:
	axctddata = pd.read_csv(args.filepath, delim_whitespace=True, skiprows=4, na_values='*****')

	Tmax = axctddata['Temp'].where(axctddata['Depth'] <= args.maxdepth).max()
	Tmin = axctddata['Temp'].where(axctddata['Depth'] <= args.maxdepth).min()
	Tave = axctddata['Temp'].where(axctddata['Depth'] <= args.maxdepth).mean()
	Tstd = axctddata['Temp'].where(axctddata['Depth'] <= args.maxdepth).std()

	print("{file},{mean},{min},{max},{std}".format(file=args.filepath,mean=Tave,min=Tmin,max=Tmax,std=Tstd))

#####
# xbt
#
if args.xbt:
	xbtdata = pd.read_csv(args.filepath, delim_whitespace=True, skiprows=3, na_values='******')

	Tmax = xbtdata['(C)'].where(xbtdata['Depth'] <= args.maxdepth).max()
	Tmin = xbtdata['(C)'].where(xbtdata['Depth'] <= args.maxdepth).min()
	Tave = xbtdata['(C)'].where(xbtdata['Depth'] <= args.maxdepth).mean()
	Tstd = xbtdata['(C)'].where(xbtdata['Depth'] <= args.maxdepth).std()

	print("{file},{mean},{min},{max},{std}".format(file=args.filepath,mean=Tave,min=Tmin,max=Tmax,std=Tstd))
