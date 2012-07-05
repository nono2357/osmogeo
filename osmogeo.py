#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python modules
import subprocess, threading, time, re, sys, os, telnetlib, socket, webbrowser, sqlite3, os

try:
	os.remove('test.db')
except OSError:
	pass

# Home-made modules
from utils import load_codes, imsi2mccmnc, to_int
from gmm2b import init_geoloc, geoloc

# threads
from layer1 import Layer1
from layer23 import Layer23
from osmocontroller import OsmoController
from trafficmonitor import TrafficMonitor

def main():
	init_geoloc()
	try:
		load_codes()
		#sys.exit(0)
		l1 = Layer1()
		l1.start()
		l23 = Layer23()
		l23.start()
		tm = TrafficMonitor()
		tm.start()
		oc = OsmoController()
		oc.start()
		while True:		
			time.sleep(1)
	except (KeyboardInterrupt, SystemExit):
		l1.tocontinue=False
		l23.tocontinue=False
		tm.tocontinue=False
		oc.tocontinue=False

if __name__ == '__main__':
	main()

