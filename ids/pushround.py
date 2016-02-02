#!/usr/bin/env python

import os
import sqlite3
import xmltodict, json
import argparse

#from flask import g

CONVO_DIR="conversations/"
STAGING_DIR="staging/"
SERVICES = {}

def parseReport(filepath):
	doc = {}
	i = 0
	db = sqlite3.connect('db.db')
	with open(filepath,'r') as fd:
		doc = xmltodict.parse(fd.read())
	doc = doc['dfxml']['configuration'][1]['fileobject']
	fname = ""
	for convo in doc:
		svc_port = min(int(convo['tcpflow']['@dstport']), int(convo['tcpflow']['@srcport']))
		if svc_port not in SERVICES:
			SERVICES[svc_port]="svc_{0}".format(svc_port)
			try:
				db.cursor().execute("INSERT INTO services (name, port) VALUES (?, ?)", [SERVICES[svc_port],svc_port])
				db.commit()
			except sqlite3.IntegrityError:
				print "Already in db"
				pass

		try:
			fname = convo['filename']
		except KeyError:
			pass

		try:
			db.cursor().execute("""INSERT INTO conversations 
			                (filename, size, time, s_port, d_port, s_ip, d_ip, round, service) VALUES         
			                (?, ?, ?, ?, ?, ?, ?, ?, (SELECT id FROM services WHERE port = (?)) )""", 
			                (fname, convo['filesize'], convo['tcpflow']['@startime'], 
			                convo['tcpflow']['@srcport'], convo['tcpflow']['@dstport'], convo['tcpflow']['@src_ipn'],
			                convo['tcpflow']['@dst_ipn'],0,svc_port) )
			db.commit()
		except sqlite3.IntegrityError:
			print "Already in db"
			pass

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Process xml files generated by tcpflow and enter them into the database')
	parser.add_argument('files', metavar='l', type=str, nargs='+', help='a list of xml files to parse')
	args = parser.parse_args()
	print args.files
	for f in args.files:
		parseReport(f)
