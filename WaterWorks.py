# Import package
from flask import Flask, render_template, request
import paho.mqtt.client as mqtt
import ssl, time, sys

# =======================================================
# Set Following Variables
# AWS IoT Endpoint
MQTT_HOST = "a2kul4sinpn50t.iot.ap-southeast-2.amazonaws.com"
# CA Root Certificate File Path
CA_ROOT_CERT_FILE = "root-CA.crt"
# AWS IoT Thing Name
THING_NAME = "myRaspberryPi_2"
# AWS IoT Thing Certificate File Path
THING_CERT_FILE = "myRaspberryPi_2.cert.pem"
# AWS IoT Thing Private Key File Path
THING_PRIVATE_KEY_FILE = "myRaspberryPi_2.private.key"
# =======================================================


# =======================================================
# No need to change following variables
MQTT_PORT = 8883
MQTT_KEEPALIVE_INTERVAL = 60
SHADOW_UPDATE_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update"
SHADOW_UPDATE_ACCEPTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/accepted"
SHADOW_UPDATE_REJECTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/rejected"
SHADOW_STATE_DOC_SPRINKLER_ON = """{"state" : {"desired" : {"SPRINKLER" : "ON"}}}"""
SHADOW_STATE_DOC_SPRINKLER_OFF = """{"state" : {"desired" : {"SPRINKLER" : "OFF"}}}"""
RESPONSE_RECEIVED = False
# =======================================================

# Define Flask App
app = Flask(__name__)

@app.route("/")
def main():
        return render_template('home.html')

@app.route('/door_ctrl', methods=['POST'])
def sprinklerCtrl():
	while True:
		if request.form['SPRINKLER'] == "ON":
			mqttc.publish(SHADOW_UPDATE_TOPIC,SHADOW_STATE_DOC_SPRINKLER_ON,qos=0)
		elif request.form['SPRINKLER'] == "OFF":
			mqttc.publish(SHADOW_UPDATE_TOPIC,SHADOW_STATE_DOC_SPRINKLER_OFF,qos=0)
	        return main()


# Define on connect event function
# We shall subscribe to Shadow Accepted and Rejected Topics in this function
def on_connect(mosq, obj, rc):
    mqttc.subscribe(SHADOW_UPDATE_ACCEPTED_TOPIC, 1)
    mqttc.subscribe(SHADOW_UPDATE_REJECTED_TOPIC, 1)

# Define on_message event function.
# This function will be invoked every time,
# a new message arrives for the subscribed topic
def on_message(mosq, obj, msg):
        if str(msg.topic) == SHADOW_UPDATE_ACCEPTED_TOPIC:
                print "\n---SUCCESS---\nShadow State Doc Accepted by AWS IoT."
                print "Response JSON:\n" + str(msg.payload)
        elif str(msg.topic) == SHADOW_UPDATE_REJECTED_TOPIC:
                print "\n---FAILED---\nShadow State Doc Rejected by AWS IoT."
                print "Error Response JSON:\n" + str(msg.payload)
        else:
                print "AWS Response Topic: " + str(msg.topic)
                print "QoS: " + str(msg.qos)
                print "Payload: " + str(msg.payload)
        # Disconnect from MQTT_Broker
        #mqttc.disconnect()				# Normally disconnected after one button click but needs to be disabled for multiple click events
        global RESPONSE_RECEIVED
        RESPONSE_RECEIVED = True


if __name__ == "__main__":
	# Initiate MQTT Client
	mqttc = mqtt.Client("client1")

	# Register callback functions
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect

	# Configure TLS Set
	mqttc.tls_set(CA_ROOT_CERT_FILE, certfile=THING_CERT_FILE, keyfile=THING_PRIVATE_KEY_FILE, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

	# Connect with MQTT Broker
	mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
	mqttc.loop_start()

        app.run(host='0.0.0.0')

	# Wait for Response
	Counter = 1
	while True:
        	time.sleep(1)
	        if Counter == 10:
	                print "No response from AWS IoT. Check your Settings."
	                break
	        elif RESPONSE_RECEIVED == True:
	                break
	        Counter = Counter + 1
