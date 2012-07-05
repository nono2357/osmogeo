#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# API Geolocalisation GSM Google Gears
# Author: Renaud Lifchitz

# Exemple : $ ./gmm2.py 208 1 24832 39863

import os, httplib, struct, time, sys, webbrowser, simplejson, pickle

dgeoloc = {}

def init_geoloc():
  global dgeoloc
  try:
    dgeoloc=pickle.load(open("gmm.pickle","rb"))  
  except IOError:
    dgeoloc = {}

def geoloc(mcc, mnc, lac, cid, show_on_map=False):
  global dgeoloc
  key = (mcc, mnc, lac, cid)
  if dgeoloc.has_key(key): return dgeoloc[key]
  params = simplejson.dumps({
    "version": "1.1.0",
    "host": "maps.google.com",
    "radio_type": "gsm",
    "request_address": True,
    "address_language": "fr_FR",
    "cell_towers": [
      {
	"cell_id": cid,
	"location_area_code": lac,
	"mobile_country_code": mcc,
	"mobile_network_code": mnc,
      }
    ],
  })
  headers = {
    "Content-Type" : "application/json",
    "Content-Length" : str(len(params)),
    "Cache-Control" : "no-cache",
    "Connection" : "close",
    "Host" : "www.google.com",
    "Accept-Charset" : "ISO-8859-15",
    "Accept-Encoding" : "plain",
  }
  while True:
    try:
      #conn = httplib.HTTPConnection("localhost",8118) # Proxy local type Privoxy/Tor
      conn = httplib.HTTPConnection("www.google.com",80)
      conn.request("POST", "/loc/json", params, headers)
      response = conn.getresponse()
      #print str(response.status)
      if str(response.status)=="200":
	data = response.read()
	conn.close()
	#print data
	dloc=simplejson.loads(data.decode("iso8859-15"))
	if dloc:
          #print dloc
	  lat,lon,acc=dloc['location']['latitude'], dloc['location']['longitude'], int(float(dloc['location']['accuracy']))
          dgeoloc[key]=(lat,lon)
          pickle.dump(dgeoloc,open('gmm.pickle','wb'))
	  return (lat,lon)
	#print "Error data : %s" % data
	dgeoloc[key]=None
	return None
    except Exception, msg:
      print "ERROR",msg
    time.sleep(0.3)
  dgeoloc[key]=None
  return None

if __name__ == '__main__':
  if len(sys.argv)==5:
    mcc, mnc, lac, cid = [int(v) for v in sys.argv[1:]]
    print geoloc(mcc, mnc, lac, cid, True)
  else:
    print "Usage: %s MCC MNC LAC CID" % sys.argv[0]

