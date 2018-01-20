#!/usr/bin/env python
# Created by: Micah Cinco
# Version 1. October 2014

from bson import json_util
import json, time
import mongo, taskhandler, cuckoo, os, sys
from lib.cuckoo.common.colors import bold, green, red, yellow
from heartbeat import setHeartbeat
from transferclient import sendAnalysis
from threading import Thread
taskid = dict()
				
def start_worker():
	"""Pull a task from MongoHQ DB and 
	add URLs for processing queue in Cuckoo db.
	@return task_id"""

	task = mongo.pull_task()
	if task != None:
		global taskid 
		# Places in a dictionary url to corresponding cuckoo taskid
		taskid[task['_id']] = [task['url'], taskhandler.add_urls(task)]
		return True
	else:
		print(bold(red("Error")) + ": no tasks in 'idle' state to pull") 
		time.sleep(30)
		return False

# Thread that automatically checks for completed tasks and removes them from database
class StatusCheck(Thread):

	def __init__(self):
		Thread.__init__(self)
		global taskid
	
	def run(self):
		while True:
			if taskid:
				for mongoid, task in taskid.items():
					if taskhandler.task_done(task[1]):
						print (bold(green("Completed")) + ": Task %d") % task[1]
						mongo.task_done(mongoid)
						sendAnalysis(task[1], task[0])
						taskid.pop(mongoid, None)

			time.sleep(1)

# Initialize cuckoo and ZB
def initialize():
	taskhandler.delete_all()
	setHeartbeat()		
	check = StatusCheck()
	check.daemon = True
	check.start()
			
if __name__ == '__main__':
	try:
		initialize()
		
		while True:	
			free = taskhandler.check_machines()
			if free and not taskhandler.check_pending_tasks():
				start_worker()	
				while taskhandler.check_machines() >= free:
					pass
				
	except KeyboardInterrupt:
		exit
	
