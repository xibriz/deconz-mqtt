import urllib2
import json
import ConfigParser
import os
import paho.mqtt.publish as publish

class Lights:
	bri_max = 255.0
	groups = []
	lights = []

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

		self.get_groups()

	def get_light(self, light_name):
		#print 'get_light: {}'.format(light_name)
		id = self.get_light_id(light_name)

		try:
			response = urllib2.urlopen('http://{}:{}/api/{}/lights/{}'.format(self.deconz_ip, self.deconz_port, self.api_key, id))
			resp_dict = json.loads(response.read())
		except urllib2.HTTPError, urllib2.URLError:
			return False

		state = 0
		if resp_dict['state']['on']:
			state = int(round(resp_dict['state']['bri']/self.bri_max, 2)*100)

		group_name = self.get_group_name(id)
		publish.single(self.topic_pub.format(group_name=group_name, light_name=light_name), state, hostname=self.mqtt_ip, port=self.mqtt_port)


	def get_lights(self):
		try:
			response = urllib2.urlopen('http://{}:{}/api/{}/lights'.format(self.deconz_ip, self.deconz_port, self.api_key))
			self.lights = json.loads(response.read())
		except urllib2.HTTPError, urllib2.URLError:
			return False

		for key in self.lights:
			state = 0
			if self.lights[key]['state']['on']:
				state = int(round(self.lights[key]['state']['bri']/self.bri_max, 2)*100)
			light_name = self.lights[key]['name'].replace(" ", "")
			group_name = self.get_group_name(key)
			publish.single(self.topic_pub.format(group_name=group_name, light_name=light_name), state, hostname=self.mqtt_ip, port=self.mqtt_port)

	def set_light(self, light_name, state):
		try:
			state = int(state)
		except ValueError:
			self.get_light(light_name)
			return False

		id = self.get_light_id(light_name)
		url = 'http://{}:{}/api/{}/lights/{}/state'.format(self.deconz_ip, self.deconz_port, self.api_key, id)

		if state > 0:
			on = True
			bri = int((state / 100.0)*self.bri_max)
			data = json.dumps({'on': True, 'bri': bri})
		else:
			data = json.dumps({'on': False})

		try:
			opener = urllib2.build_opener(urllib2.HTTPHandler)
			request = urllib2.Request(url, data=data)
			request.add_header('Content-Type', 'application/json')
			request.get_method = lambda: 'PUT'
			url = opener.open(request)

			#print url.read()
			self.get_light(light_name)
		except urllib2.HTTPError, urllib2.URLError:
			return False

	def get_groups(self):
		try:
			response = urllib2.urlopen('http://{}:{}/api/{}/groups'.format(self.deconz_ip, self.deconz_port, self.api_key))
			self.groups = json.loads(response.read())
		except urllib2.HTTPError, urllib2.URLError:
			return False

	def get_group_name(self, light_id):
		for key in self.groups:
			#print key, self.groups[key]['devicemembership']
			if light_id in self.groups[key]['lights']:
				return self.groups[key]['name'].replace(" ", "")

	def get_light_id(self, light_name):
		for key in self.lights:
			if light_name == self.lights[key]['name'].replace(" ", ""):
				return key
