# Created by: Micah Cinco
# Version 1. October 2014

import json
from datetime import datetime

"""Task object"""
class Task(object):
	# urls = []
	# tid_list = []

    # The class "constructor" 
	def __init__(self, url, timeout, priority):
		self.url = url
		if priority == None:
			self.priority = "Normal"
		else:
			self.priority = priority
		if priority == None:
			self.timeout = "100"
		else:
			self.timeout = timeout
		self.progress = "idle"
		self.tid = 0
		self.date_created = str(datetime.now())
		self.assigned_worker = ""
        
	def printTask(self):
		"""Returns the Task in JSON format as a string.
		@return task.__dict__"""
		return json.dumps(self.__dict__)
		
class Config(object):

    # The class "constructor" 
	def __init__(self, server, workers, heartbeat, alert):
		self.server = server
		self.workers = workers
		self.heartbeat = heartbeat
		self.alert = alert

        
	def printTask(self):
		"""Returns the Task in JSON format as a string.
		@return task.__dict__"""
		return json.dumps(self.__dict__)