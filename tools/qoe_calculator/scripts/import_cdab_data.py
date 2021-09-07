import argparse 
from os import listdir
from os.path import isfile, join
import mysql.connector
import json
from sys import exit
import glob
from datetime import datetime

def get_args():
	# Using argparse to obtain the arguments, both marked as required

	parser = argparse.ArgumentParser(description="This script is responsible\
	 for populating a database with results \
		produced by ESA's cdab benchmarking suite.\n\
		Further information can be obtained from the official GitHub repository \
		https://github.com/esa-cdab/cdab-testsuite")

	parser.add_argument(
		"-i", 
		metavar="Input", 
		required=True, 
		help="Specifies the full path to the directory containing json results")

	parser.add_argument(
		"-c", 
		metavar="Config", 
		required=True, 
		help="Specifies the full path to the file containing \
		the database configuration")

	return parser.parse_args()


def open_db(config):
	# Retrieves data from the config file and opens a connection

	with open(config) as f:
		data = json.load(f)
	try:
		db = mysql.connector.connect(
		  host=data["host"],
		  user=data["user"],
		  password=data["password"],
		  database=data["database"]
		)
	except mysql.connector.Error as err:
		print("Something went wrong: {}".format(err))
		exit(1)

	return (db.cursor(), db)

def update_db(cursor, input_dir):
	# First get the name of all the json files in the directory, then open one by one and parse + update db. 
	# Returns 1 if everything was correctly executed, in case of error returns 0
  
	files = glob.glob(input_dir+ '/**/*.json', recursive=True)
  
	for filename in files:
	  with open(filename) as f:
	    data = json.load(f)
	  
	  try:
	    target = data["testTarget"]
	    test_site = data["testSite"]
	    test_scenario = data["testScenario"]
 						
	    for test_case in data["testCaseResults"]:
	      test_name = test_case["testName"]
	      started_at = test_case["startedAt"].replace('Z','')
	      insert_query = "INSERT INTO TestCase (testScenario, name, target, testSite, startedAt) VALUES ('{}', '{}', '{}', '{}', DATE_FORMAT('{}','%Y-%m-%dT%l:%i:%s'))".format(test_scenario, test_name, target, test_site, started_at)
	      cursor.execute(insert_query)
 				
	      test_id = cursor.lastrowid
	      collection = ["NULL"]
	      for metric in test_case["metrics"]:
	        if metric["name"] == "dataCoverageOnline":
	           for lst_metric in test_case["metrics"]:
	              if lst_metric["name"] == "dataCollectionDivision":
	                 collection = lst_metric["value"]
 				                            
	      for metric in test_case["metrics"]:				  
	         if not isinstance(metric["value"], list):
	           cursor.execute("SELECT id FROM Metrics WHERE name=%s", (metric["name"],))
 						
	           try:
	              metric_id = cursor.fetchone()[0]
	           except TypeError:
	              print("Metric {} is not currently supported in the database".format(metric["name"]))
	              continue
             
	           cursor.execute(
 							"INSERT IGNORE INTO Runs \
 							(metricId, testcaseId, value, collection) VALUES \
 							(%s, %s, %s, %s)", 
 							(metric_id, test_id, metric["value"], ""))
 
	         elif metric["uom"] != "string":
	           cursor.execute("SELECT id FROM Metrics WHERE name=%s", (metric["name"],))
	           try:
	              metric_id = cursor.fetchone()[0]
	           except TypeError:
	              print("Metric {} is not currently supported in the database".format(metric["name"]))
	              continue
 
	           query = "INSERT IGNORE INTO Runs (metricId, testcaseId, value, collection) VALUES "
	           i = 0
	           if collection  != ["NULL"]:
	             for val in metric["value"]:
	                 query += "(" + str(metric_id) + "," + str(test_id)  + "," + str(val) + ",'" + str(collection[i]) +"'),"
	                 i+=1				    
	           else:
	              for val in metric["value"]:
	                 query += "(" + str(metric_id) + "," + str(test_id)  + "," + str(val) + "," + str(collection[0]) +"),"
	              
	           query = query[:-1]
	           cursor.execute(query, ())
 
	  except KeyError:
 			 print("Seems you provided a wrongly formatted file, check {} and try again please".format(filename))
 			 return 0
	return 1

def main():

	args = get_args()
	cursor, db = open_db(args.c)
	result = update_db(cursor, args.i)
	if result:
		db.commit()
	cursor.close()
	db.close()


if __name__ == '__main__':
	main()