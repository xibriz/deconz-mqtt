import urllib2
import json
import ConfigParser
import os
import paho.mqtt.publish as publish

class Lights:
	bri_max = 255.0

	def __init__(self):
		config = ConfigParser.RawConfigParser()
		config.read('./config/prod.cfg')

		self.mqtt_ip = config.get('MQTT', 'ip')
		self.mqtt_port = config.getint('MQTT', 'port')
		self.topic_pub = config.get('MQTT', 'light_pub')
		self.topic_sub = config.get('MQTT', 'light_sub')
		self.topic_status = config.get('MQTT', 'light_status')

		self.deconz_ip = config.get('deCONZ', 'ip')
		self.deconz_port = config.getint('deCONZ', 'port')
		self.api_key = config.get('deCONZ', 'api_key')

	def get_light(self, id):
		response = urllib2.urlopen('http://{}:{}/api/{}/lights/{}'.format(self.deconz_ip, self.deconz_port, self.api_key, id))
		resp_dict = json.loads(response.read())
		state = 0
		if resp_dict['state']['on']:
			state = int(round(resp_dict['state']['bri']/self.bri_max, 2)*100)
		publish.single(self.topic_pub.format(id), state, hostname=self.mqtt_ip, port=self.mqtt_port)


	def get_lights(self):
		response = urllib2.urlopen('http://{}:{}/api/{}/lights'.format(self.deconz_ip, self.deconz_port, self.api_key))
		resp_dict = json.loads(response.read())
		for key in resp_dict:
			state = 0
			if resp_dict[key]['state']['on']:
				state = int(round(resp_dict[key]['state']['bri']/self.bri_max, 2)*100)
			publish.single(self.topic_pub.format(key), state, hostname=self.mqtt_ip, port=self.mqtt_port)

	def set_light(self, id, state):
		url = 'http://{}:{}/api/{}/lights/{}/state'.format(self.deconz_ip, self.deconz_port, self.api_key, id)

		if state > 0:
			on = True
			bri = int((state / 100.0)*self.bri_max)
			data = json.dumps({'on': True, 'bri': bri})
		else:
			data = json.dumps({'on': False})

		opener = urllib2.build_opener(urllib2.HTTPHandler)
		request = urllib2.Request(url, data=data)
		request.add_header('Content-Type', 'application/json')
		request.get_method = lambda: 'PUT'
		url = opener.open(request)

		# TODO: do something with the result.. maybe call get_light?
		#print url.read()
		self.get_light(id)

