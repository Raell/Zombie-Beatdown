#!/usr/bin/env python
import socket, time, os
from threading import Thread
from mongo import retrieve_config

# Retrieves config from mongodb
try:
	config = retrieve_config()
	DEST_IP = config['server']['server_ip']
	DEST_PORT = int(config['server']['heartbeat_port'])
	PERIOD = int(config['heartbeat']['period'])
except:
	DEST_PORT = 15196
	PERIOD = 5

# Thread that sends regular heartbeats
class Heartbeat(Thread):
	
	def __init__(self):
		Thread.__init__(self)
	
	def run(self):
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		while True:
			#print "Sending heartbeat to %s on %d." % (DEST_IP, DEST_PORT)	
			sock.sendto("Heartbeat", (DEST_IP, DEST_PORT))
			time.sleep(PERIOD)

# Initialize heartbeats
def setHeartbeat():
	heartbeat = Heartbeat()
	heartbeat.daemon = True
	heartbeat.start()
	print "Sending heartbeat to %s(%d) every %d seconds" %(DEST_IP, DEST_PORT, PERIOD)
				
if __name__ == "__main__":
	try:
	
		setHeartbeat()	
		
		while True:
			time.sleep(1)
		
	except KeyboardInterrupt:
			exit
	