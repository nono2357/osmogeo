#!/usr/bin/python
# -*- coding: utf-8 -*-
# OsmoController

import threading, re, socket, telnetlib, time
from utils import imsi2mccmnc, to_int
from gmm2b import geoloc
from config import *

class OsmoController(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon=True
		self.tocontinue=True
		self.tn = None	
		self.reprompt = re.compile(r'OsmocomBB[\(\)a-z]*?[>#]')
		self.relcells = re.compile(r'^([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)\|([^\|]*)')

	def send(self, lcmd, debug=False):
		output=""
		while True:
			try:
				self.tn = telnetlib.Telnet('localhost',4247)
				#self.tn.set_debuglevel(5)
				self.tn.expect([self.reprompt])
				for cmd in lcmd:
					self.tn.write("%s\r\n" % cmd)
					s=self.tn.expect([self.reprompt])[2]
					if debug: print s
					output=output+s
				self.tn.close()
				break
			except (socket.error, AttributeError):
				time.sleep(1)
				continue
		return output			

	def get_cells(self):
		s=self.send(['show cell 1'])
		lc=[l.split('|') for l in s.split('\n')]				
		lc=[l for l in lc if l.__class__.__name__=='list' and len(l)==10]
		lc=[[to_int(e) for e in l] for l in lc][1:] # Keep only resolved antennas
		lc=[(l[:5],geoloc(*l[1:5])) for l in lc if None not in l[:5]] # Geolocation of antennas
		lc=[(a,b) for a,b in lc if b] # Keep only geolocated antennas
		for a,b in lc:
			arfcn, mcc, mnc, lac, cid = a
			lat, lon = b
			mcc2,mnc2, country, network = imsi2mccmnc("%d%02d000000" % (mcc,mnc))
			try:
				self.mydbcur.execute('''INSERT INTO antennas VALUES (strftime('%Y-%m-%d %H:%M:%S'),?,?,?,?,?,?,?,?,?)''',(arfcn,mcc,mnc,lac,cid,country,network,lat,lon))
			except sqlite3.Error, msg:
				pass
		self.mydbcur.execute('''SELECT COUNT(*) FROM antennas''')
		mb = list(self.mydbcur)[0][0]
		if mb: print mb, "mapped BTS! (open map.html in a browser)"
		fd=open("oldata.txt","w")
		fd.write("lat	lon	title	description	icon	iconSize	iconOffset\n")
		self.mydbcur.execute('''SELECT lat,lon,'ARFCN '||arfcn,mcc||'-'||mnc||'-'||lac||'-'||cid||'<br/>'||network||'<br/>'||country,'imgs/Ol_icon_blue_example.png','24,24','0,-24' FROM antennas''')
		for l in self.mydbcur:
			fd.write('\t'.join([str(e) for e in l]))
			fd.write('\n')
		fd.close()
		return lc

	def make_stats(self):
		pass

	def run(self):
		print "Launching OsmoController..."
		# DB
		self.dbcon = sqlite3.connect('test.db')
		self.dbcon.isolation_level = None
		self.mydbcur = self.dbcon.cursor()
		self.send(['enable','conf t','ms 1','no shutdown','end','end'], False)
		while True:
			self.get_cells()
			self.make_stats()
			time.sleep(10)
