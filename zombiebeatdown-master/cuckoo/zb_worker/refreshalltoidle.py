#!/usr/bin/env python
# Created by: Micah Cinco
# Version 1. October 2014

import os, pymongo
from pymongo import MongoClient

MONGO_URL = 'mongodb://ZB_Admin:cuck00@130.195.4.93:45151/ZombieBeatdown'

def refresh_tasks():
    """Reset all tasks in the database to progress state == "idle"."""  
    client = MongoClient(MONGO_URL)
    db = client.ZombieBeatdown
    collection = db.evaluation
    
    for task in collection.find():
        collection.update(({ "progress": "completed" }) , {'$set':{'progress': "idle", 'tid_list': []}}, upsert=False, multi=False)
    return 'Successfully refreshed all tasks to idle.'

if __name__ == '__main__':
    print refresh_tasks()
