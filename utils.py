#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

reparen = re.compile(r" ?\(.*?\)")

d_mcc = {}
d_mccmnc = {}

def delete_paren(ch):
	return reparen.sub("",ch)

def to_int(ch):
	try:
		ch2=ch.replace('DCS','').strip()
		if ch2.startswith('0x'):
			return int(ch2,16)
		else:
			return int(ch2)
	except ValueError:
		return None

def load_codes():
	global d_mcc, d_mccmnc
	mcc_mnc_file=open('/home/renaud/installations/wireshark/wireshark-1.6.7/epan/dissectors/packet-e212.c').read()
	# MCC
	remcc = re.compile(r'E212_codes\[\] = \{(.*?)\};',re.MULTILINE|re.DOTALL)
	ch=remcc.findall(mcc_mnc_file)[0].replace("\n","").replace('NULL','"Unassigned"')
	lmcc=[(k,v) for k,v in eval(ch.replace('{','[').replace('}',']')) if v!='Unassigned']
	d_mcc = dict(lmcc)
	# MCC-MNC
	remccmnc = re.compile(r'mcc_mnc_codes\[\] = \{(.*?)\};',re.MULTILINE|re.DOTALL)
	ch=remccmnc.findall(mcc_mnc_file)[0].replace("\n","").replace('NULL','"Unassigned"')
	lmccmnc=[(k,v) for k,v in eval(ch.replace('{','[').replace('}',']')) if v!='Unassigned']
	d_mccmnc = dict(lmccmnc)
	d_mccmnc[20825] =  "Lycamobile"
	d_mccmnc[20815] =  "Free Mobile"
	d_mccmnc[20801] =  "Orange"
	d_mccmnc[20810] =  "S.F.R."
	d_mccmnc[20810] =  "Bouygues Telecom"
	#print d_mccmnc

def imsi2mccmnc(imsi):
	prefix = str(imsi).strip()[:6]
	mcc = prefix[:3]
	mnc, mnc2, mnc3 = None, prefix[3:5], prefix[3:6]
	if d_mccmnc.has_key(int(mcc+mnc3)):
		mnc = mnc3
	elif d_mccmnc.has_key(int(mcc+mnc2+"0")):
		mnc = mnc2+"0"
	elif d_mccmnc.has_key(int(mcc+mnc2)):
		mnc = mnc2
	else:
		mnc = mnc2
	return (int(mcc),int(mnc),delete_paren(d_mcc.get(int(mcc),'')),delete_paren(d_mccmnc.get(int(mcc+mnc),'')))

if __name__ == '__main__':
	print delete_paren('Andorra (Principality of)')

