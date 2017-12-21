import urllib2
import json
import ConfigParser
import hashlib
import time

config = ConfigParser.RawConfigParser()
config.read('./config/prod.cfg')

deconz_ip = config.get('deCONZ', 'ip')
deconz_port = config.getint('deCONZ', 'port')

url = 'http://{}:{}/api'.format(deconz_ip, deconz_port)

api_key = hashlib.sha224(str(time.time())).hexdigest()
data = json.dumps({"username": api_key,"devicetype": "deconz-mqtt"})

opener = urllib2.build_opener(urllib2.HTTPHandler)
request = urllib2.Request(url, data=data)
request.add_header('Content-Type', 'application/json')
request.get_method = lambda: 'POST'

try:
	url = opener.open(request)
	config.set('deCONZ', 'api_key', api_key)
	with open('./config/prod.cfg', 'wb') as configfile:
		config.write(configfile)
	print 'api key written to config file'
except urllib2.HTTPError as err:
	print err.code

