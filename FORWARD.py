#!/usr/bin/env python
# -*- coding: utf-8 -*-
# A SIMPLE HTTP PROXY FIX VS2015 IIS ONLY ACCESSABLE FROM LOCAL PROBLEM
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import urllib2

class NO_EXCEPTION(urllib2.HTTPErrorProcessor):
	def http_response(self, request, response):
		return response
	https_response = http_response

def HEADERS_TO_DICT(headers):
	DICT = {}
	for H in headers:
		SPLIT = H.find(":")
		if SPLIT > 0:
			DICT[H[:SPLIT]] = H[SPLIT+1:].strip()
	return DICT

class HANDLER(BaseHTTPRequestHandler):
	FORWARD_TARGET = "localhost:2741"
	
	def FORWARD(self, IS_POST):
		URL = "http://%s%s"%(self.FORWARD_TARGET, self.path)
		# print self.headers
		COOKIE = self.headers.getheader("Cookie")
		CONTENT_TYPE = self.headers.getheader("Content-Type")
		print "FORWARD %s"%URL
		
		OPENER = urllib2.build_opener(NO_EXCEPTION)
		if COOKIE:
			OPENER.addheaders.append(("Cookie", COOKIE))
		if CONTENT_TYPE:
			OPENER.addheaders.append(("Content-Type", CONTENT_TYPE))
		POSTDATA = None
		if IS_POST:
			LENGTH = int(self.headers.getheader("Content-Length", 0))
			POSTDATA = self.rfile.read(LENGTH)
		RESPONSE = OPENER.open(URL, POSTDATA)
		CODE = RESPONSE.code
		RESPONSE_DATA = RESPONSE.read()
		RESPONSE_HEADERS = HEADERS_TO_DICT(RESPONSE.info().headers)
		print "RESULT CODE %s"%CODE
		
		self.send_response(CODE)
		for K, V in RESPONSE_HEADERS.iteritems():
			self.send_header(K, V)
		self.end_headers()
		self.wfile.write(RESPONSE_DATA)
		self.wfile.close()
	
	def do_GET(self):
		self.FORWARD(0)
	
	def do_POST(self):
		self.FORWARD(1)

class THREAD_HTTP_SERVER(ThreadingMixIn, HTTPServer):
	def __init__(self, *args):
		HTTPServer.__init__(self, *args)
		print "SERVER STARTED, PRESS CTRL+C EXIT"
		print "SOMETIME YOU WILL GET FREEZE"
		print "KILL PYTHON.EXE ON YOUR TASKMANAGER"

if __name__ == "__main__":
	def SERVER_THREAD():
		SERVER = THREAD_HTTP_SERVER(("0.0.0.0", 12741), HANDLER)
		SERVER.serve_forever()
	THREAD = threading.Thread(target = SERVER_THREAD)
	THREAD.setDaemon(1)
	THREAD.start()
	while 1:
		raw_input()
