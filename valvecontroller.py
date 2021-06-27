import RPi.GPIO as GPIO
import time
import datetime
import http.client
import json
import requests

errorLedPin = 4
wateringLedPin = 17
relayPin0 = 23

valveId = 1

avgMoisture = 1000
avgWateringMinimum = 300
useSensors = 6

autoWateringDuration = 3

GPIO.setmode(GPIO.BCM)

GPIO.setup(errorLedPin, GPIO.OUT)
GPIO.setup(wateringLedPin, GPIO.OUT)
GPIO.setup(relayPin0, GPIO.OUT)

def water(duration):
	print("Watering now")
	GPIO.output(relayPin0, GPIO.LOW)
	GPIO.output(wateringLedPin, GPIO.HIGH)
	time.sleep(duration)
	GPIO.output(relayPin0, GPIO.HIGH)
	GPIO.output(wateringLedPin, GPIO.LOW)
	time.sleep(5)

while True:
	try:
		GPIO.output(errorLedPin, GPIO.LOW)
		GPIO.output(wateringLedPin, GPIO.LOW)
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
		#Calculate the sensor average value
		sensorTotal = 0
		for sensor in range(useSensors):
			sensorTotal = sensorTotal + sensorData[sensor]["value"]

		print(str(sensorTotal / useSensors))
		avgMoisture = int(sensorTotal / useSensors)

		#If the schedule_watering bool is set to true or the average moisture (calculated right before) is lower than the sensor watering trigger value
		if(data[0]['schedule_watering'] or avgMoisture < avgWateringMinimum):
			if(data[0]['schedule_watering_duration'] == 0):
				data[0]['schedule_watering_duration'] = autoWateringDuration

			water(int(data[0]['schedule_watering_duration']))
			connBody = "{\"id\": 1, \"last_time_watered\": " +str(int(datetime.datetime.now().timestamp()))+ " , \"schedule_watering\": false, \"schedule_watering_duration\": 0.0}"
			postreq = requests.post("http://000raspberry.ddns.net/cultivates/api/valve?password=12345678", connBody)
		else:
			print("No watering scheduled")
			time.sleep(1)

		conn.close()
	except Exception as e:
		GPIO.output(errorLedPin, GPIO.HIGH)
		print("An error occured")
		print(e)
		time.sleep(1)
