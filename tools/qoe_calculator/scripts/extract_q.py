import mysql.connector
import argparse 
import json
from sys import exit

def get_args():
	# Using argparse to obtain the argument

	parser = argparse.ArgumentParser(description="This script extracts from a database\
		the data needed to calculate Quality of Experience indicators 1, 2, 3 and 4\n\
		A configuration file must be provided with the informations needed to \
		connect to a database that contains the metrics stored with the schema \
		provided by the create_cdab_db_stats script.\n\
		Further information can be obtained from the official GitHub repository\
		https://github.com/esa-cdab/cdab-testsuite")

	parser.add_argument(
		"-c", 
		metavar="Config", 
		required=True, 
		help="Specifies \
		the full path to the file containing the database configuration")

	return parser.parse_args()


def open_db(config):
	# Tries to open a connection to the database

	try:
		db = mysql.connector.connect(
		  host=config["host"],
		  user=config["user"],
		  password=config["password"],
		  database=config["database"]
		)
	except mysql.connector.Error as err:
		print("Something went wrong: {}".format(err))
		exit(1)

	return (db.cursor(), db)

def fetch_metric(cursor, metric, test_case, config):
	# standard fetch function, given a metric name retrieves all the values
	# in the database associated with that metric
  testSite_list = str(config["testsite"]).replace('"',"'").replace('[','').replace(']','')
  target = str(config["target"]).replace('"',"'")
  
  query = str("SELECT value FROM Runs WHERE metricId = (SELECT id FROM Metrics WHERE name='{}') and testCaseId in (select id from TestCase where name='{}'and target = '{}' and testSite IN ({}) and startedAt Between '{}' and '{}');").format(str(metric),str(test_case), target,testSite_list, config['startTime'], config['stopTime'])
  cursor.execute(query)
  
  res = [d[0] for d in cursor.fetchall()]
  return res

def fetch_metric_collection(cursor, metric, test_case, config):
	# standard fetch function, given a metric name retrieves all the values
	# in the database associated with that metric
  testSite_list = str(config["testsite"]).replace('"',"'").replace('[','').replace(']','')
  target = str(config["target"]).replace('"',"'")
  
  query = str("SELECT collection FROM Runs WHERE metricId = (SELECT id FROM Metrics WHERE name='{}') and testCaseId in (select id from TestCase where name='{}'and target = '{}' and testSite IN ({}) and startedAt Between '{}' and '{}');").format(str(metric),str(test_case), target,testSite_list, config['startTime'], config['stopTime'])
  cursor.execute(query)
  
  res = [d[0] for d in cursor.fetchall()]
  return res

def q1(cursor, config):
	# Fetches metrics needed to calculate Q1 and save them in a json file
	results = {}
	results["M015"] = fetch_metric(cursor, "catalogueCoverage", "TC501", config)
	results["M023"] = fetch_metric(cursor, "dataCoverage", "TC502", config)
	results["M013"] = fetch_metric(cursor, "avgDataAvailabilityLatency", "TC602", config)
	results["M024"] = fetch_metric(cursor, "dataOfferConsistency", "TC503", config)

	with open("q1_data.json", "w") as output:
		json.dump(results, output)

def q2(cursor, config):
	# Fetches metrics needed to calculate Q2 and save them in a json file
	results = {}
	results["M001"] = fetch_metric(cursor, "avgResponseTime", "TC101", config)
	results["M002"] = fetch_metric(cursor, "peakResponseTime", "TC101", config)
	results["M003"] = fetch_metric(cursor, "errorRate", "TC101", config)
	with open("q2_data.json", "w") as output:
		json.dump(results, output)
	

def q3(cursor, config):
	# Fetches metrics needed to calculate Q3 and save them in a json file
	results = {}
	results["M001"] = []
	results["M002"] = []
	results["M003"] = []
	results["M012"] = []
	for tc in ["TC201", "TC202", "TC203", "TC204", "TC209"]:
		results["M001"].append(fetch_metric(cursor, "avgResponseTime", tc, config))
		results["M002"].append(fetch_metric(cursor, "peakResponseTime", tc, config))
		results["M003"].append(fetch_metric(cursor, "errorRate", tc, config))
	for tc in ["TC201", "TC202", "TC203", "TC204"]:
		results["M012"].append(fetch_metric(cursor, "resultsErrorRate", tc, config))

	with open("q3_data.json", "w") as output:
		json.dump(results, output)

def q4(cursor, config):
	# Fetches metrics needed to calculate Q4 and save them in a json file
	results = {}
	results["M001"] = []
	results["M002"] = []
	results["M003"] = []
	results["M005"] = []

	for tc in ["TC301", "TC302", "TC303",  "TC309"]:
		results["M001"].append(fetch_metric(cursor, "avgResponseTime", tc, config))
		results["M002"].append(fetch_metric(cursor, "peakResponseTime", tc, config))
		results["M003"].append(fetch_metric(cursor, "errorRate", tc, config))
		results["M005"].append(fetch_metric(cursor, "throughput", tc, config))

	results["M017"] = fetch_metric(cursor, "offlineDataAvailabilityLatency", "TC304", config)
	results["M023"] = fetch_metric(cursor, "dataCoverageOnline", "TC804", config)
	results["M016"] = fetch_metric_collection(cursor, "dataCoverageOnline", "TC804", config)
	
	with open("q4_data.json", "w") as output:
		json.dump(results, output)

def main():
	# Retrieves arguments, opens the config file, extracts the metrics
	args = get_args()
	
	with open(args.c) as f:
		config = json.load(f)

	cursor, db = open_db(config)

	if config["q1"]:
			q1(cursor, config)
	if config["q2"]:
			q2(cursor, config)
	if config["q3"]:
			q3(cursor, config)
	if config["q4"]:
			q4(cursor, config)		

	cursor.close()
	db.close()

if __name__ == '__main__':
	main()