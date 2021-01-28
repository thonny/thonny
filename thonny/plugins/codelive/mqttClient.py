import paho.mqtt.client as mqtt
import time

#listens for messages just run this


# Constants
BROKER = "test.mosquitto.org" # Set the MQTT broker (change if needed)
PORT = 1883
QOS = 0
LED = 16
MESSAGE = 'Button pressed'
TOPIC = "codelive/1"

# Callback when a connection has been established with the MQTT broker
def on_connect(client, userdata, rc, *extra_params):
    print('Connected with result code='+str(rc))

# Callback when client receives a message from the broker
def on_message(client, data, msg):
    if msg.topic == TOPIC:
        print(msg.payload.decode("utf-8"))
    #else:
       # print("Bye")

# Setup MQTT client and callbacks
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
# Connect to MQTT broker and subscribe to the button topic
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC, qos=QOS)
client.loop_forever()
client.disconnect()