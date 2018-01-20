#!/usr/bin/env python
import sys
import multiprocessing.managers
import time, os, ConfigParser
from threading import Thread
from mongo import retrieve_config

# Retrieves config from mongodb
try:
	config = retrieve_config()
	port = int(config['server']['report_port'])
	password = config['server']['password']
except:
	port = 2210
	password = 'ZombieBeatdown'

# Writes files to local system
def writeFile(filename, contents):
	fh = None
	try:
		filename = filename.replace("\\", os.sep).replace("/", os.sep)
		fh = open(filename, "wb")
		fh.write(contents)
	except:
		print "ReportServer: Failed to write %s" % filename
	finally:
		if fh is not None:
			fh.close()

# Creates folder in local system
def createFolder(path):
	path = path.replace("\\", os.sep).replace("/", os.sep)	
	if not os.path.exists(path):
		try:
			os.makedirs(path)
			print "ReportServer: Created folder", path
		except:
			print "ReportServer: Failed to create folder %s" % path

# Checks if path exists
def checkPathExists(path):
	path = path.replace("\\", os.sep).replace("/", os.sep)	
	if os.path.isdir(path):
		return 1
	else:
		return 0

class RemoteManager(multiprocessing.managers.BaseManager):
    pass

RemoteManager.register("writeFile", writeFile)
RemoteManager.register("createFolder", createFolder)
RemoteManager.register("checkPathExists", checkPathExists)

class ReportServer(Thread):

	def __init__(self):
		Thread.__init__(self)
		self.port = port
		self.password = password
	
	def run(self):
		#print "Listening for incoming connections..."
		mgr = RemoteManager(address=('', self.port), authkey=self.password)
		server = mgr.get_server()
		server.serve_forever()

# Initialization for report server
def setReportServer():
	server = ReportServer()
	server.daemon = True
	server.start()
	print "Started transfer server on port", port
		
if __name__ == "__main__":
		
	try:
		
		setReportServer()
		
		while True:
			time.sleep(1)
			
	except KeyboardInterrupt:
		exit

