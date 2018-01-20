#!/usr/bin/env python
# Copyright (C) 2010-2014 Cuckoo Sandbox Developers.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.
# Edited by Micah Cinco - October 2014

import mongo
import os, sys, shutil
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

from lib.cuckoo.common.colors import bold, green, red
from lib.cuckoo.core.database import Database, TASK_PENDING, TASK_RUNNING, Task
from lib.cuckoo.core.database import TASK_COMPLETED, TASK_RECOVERED
from lib.cuckoo.core.database import TASK_REPORTED, TASK_FAILED_ANALYSIS
from lib.cuckoo.core.database import TASK_FAILED_PROCESSING, TASK_PENDING
task = 0

# Adds url to cuckoo queue
def add_urls(task):  
    
	url = task['url']
	db = Database()

	task_id = db.add_url(url, timeout=task['timeout'], priority=task['priority'])

	if task_id:
		print(bold(green("Success")) + u": URL \"{0}\" added as task with ID {1}".format(url, task_id))
		mongo.update_tasklist(task, task_id)
		return task_id
	else:
		print(bold(red("Error")) + ": adding task to database")

# Returns number of available VMs for analysis		
def check_machines():
	db = Database()
	return db.count_machines_available()
	
# Returns number of tasks pending for VMs
def check_pending_tasks():
	db = Database()
	return len(db.list_tasks(status=TASK_PENDING))
 
def delete_all():  
    """Delete ALL tasks in Cuckoo's local processing queue and clears any existing analysis files"""
    
    db = Database()
    list = db.list_tasks()
    
    if not list:
        print(bold(red("Error")) + ": no tasks to be deleted")
    else: 
        for url in list:
            db.delete_task(db.count_tasks())
			
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "storage", "analyses")
	for root, dirs, files in os.walk(path):
		for f in files:
			os.unlink(os.path.join(root, f))
		for d in dirs:			
			if os.path.islink(os.path.join(root, d)):
				os.unlink(os.path.join(root, d))		
			else:
				shutil.rmtree(os.path.join(root, d))

# Returns true is all tasks are completed
def task_done(tid):
	
	db = Database()
	if (db.get_status(status=TASK_REPORTED, tid=tid)):
		return True
	else:
		return False
       
if __name__ == '__main__':
    delete_all()
