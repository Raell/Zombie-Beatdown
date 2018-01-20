#!/usr/bin/env python
import sys
import multiprocessing.managers
import os, shutil, re, urllib
from mongo import retrieve_config, getIP

# Retrieves config from mongodb
try:
	config = retrieve_config()
	server = config['server']['server_ip']
	port = int(config['server']['report_port'])
	password = config['server']['password']
	dest_folder = config['server']['analysis_folder']
	source_folder = "../storage/analyses"
	path = os.path.dirname(os.path.abspath(__file__))
except:
	port = 2210

class RemoteManager(multiprocessing.managers.BaseManager):
    pass
	
RemoteManager.register("writeFile")
RemoteManager.register("createFolder")
RemoteManager.register("checkPathExists")

# Writes file to remote server
def writeRemoteFile(mgr, srcpath, destpath):
	try:
		fh = open(srcpath, "rb")
		contents = fh.read()
		mgr.writeFile(destpath, contents)
	except:
		print "ReportClient: Failed to open %s" % srcpath
	finally:
		if fh is not None:
			fh.close()
		
	
# Copies over analysis report to server
def sendAnalysis(tid, url):
	mgr = RemoteManager(address=(server, port), authkey=password)
	mgr.connect()
	
	fdirname = urllib.quote_plus(url)
	if (len(fdirname) > 250):
		fdirname = fdirname[:247]		
	first_char = re.sub(r"(http://|https://)?(www.)?", "", url)[:1]
	second_char = re.sub(r"(http://|https://)?(www.)?", "", url)[1:3]
	
	destpath = dest_folder + os.sep + getIP() + os.sep + first_char + os.sep + second_char + os.sep + fdirname
	
	if str(mgr.checkPathExists(destpath)) == "1":
		
		no = 0
		while True:
			ext = "(%d)" % no
			if str(mgr.checkPathExists(destpath + ext)) == "0":
				destpath += ext
				break
			no += 1
	
	srcpath = source_folder + os.sep + str(tid)
	processDirectory(mgr, srcpath, destpath)
	shutil.rmtree(srcpath)

# Writes files and folders to server
def processDirectory(mgr, srcpath, destpath):
	mgr.createFolder(destpath)
	for root, dirs, files in os.walk(srcpath):
		
		for dir in dirs:
			subdir = root.replace(srcpath, destpath) + os.sep + dir
			#print "Folder:", subdir
			mgr.createFolder(subdir)
			
		for file in files:
			srcfilepath = root + os.sep + file
			destfilepath = root.replace(srcpath, destpath) + os.sep + file
			#print "File:", destfilepath
			writeRemoteFile(mgr, srcfilepath, destfilepath)
			
	
if __name__ == "__main__":
	if len(sys.argv) > 2:
		mgr = RemoteManager(address=(server, port), authkey=password)
		mgr.connect()
		if sys.argv[1] == "-f":
			processDirectory(mgr, sys.argv[2], sys.argv[3])
		else:	
			writeRemoteFile(mgr, sys.argv[1], sys.argv[2])
	else:
		print "usage: python " + sys.argv[0] + " [-f] <local_file_name> <remote_file_name>"