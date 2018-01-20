# Created by: Micah Cinco
# Version 1. October 2014

from pymongo import MongoClient
import socket

MONGO_URL = 'mongodb://ZB_Admin:cuck00@130.195.4.93:45151/ZombieBeatdown'

client = MongoClient(MONGO_URL)
db = client.ZombieBeatdown
collection = db.evaluation

def pull_task():    
	"""Pulls task from MongoHQ DB according to priority and must be in "idle" state.
	@return task"""
	
	if collection.find_one({ "progress":"idle" }) == None:
		return None
	else:
		if collection.find_one({ "progress":"idle", "priority":"High" }) == None:
			if collection.find_one({ "progress":"idle", "priority":"Normal" }) == None:
				for task in collection.find({ "progress":"idle", "priority":"Low" }):
					collection.update(task , {'$set':{'progress': "inprogress", "assigned_worker": getIP()}}, upsert=False, multi=False)
					return task
			else:
				for task in collection.find({ "progress":"idle", "priority":"Normal" }):
					collection.update(task , {'$set':{'progress': "inprogress", "assigned_worker": getIP()}}, upsert=False, multi=False) 
					return task
		else: 
			for task in collection.find({ "progress":"idle", "priority":"High" }):
				collection.update(task , {'$set':{'progress': "inprogress", "assigned_worker": getIP()}}, upsert=False, multi=False)
				return task      
            
def update_tasklist(task, tid):    
    """Update tasklist of given task."""    
    collection.update({ "_id": task['_id']} , {'$set':{'tid': tid}})
    
def task_done(_id):   
    """Change given task's progress to "completed".""" 
    for task in collection.find({ "_id": _id }):
		collection.update(task , {'$set':{'progress': "completed", 'assigned_worker': ""}}, upsert=False, multi=False)

def retrieve_config():
	"""Retrieves config file from database."""
	client = MongoClient(MONGO_URL)
	db = client.ZombieBeatdown
	collection = db.config
	return collection.find_one()

def getIP():
	"""Gets current machine IP."""
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 80))
	ip = s.getsockname()[0]
	s.close()
	return ip