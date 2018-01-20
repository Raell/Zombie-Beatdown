#!/usr/bin/env python
# Created by: Micah Cinco
# Version 1. October 2014

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import cgi, json, mongo, pprint, re, os, time
from heartbeatserver import setHeartbeatServer, getHeartbeat
from transferserver import setReportServer
from task import Task, Config
from bson.json_util import dumps
from mongo import retrieve_config

rootpath = os.path.dirname(os.path.abspath(__file__))

# Loads config from mongodb
try:
	config = retrieve_config()
	PORT_NUMBER = int(config['server']['http_port'])
except:
	PORT_NUMBER = 8080

class myHandler(BaseHTTPRequestHandler):
	"""Handles all GET and POST requests from
		the browser."""
	
	def get_file(self, file, mimetype):
		self.send_response(200)
		self.send_header('Content-type', mimetype)
		self.end_headers()
		self.wfile.write(file)
		global rootpath
	
	# Handler for the GET requests
	def do_GET(self):
		if self.path == "/":
			self.path = "/index.html"

		try:
			# Check the file exists
			sendReply = False
			if self.path.endswith(".html"):
				mimetype = 'text/html'
				sendReply = True
			
			elif self.path.endswith(".png"):
				mimetype = "image/png"
				sendReply = True
				
			elif self.path.endswith(".json"):
				
				mimetype = "application/json"
				file = None
				if self.path == "/config.json":
					file = dumps(mongo.retrieve_config())
				elif self.path == "/heartbeat.json":
					file = getHeartbeat()
				
				self.get_file(file, mimetype)

			if sendReply == True:
				# Open the static file requested and send it
				f = open(rootpath + sep + self.path, 'rb') 
				self.get_file(f.read(), mimetype)
				f.close()
			return
		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

	# Handler for the POST requests
	def do_POST(self):
		# Sets config 
		if self.path == "/config":
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			
			server = dict()
			workers = dict()
			heartbeat = dict()
			alert = dict()
			
			server["server_ip"] = form.getvalue("server_ip")
			server["http_port"] = form.getvalue("http_port")
			server["heartbeat_port"] = form.getvalue("heartbeat_port")
			server["analysis_folder"] = form.getvalue("analysis_folder")
			server["report_port"] = form.getvalue("report_port")
			server["password"] = form.getvalue("password")
			
			workers["machines"] = [x.strip() for x in re.split(' |,|\n', form.getvalue("machines")) if x.strip()]
			
			heartbeat["period"] = form.getvalue("period")
			heartbeat["timeout"] = form.getvalue("timeout")
			
			alert["mailing_list"] = form.getvalue("mailing_list")
			
			config = Config(server, workers, heartbeat, alert)
			mongo.set_config(config)
			self.send_response(200)
			self.end_headers()
			self.wfile.write("Config updated successfully.\n")
			
		# Create a Task
		if self.path == "/send":
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})

			data = form.getvalue("urls")
			if data:
				urls = [x.strip() for x in re.split(' |,|\n', data)]
				timeout = form.getvalue("timeout")
				priority = form.getvalue("priority")
				
				obj_id = []
				
				for url in urls:
					if url:
						url = unicode(url, errors="replace")
						t = Task(url, timeout, priority)
						obj_id.append(mongo.push_task(t))
				
				self.send_response(200)
				self.end_headers()
				self.wfile.write("Task(s) pushed to DB successfully.\n")
				self.wfile.write(obj_id)
			return
		
		# Check Tasks
		elif self.path == "/check":
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			
			progress = form.getvalue("progress")
			if progress == None:
				self.wfile.write("No progress selected\n")
				return
			self.send_response(200)
			self.end_headers()
			self.wfile.write(dumps(mongo.check_tasks(progress), indent=2, sort_keys=True))
			self.wfile.write(mongo.print_size(progress))
			return

		# Delete Tasks (by progress or ID)
		elif self.path == "/delete":
			form = cgi.FieldStorage(
				fp=self.rfile,
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			
			progress = form.getvalue("progress")
			if progress == None:
				taskid = form.getvalue("deleteID")
				if taskid == None:
					self.wfile.write("No progress or Task ID entered.\n")
					return
				else:
					self.wfile.write(mongo.delete_task(taskid))
					return
			
			else:
				if mongo.get_progress_size(progress) == 0:
					self.wfile.write("No tasks to delete in selected progress state.\n")
					return
				else:
					self.wfile.write("Successfully deleted tasks.\n")
					self.wfile.write(mongo.delete_progress(progress))
					return
		
try:
	# Create a web server and define the handler to manage the
	# incoming request
	server = HTTPServer(('', PORT_NUMBER), myHandler)
	print 'Started httpserver on port' , PORT_NUMBER
	# Starts heartbeat and report servers
	setHeartbeatServer()
	setReportServer()
	# Wait forever for incoming http requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()