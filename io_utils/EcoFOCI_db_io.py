#!/usr/bin/env python

"""
 Background:
 --------
 EcoFOCI_db_io.py
 
 
 Purpose:
 --------
 Various Routines and Classes to interface with the mysql database that houses EcoFOCI meta data
 
 History:
 --------


"""

import pymysql
import ConfigParserLocal 
import datetime

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2014, 01, 29)
__modified__ = datetime.datetime(2016, 8, 10)
__version__  = "0.1.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header'

class EcoFOCI_db_ALAMO(object):
	"""Class definitions to access EcoFOCI Mooring Database"""

	def connect_to_DB(self, db_config_file=None):
		"""Try to establish database connection

		Parameters
		----------
		db_config_file : str
			full path to json formatted database config file    

		"""
		self.db_config = ConfigParserLocal.get_config(db_config_file)
		try:
			self.db = pymysql.connect(self.db_config['host'], 
									  self.db_config['user'],
									  self.db_config['password'], 
									  self.db_config['database'], 
									  self.db_config['port'])
		except:
			print "db error"
			
		# prepare a cursor object using cursor() method
		self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
		return(self.db,self.cursor)

	def manual_connect_to_DB(self, host='localhost', user='viewer', 
							 password=None, database='ecofoci', port=3306):
		"""Try to establish database connection

		Parameters
		----------
		host : str
			ip or domain name of host
		user : str
			account user
		password : str
			account password
		database : str
			database name to connect to
		port : int
			database port

		"""	    
		self.db_config['host'] = host
		self.db_config['user'] = user
		self.db_config['password'] = password
		self.db_config['database'] = database
		self.db_config['port'] = port

		try:
			self.db = pymysql.connect(self.db_config['host'], 
									  self.db_config['user'],
									  self.db_config['password'], 
									  self.db_config['database'], 
									  self.db_config['port'])
		except:
			print "db error"
			
		# prepare a cursor object using cursor() method
		self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
		return(self.db,self.cursor)

	def read_profile(self, table=None, CycleNumber=None, verbose=False):
		
		sql = ("SELECT * from `{0}` WHERE `CycleNumber`= '{1}' ORDER BY `id` DESC ").format(table, CycleNumber)

		if verbose:
			print sql

		result_dic = {}
		try:
			# Execute the SQL command
			self.cursor.execute(sql)
			# Get column names
			rowid = {}
			counter = 0
			for i in self.cursor.description:
				rowid[i[0]] = counter
				counter = counter +1 
			#print rowid
			# Fetch all the rows in a list of lists.
			results = self.cursor.fetchall()
			for row in results:
				result_dic[row['Pressure']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
			return (result_dic)
		except:
			print "Error: unable to fetch data"

	def count(self, table=None, start=None, end=None, verbose=False):
		sql = ("SELECT count(*) FROM (SELECT * FROM `{table}` where `CycleNumber` between"
			   " {start} and {end} group by `CycleNumber`) as temp").format(table=table, start=start, end=end)

		if verbose:
			print sql	

		try:
			# Execute the SQL command
			self.cursor.execute(sql)
			# Get column names
			rowid = {}
			counter = 0
			for i in self.cursor.description:
				rowid[i[0]] = counter
				counter = counter +1 
			#print rowid
			# Fetch all the rows in a list of lists.
			results = self.cursor.fetchall()
			return results[0]['count(*)']
		except:
			print "Error: unable to fetch data"
	def close(self):
		"""close database"""
		self.db.close()

