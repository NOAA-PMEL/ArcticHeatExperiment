#!/usr/bin/env python

"""

 Background:
 --------
 ArcticHeat_ALAMO_functions.py
 
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


"""----------------------------- Main -------------------------------------"""

parser = argparse.ArgumentParser(description='ArcticHeat ctd datafile parser ')
parser.add_argument('-alamo','--alamofloats', type=str,
	help='work with alamo float data in sql database')
parser.add_argument('-alamocycle','--alamofloats_cycle', type=int, nargs=2,
	help='start and stop range for cycle number')

args = parser.parse_args()

#####
# alamo floats
#


startcycle=args.alamofloats_cycle[0]
endcycle=args.alamofloats_cycle[1]

#get information from local config file - a json formatted file
config_file = 'EcoFOCI_config/db_config/db_config_alamofloats.pyini'


EcoFOCI_db = EcoFOCI_db_ALAMO()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

num_cycles = EcoFOCI_db.count(table=args.alamofloats, 
	start=args.alamofloats_cycle[0], end=args.alamofloats_cycle[1])
	
for cycle in range(startcycle,endcycle+1,1):
	#get db meta information for mooring
	Profile = EcoFOCI_db.read_profile(table=args.alamofloats, CycleNumber=cycle, verbose=False)

	try:
		temp_time =  Profile[sorted(Profile.keys())[0]]['ProfileTime']
		Pressure = np.array(sorted(Profile.keys()))
		Temperature = np.array([Profile[x]['Temperature'] for x in sorted(Profile.keys()) ])
		temp_t = Temperature[np.where(Pressure > 0)]
		print "{cycle}, {temp_time}, {meantemp}".format(cycle=cycle,
			temp_time=temp_time, meantemp=np.mean(temp_t))
	except:
		pass