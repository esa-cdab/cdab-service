import argparse 
from os import listdir
from os.path import isfile, join
import mysql.connector
import json
from sys import exit

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

	parser.add_argument(
		"-t", 
		metavar="TestSite",  
		help="The test site where the test was performed, if not specified it \
		will be retrieved from the json parameter \"testSite\"")

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

def update_db(cursor, input_dir, testSite=None):
	# First get the name of all the json files in the directory, then open one by one and parse + update db. 
	# Returns 1 if everything was correctly executed, in case of error returns 0

	files = [file for file in listdir(input_dir) if isfile(join(input_dir, file)) and file.endswith(".json")]
	for filename in files:
		with open(input_dir + "/" + filename) as f:
			data = json.load(f)

		if testSite is None:
			try:
				testSite = data["testSite"]
			except KeyError:
				print("File {} is missing testSite parameter, please import\
					it again specifing it".format(filename))
				continue

		try:
			target = data["testTarget"]		
			
			for test_case in data["testCaseResults"]:
				test_name = test_case["testName"]
				started_at = test_case["startedAt"]
				
				cursor.execute("INSERT INTO TestCase (name, target, startedAt, testSite) \
					VALUES (%s, %s, %s, %s)", (test_name, target, started_at, testSite))
				
				test_id = cursor.lastrowid

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
							(metricId, testcaseId, value) VALUES \
							(%s, %s, %s)", 
							(metric_id, test_id, metric["value"]))

					elif metric["uom"] != "string":
						cursor.execute("SELECT id FROM Metrics WHERE name=%s", (metric["name"],))
						try:
							metric_id = cursor.fetchone()[0]
						except TypeError:
							print("Metric {} is not currently supported in the database".format(metric["name"]))
							continue

						query = "INSERT IGNORE INTO Runs (metricId, testcaseId, value) VALUES "
						for val in metric["value"]:
							query += "(" + str(metric_id) + "," + str(test_id)  + "," + str(val) + "),"
						
						query = query[:-1]
						cursor.execute(query, ())

		except KeyError:
			print("Seems you provided a wrongly formatted file, check {} and try again please".format(filename))
			return 0
	return 1

def main():

	args = get_args()
	cursor, db = open_db(args.c)
	result = update_db(cursor, args.i, args.t)
	if result:
		db.commit()
	cursor.close()
	db.close()


if __name__ == '__main__':
	main()