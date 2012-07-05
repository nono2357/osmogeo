#!/usr/bin/python
# -*- coding: utf-8 -*-
# Layer23

import threading, subprocess, os

from config import *

class Layer23(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon=True
		self.tocontinue=True

	def run(self):
		print "Launching Layer23..."
		# 224.0.0.251 for broadcast
		p = subprocess.Popen([os.path.join(INSTALL_PATH,'osmocom-bb/src/host/layer23/src/mobile/mobile'),'-i','127.0.0.1'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p.stdin.close()
		l = p.stderr.readline()
		while l!=None and self.tocontinue:
			#print l
			l=p.stderr.readline()
		print 'Layer23 finished!'
