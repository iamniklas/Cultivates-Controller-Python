import RPi.GPIO as GPIO
import time
import datetime
import http.client
import json
import requests
import shared

relayPin0 = shared.watering_pin
led_indicator = shared.watering_led_pin

valveId = 1

avgMoisture = 1000
avgWateringMinimum = 300
useSensors = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(relayPin0, GPIO.OUT)

while True:
	conn = http.client.HTTPConnection("000raspberry.ddns.net", timeout=0.5)
	headers = {
	    'content-type': "application/json"
	}
	body = ""

	timestamp = str(int(datetime.datetime.now().timestamp()))
	conn.request("GET", "/cultivates/api/valve?password=12345678&id=" + str(valveId), body, headers)

	res = conn.getresponse()
	data = json.loads(res.read())

	#Sensor Data Request
	conn.request("GET", "/cultivates/api/sensors?password=12345678")
	sensorrequest = conn.getresponse()
	sensor = sensorrequest.read()
	sensorData = json.loads(sensor)
	print(len(sensorData))
	sensorTotal = 0
	for sensor in range(useSensors):
		sensorTotal = sensorTotal + sensorData[sensor]["value"]

	print(str(sensorTotal / useSensors))
	avgMoisture = int(sensorTotal / useSensors)


	if(data[0]['schedule_watering'] or avgMoisture < avgWateringMinimum):
		print("Watering now")

		GPIO.output(led_indicator, GPIO.HIGH)
		GPIO.output(relayPin0, GPIO.LOW)
		time.sleep(int(data[0]['schedule_watering_duration']))
		GPIO.output(led_indicator, GPIO.LOW)
		GPIO.output(relayPin0, GPIO.HIGH)
		time.sleep(2)

		connBody = "{\"id\": 1, \"last_time_watered\": " +str(int(datetime.datetime.now().timestamp()))+ " , \"schedule_watering\": false, \"schedule_watering_duration\": 0.0}"
		#print(connBody)
		postreq = requests.post("http://000raspberry.ddns.net/cultivates/api/valve?password=12345678", connBody)
	else:
		print("No watering scheduled")
		time.sleep(1)

	conn.close()
