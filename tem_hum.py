#!/usr/bin/env python
 
import os
import xively
import subprocess
import time
import datetime
import requests
import re
import sys
 
# extract feed_id and api_key from environment variables
FEED_ID = os.environ["FEED_ID"]
API_KEY = os.environ["API_KEY"]
DEBUG = os.environ["DEBUG"] or false
 
# initialize api client
api = xively.XivelyAPIClient(API_KEY)
 
def read_temp():  
	while(True):
	# Run the DHT program to get the humidity and temperature readings!

		output = subprocess.check_output(["sudo", "/home/pi/Adafruit-Raspberry-Pi-Python-Code/Adafruit_DHT_Driver/Adafruit_DHT", "2302", "4"]);
		print output
		matches = re.search("Temp =\s+([0-9.]+)", output)
		if (not matches):
			time.sleep(3)
			continue
		temp = float(matches.group(1))
  
		# search for humidity printout
		matches = re.search("Hum =\s+([0-9.]+)", output)
		if (not matches):
			time.sleep(3)
			continue
		humidity = float(matches.group(1))

		print "Temperature: %.1f C" % temp
		print "Humidity:    %.1f %%" % humidity
		return temp, humidity

 
# function to return a datastream object. This either creates a new datastream,
# or returns an existing one

def get_datastream(feed, channel, tag):
	try:
		datastream = feed.datastreams.get(channel)
		if DEBUG:
			print "Found existing datastream"
		return datastream
	except:
		if DEBUG:
			print "Creating new datastream"
		datastream = feed.datastreams.create(channel, tags=tag)
		return datastream
 
# main program entry point - runs continuously updating our datastream with the
# current 1 minute load average
def run():
	print "Starting Xively tutorial script"
	
	feed = api.feeds.get(FEED_ID)
	#channels = ["temp"]
	tempStream = get_datastream(feed, "temp", "temp_01")
	tempStream.max_value = None
	tempStream.min_value = None
	
	humStream = get_datastream(feed, "hum", "hum_01")
	humStream.max_value = None
	humStream.min_value = None
		
		
	#for channel in channels:
	#	datastream = get_datastream(feed, channel, "temp_01")
	#	datastream.max_value = None
	#	datastream.min_value = None
 
	while True:
		temp, humidity = read_temp()
		print temp
		print humidity
	
	if DEBUG:
		print "Updating Xively feed with value: %s" % temp
		print "Updating Xively feed with value: %s" % humidity
	
	tempStream.current_value = temp
	tempStream.at = datetime.datetime.utcnow()
	
	humStream.current_value = humidity
	humStream.at = datetime.datetime.utcnow()
	try:
		tempStream.update()
		humStream.update()
	except requests.HTTPError as e:
		print "HTTPError({0}): {1}".format(e.errno, e.strerror)
	
	time.sleep(30)
 
run()
