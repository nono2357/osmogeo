#!/usr/bin/python
# -*- coding: utf-8 -*-
# Layer1

import threading, subprocess, os

from config import *

class Layer1(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon=True
		self.tocontinue=True
		self.flashed=False

	def run(self):
		print "Launching Layer1..."
		p = subprocess.Popen([os.path.join(INSTALL_PATH,'osmocom-bb/src/host/osmocon/osmocon'),'-p','/dev/ttyUSB0','-m','c123xor',os.path.join(INSTALL_PATH,'osmocom-bb/src/target/firmware/board/compal_e88/layer1.compalram.bin')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p.stdin.close()
		l = p.stdout.readline()
		while l!=None and self.tocontinue:
			#print l,
			if 'OSMOCOM Layer 1' in l: self.flashed=True
			l=p.stdout.readline()
		print 'Layer1 finished!'

