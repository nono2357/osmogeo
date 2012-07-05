#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3

# OsmocomBB installation path
INSTALL_PATH = "/home/renaud/installations/osmocombb/"

# Initialize Database
#dbcon = sqlite3.connect(":memory:")
dbcon = sqlite3.connect('test.db')
dbcon.isolation_level = None
dbcur = dbcon.cursor()
dbcur.execute('''CREATE TABLE antennas (ddate TEXT, arfcn INTEGER PRIMARY KEY, mcc INTEGER, mnc INTEGER, lac INTEGER, cid INTEGER, country TEXT, network TEXT, lat REAL, lon REAL)''')
dbcur.execute('''CREATE TABLE imsis (ddate TEXT, imsi TEXT, arfcn INTEGER, mcc INTEGER, mnc INTEGER, country TEXT, network TEXT)''')
dbcur.execute('''CREATE INDEX indeximsi on imsis (imsi)''')

