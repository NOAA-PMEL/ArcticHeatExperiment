#!/usr/bin/env python

"""
ArcticHeatAirCraft2JSON.py

Takes aircraft data and parses it

 2016-06-07 - added altitude to output for csv and time
"""

#System Stack
import datetime
import argparse
import csv

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 05, 22)
__modified__ = datetime.datetime(2014, 05, 22)
__version__  = "0.1.1"
__status__   = "Development"
__keywords__ = 'arctic heat','ctd','FOCI', 'wood', 'kevin'


"""----------------------------- Main -------------------------------------"""

parser = argparse.ArgumentParser(description='ArcticHeat datafile parser ')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument('-r','--rows', action="store_true", 
	help='organize by entries')
parser.add_argument('-a','--all', action="store_true", 
	help='output all columns')
parser.add_argument('-k','--keys', action="store_true", 
	help='output column names')
parser.add_argument('-geojson','--geojson', action="store_true", 
	help='output basic location')
parser.add_argument('-kn','--key_names', nargs='+', type=str, 
	help='output from selected column names seperate names by spaces')
parser.add_argument('-p','--pandas', action="store_true",
	help='ingest data via pandas')
parser.add_argument('-csv','--csv', action="store_true",
	help='export data to csv')

args = parser.parse_args()

if not args.rows:
	with open(args.DataPath) as csvfile:
		reader = csv.DictReader(csvfile)

		result = {}
		for row in reader:
		    for column, value in row.iteritems():
		        result.setdefault(column, []).append(value)
else:
	with open(args.DataPath) as csvfile:
		reader = csv.DictReader(csvfile)

		count = 0
		result = {}
		for row in reader:
			result[count] = {}
			for column, value in row.iteritems():
				result[count].update({column: value})
			count +=1

if args.all:

	for k in result.keys():
		print "{0}, {1}".format(k, result[k])


if args.keys:
	if args.rows:
		print result[0].keys()
	else:
		for k in result.keys():
			print k

if args.key_names:
	if args.rows:
		for j in result.keys():
			for k in result[j].keys():
				if k in args.key_names:
					print "{0}, {1}".format(k, result[j][k])
	else:
		for k in result.keys():
				if k in args.key_names:
					print "{0}, {1}".format(k, result[k])

if args.geojson:
	output_params = ['LON','LAT']

   	geo_json_head = '''{
  "type": "FeatureCollection",
  "features": ['''

	geo_json_tail = ''']\n}'''

  	print geo_json_head
	if args.rows:
		for j in result.keys():
			lat = result[j]['LAT']
			lon = result[j]['LON']
			geo_json = ''' {{"type": "Feature","properties": {{}},"geometry": {{"type": "Point","coordinates": [{1},{0}] }}}}, '''.format(lat,lon)
			print geo_json
	else:
		for k in result.keys():
				if k in output_params:
   					print "{1}".format(result[k])
   	#duplicate the last point
   	print ''' {{"type": "Feature","properties": {{}},"geometry": {{"type": "Point","coordinates": [{1},{0}] }}}} '''.format(lat,lon)
   	print geo_json_tail

if args.pandas:
	import pandas as pd

	data = pd.read_csv(args.DataPath)

if args.csv:

	if args.rows:
		for j in result.keys():
			try:
				time_temp = (datetime.datetime.strptime(result[j]['TIME'], '%Y%m%dT%H%M%S')).strftime('%Y-%m-%d %H:%M:%S')
				geo_json = '''{0},{1},{2},{3},{4},{5},{6} '''.format(time_temp,result[j]['LON'],result[j]['LAT'],result[j]['ALTGPS'],result[j]['SST'],result[j]['PYRAUCLEAR'],result[j]['ROLL'])
				print geo_json
			except KeyError:
				print result[j]
