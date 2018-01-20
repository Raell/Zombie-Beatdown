#!/usr/bin/env python
import socket, time, json, os, smtplib
from threading import Thread
from datetime import datetime, timedelta
from mongo import reallocate_task, retrieve_config, check_tasks
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Retrieve config from mongodb
try:
	config = retrieve_config()
	MACHINES = config['workers']['machines']
	DEST_PORT = int(config['server']['heartbeat_port'])
	PERIOD = int(config['heartbeat']['period'])
	TIMEOUT = int(config['heartbeat']['timeout'])
	RECIPIENTS = config['alert']['mailing_list']
except:
	MACHINES = []
	DEST_PORT = 15196
	PERIOD = 5
	TIMEOUT = 5

# Thread that listens for heartbeats
class SocketListener(Thread):
	
	check = None
	 
	def __init__(self, check):
		Thread.__init__(self)
		self.check = check
		
	def run(self):
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((getIP(), DEST_PORT))

		while True:
			data, addr = sock.recvfrom(1024)
			self.check.processHeartbeat(addr[0], data)
	

class HeartbeatCheck():

	def __init__(self):
		self.heartbeats = dict()
		for addr in MACHINES:
			self.heartbeats[addr] = datetime.min
		
	# Records time and source of heartbeat
	def processHeartbeat(self, addr, data):
		if(data == "Heartbeat") and (addr in MACHINES):
			self.heartbeats[addr] = datetime.now()
			print "HeartbeatServer: Received heartbeat from %s at %s" %(addr, str(self.heartbeats[addr]))
	
	# Checks heartbeats status and dumps results to JSON
	def checkHeartbeat(self):
		
		log = dict()
		machines = list()
		
		for addr, data in self.heartbeats.iteritems():
			currtime = datetime.now()
			details = dict()
			details["ip"] = addr
			details["lastresponse"] = str(data)
			details["currenttime"] = str(currtime)
			
			if currtime > data + timedelta(seconds=PERIOD*TIMEOUT):				
				details["status"] = "Down"
				reallocate_task(addr)				
				
			elif currtime > data + timedelta(seconds=PERIOD):
				details["status"] = "Warning"
				
			else:
				details["status"] = "Okay"
			
			machines.append(details)
			
		log["machines"] = machines
		
		return json.dumps(log)

# Email alert if task in progress is not completed after 1 hour
# Temporary alert for VM hanging problem
class CheckTasks(Thread):
	
	def run(self):
		while True:
			self.checkTasks()
			time.sleep(3600)
			
	def checkTasks(self):
		tasks = check_tasks("inprogress")
		if tasks and RECIPIENTS:
			for task in tasks:
				now = datetime.now()
				started = datetime.strptime(task["date_created"], "%Y-%m-%d %H:%M:%S.%f")
				if now > started + timedelta(hours=1):
					sender = 'zombiebeatdown.alert@gmail.com'
					
					msg = MIMEMultipart('alternative')
					msg['Subject'] = "ZombieBeatdown Task Alert"
					msg['From'] = sender
					msg['To'] = sender
					
					html = """<h3><u>ZombieBeatdown Task Alert</u></h3>
					<p>The task <b>%s</b> is still uncompleted as of %s.</p>
					<p><u><b>Details</b></u></p>
					<p>URL: %s</p>
					<p>Assigned: %s</p>
					<p>Started: %s</p>
					""" % (task['_id'], str(now.strftime("%Y-%m-%d %H:%M:%S")), task['url'], task['assigned_worker'], datetime.strptime(task['date_created'], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"))
					
					part = MIMEText(html, 'html')
					msg.attach(part)
					
					user = 'zombiebeatdown.alert'
					password = 'zombiebeatdowncuck00'

					try:
						smtp = smtplib.SMTP('smtp.gmail.com:587')
						smtp.starttls()
						smtp.login(user, password)
						smtp.sendmail(sender, RECIPIENTS, msg.as_string())
						smtp.quit()
						print "HeartbeatServer: Sent alert email"
					except:
						print "HeartbeatServer: Unable to send mail"

# Returns heartbeat results						
def getHeartbeat():	
	return check.checkHeartbeat()
	
# Initialization of heartbeat server
def setHeartbeatServer():
	listener = SocketListener(check)
	listener.daemon = True
	listener.start()
	taskcheck = CheckTasks()
	taskcheck.daemon = True
	taskcheck.start()
	print "Started heartbeat server on port", DEST_PORT
	
# Returns current machine IP
def getIP():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 80))
	ip = s.getsockname()[0]
	s.close()
	return ip

check = HeartbeatCheck()
	
if __name__ == "__main__":	
	
	try:
		
		setHeartbeatServer()
		
		while True:
			time.sleep(1)
			
	except KeyboardInterrupt:
		exit
		
