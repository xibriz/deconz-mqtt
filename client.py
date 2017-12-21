import paho.mqtt.client as mqtt
import re
from src import lights

light = lights.Lights()
rg_set = re.compile(light.topic_sub.format('(.*?)').replace('/','\\/'))
rg_status = re.compile(light.topic_status.format('(.*?)').replace('/','\\/'))

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	#print("Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("deconz/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	#print(msg.topic+" "+str(msg.payload))
	m = rg_set.search(msg.topic)
	if m:
		id = m.group(1)
		light.set_light(id, int(msg.payload))

	m = rg_status.search(msg.topic)
	if m:
		id = m.group(1)
		light.get_light(id)



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(light.mqtt_ip, light.mqtt_port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
