#!/usr/bin/python
# -*- coding: utf-8 -*-
# TrafficMonitor

import threading, re, subprocess, time, sqlite3

from utils import imsi2mccmnc

class TrafficMonitor(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon=True
		self.tocontinue=True
		self.reimsi = re.compile(r'IMSI \(([0-9]{10,})\)')
		self.reepoch = re.compile(r'Epoch Time: ([0-9\.]+) seconds')
		self.rearfcn = re.compile(r'GSM TAP Header, ARFCN: ([0-9]+) \((.*?)\)')
		self.reimmediate = re.compile(r'Single channel : ARFCN ([0-9]+)')   # tshark -r gsm_radio.pcap -V udp.dstport == 4729 | grep -E "channel : ARFCN |Immediate"
	
	def run(self):
		print "Launching TrafficMonitor..."
		# DB
		self.dbcon = sqlite3.connect('test.db')
		self.dbcon.isolation_level = None
		self.mydbcur = self.dbcon.cursor()
		framecontent=""
		p = subprocess.Popen("tshark -i lo -V udp and dst port 4729".split(" "), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p.stdin.close()
		l = p.stdout.readline()
		while l!=None and self.tocontinue:
			if l=="\n":
				#print "***",framecontent
				self.handleFrame(framecontent)
				framecontent=""
			else:
				framecontent+=l
			l=p.stdout.readline()
		print 'TrafficMonitor finished!'

	def handleFrame(self, fc):
		lr=self.reimsi.findall(fc)
		if lr:
			le=self.reepoch.findall(fc)
			st=time.localtime(float(le[0]))
			arfcn=self.rearfcn.findall(fc)[0]
			for imsi in lr:
				i2m = imsi2mccmnc(imsi)
				print '%s %s' % (time.strftime('[%d/%m/%Y %H:%M:%S]',st),imsi), i2m, arfcn
				#try:
				self.mydbcur.execute('''INSERT INTO imsis VALUES (strftime('%Y-%m-%d %H:%M:%S'),?,?,?,?,?,?)''',(imsi,int(arfcn[0]),i2m[0],i2m[1],i2m[2],i2m[3]))
				#except sqlite3.Error:
				#	pass
			"""
			if len(lr)>2:
				print fc
				self.tocontinue=False
			"""
		self.handleImmediateFrame(fc)

	def handleImmediateFrame(self, fc):
		limm = self.reimmediate.findall(fc)
		if limm:
		  for imm in limm:
		    print "Immediate Paging for Call ARFCN=%s" % imm   # XXX Add here visualization of calls in AJAX
		  return limm
		else:
		  return None


import unittest

exp_imm_fc = """Frame 281: 81 bytes on wire (648 bits), 81 bytes captured (648 bits)
    Arrival Time: May 25, 2012 14:03:45.108181000 CEST
    Epoch Time: 1337947425.108181000 seconds
    [Time delta from previous captured frame: 0.003785000 seconds]
    [Time delta from previous displayed frame: 0.003785000 seconds]
    [Time since reference or first frame: 108.144648000 seconds]
    Frame Number: 281
    Frame Length: 81 bytes (648 bits)
    Capture Length: 81 bytes (648 bits)
    [Frame is marked: False]
    [Frame is ignored: False]
    [Protocols in frame: eth:ip:udp:gsmtap:gsm_a_ccch]
Ethernet II, Src: IntelCor_6f:e6:50 (00:23:14:6f:e6:50), Dst: IPv4mcast_00:00:fb (01:00:5e:00:00:fb)
    Destination: IPv4mcast_00:00:fb (01:00:5e:00:00:fb)
        Address: IPv4mcast_00:00:fb (01:00:5e:00:00:fb)
        .... ...1 .... .... .... .... = IG bit: Group address (multicast/broadcast)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
    Source: IntelCor_6f:e6:50 (00:23:14:6f:e6:50)
        Address: IntelCor_6f:e6:50 (00:23:14:6f:e6:50)
        .... ...0 .... .... .... .... = IG bit: Individual address (unicast)
        .... ..0. .... .... .... .... = LG bit: Globally unique address (factory default)
    Type: IP (0x0800)
Internet Protocol Version 4, Src: 192.168.1.15 (192.168.1.15), Dst: 224.0.0.251 (224.0.0.251)
    Version: 4
    Header length: 20 bytes
    Differentiated Services Field: 0x00 (DSCP 0x00: Default; ECN: 0x00: Not-ECT (Not ECN-Capable Transport))
        0000 00.. = Differentiated Services Codepoint: Default (0x00)
        .... ..00 = Explicit Congestion Notification: Not-ECT (Not ECN-Capable Transport) (0x00)
    Total Length: 67
    Identification: 0x0066 (102)
    Flags: 0x02 (Don't Fragment)
        0... .... = Reserved bit: Not set
        .1.. .... = Don't fragment: Set
        ..0. .... = More fragments: Not set
    Fragment offset: 0
    Time to live: 1
        [Expert Info (Note/Sequence): "Time To Live" != 255 for a packet sent to the Local Network Control Block (see RFC 3171)]
            [Message: "Time To Live" != 255 for a packet sent to the Local Network Control Block (see RFC 3171)]
            [Severity level: Note]
            [Group: Sequence]
    Protocol: UDP (17)
    Header checksum: 0xd691 [correct]
        [Good: True]
        [Bad: False]
    Source: 192.168.1.15 (192.168.1.15)
    Destination: 224.0.0.251 (224.0.0.251)
User Datagram Protocol, Src Port: 48422 (48422), Dst Port: gsmtap (4729)
    Source port: 48422 (48422)
    Destination port: gsmtap (4729)
    Length: 47
    Checksum: 0xa663 [validation disabled]
        [Good Checksum: False]
        [Bad Checksum: False]
GSM TAP Header, ARFCN: 82 (Downlink), TS: 0, Channel: PCH (0)
    Version: 2
    Header length: 16 bytes
    Payload Type: GSM Um (MS<->BTS) (1)
    Time Slot: 0
    ..00 0000 0101 0010 = ARFCN: 82
    .0.. .... .... .... = Uplink: 0
    Signal/Noise Ratio (dB): 206
    Signal Level (dBm): 0
    GSM Frame Number: 2011686
    Channel Type: PCH (5)
    Antenna Number: 0
    Sub-Slot: 0
GSM CCCH - Immediate Assignment
    L2 Pseudo Length
        L2 Pseudo Length
            0010 11.. = L2 Pseudo Length value: 11
    Protocol Discriminator: Radio Resources Management messages
        0000 .... = Skip Indicator: 0
        .... 0110 = Protocol discriminator: Radio Resources Management messages (6)
    Message Type: Immediate Assignment
    Page Mode
        .... ..00 = Page Mode: Normal paging (0)
    Dedicated mode or TBF
        .011 .... = Dedicated mode or TBF: This message assigns a downlink TBF to the mobile station identified in the IA Rest Octets IE (3)
    Packet Channel Description
        Packet Channel Description
            0000 1... = Spare bits (ignored by receiver)
            .... .111 = Timeslot: 7
            101. .... = Training Sequence: 5
            ...0 .... = Hopping channel: No
            .... 10.. = Spare
            Single channel : ARFCN 22
    Request Reference
        Request Reference
            Random Access Information (RA): 0
            1101 0... = T1': 26
            .... .010 001. .... = T3: 17
            ...1 0001 = T2: 17
            [RFN: 34493]
    Timing Advance
        Timing advance value: 0
    Mobile Allocation
        Length: 0
    IA Rest Octets
        IA Rest Octets
            Data(Not decoded)
"""


class TestTrafficMonitor(unittest.TestCase):

    def setUp(self):
        self.tm = TrafficMonitor()

    def test_handle_immediate_frame(self):
        l = self.tm.handleImmediateFrame(exp_imm_fc)
        #print l
        self.assertTrue(len(l) > 0)

if __name__ == '__main__':
  unittest.main()

