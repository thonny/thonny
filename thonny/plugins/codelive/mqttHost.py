import paho.mqtt.client as mqtt
import time
import os

#run this once, does not repeat.


# class MqttConnection:
#     def __init__(self):
#         self.broker ="test.mosquitto.org" #TODO: have backup servers - a list of possible alternatives
#         self.port = 1883
#         self.qos = 0
#         self.delay = 1.0
#         self.topic = "codelive/1" #TODO: generate this dynamically
    
#     def ConnectToSession(self, client):
#         client.connect(self.broker, self.port, 60)
#         client.subscribe(self.topic, qos=self.qos)
    
#     def EndSession(self, client):
#         client.disconnect()

#     def PublishMessage(self, client, msg):
#         client.publish(self.topic, msg)

#     # Callback when a message is published
#     def on_publish(client, userdata, mid):
#         #do something

#     # Callback when connecting to the MQTT broker
#     def on_connect(self,client, userdata, flags, rc):
#         if rc==0:
#             #return 'Connected to ' + self.broker
#             #do something

#     # Callback when client receives a PUBLISH message from the broker
#     def on_message(self,client, data, msg):
#         if msg.topic == self.topic:
#             print(msg.payload.decode("utf-8"))
#             #add to queue instead of what we're doing above




# myClient = mqtt.Client()
# myConnection = MqttConnection()
# myClient.on_message = myConnection.on_message
# myConnection.ConnectToSession(myClient)
# myClient.loop_start()


# try:
#     while True:
#         myConnection.PublishMessage(myClient, "testing ")
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("Done")
#     myConnection.EndSession(myClient)



class MqttConnection:
    def __init__(self):
        self.client = mqtt.Client()
        self.broker ="test.mosquitto.org" #TODO: have backup servers - a list of possible alternatives
        self.port = 1883
        self.qos = 0
        self.delay = 1.0
        self.topic = "codelive/1" #TODO: generate this dynamically
    
    def ConnectToSession(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.subscribe(self.topic, qos=self.qos)
    
    def EndSession(self):
        self.client.disconnect()

    def PublishMessage(self, msg):
        self.client.publish(self.topic, msg)

    # Callback when a message is published
    def on_publish(self, client, userdata, mid):
        print("")
        #do something

    # Callback when connecting to the MQTT broker
    def on_connect(self,client, userdata, flags, rc):
        if rc==0:
            print('Connected to ' + self.broker)
            #do something

    # Callback when client receives a PUBLISH message from the broker
    def on_message(self,client, data, msg):
        if msg.topic == self.topic:
            print(msg.payload.decode("utf-8"))
            #add to queue instead of what we're doing above




myConnection = MqttConnection()
client = myConnection.client
client.on_message = myConnection.on_message
myConnection.ConnectToSession()
#client.loop_start()


try:
    myConnection.PublishMessage("testing ")
except KeyboardInterrupt:
    print("Done")
    myConnection.EndSession(myClient)



