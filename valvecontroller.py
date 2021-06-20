import RPi.GPIO as GPIO
import time
import datetime
import http.client
import json
import requests

relayPin0 = 23

valveId = 1

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

	if(data[0]['schedule_watering']):
		print("Watering scheduled")

		connBody = "{\"id\": 1, \"last_time_watered\": " +str(int(datetime.datetime.now().timestamp()))+ " , \"schedule_watering\": false, \"schedule_watering_duration\": 0.0}"
		print(connBody)
		postreq = requests.post("http://000raspberry.ddns.net/cultivates/api/valve?password=12345678", connBody)
		#print(postreq.text)

		GPIO.output(relayPin0, GPIO.LOW)
		time.sleep(5)
		GPIO.output(relayPin0, GPIO.HIGH)
	else:
		#print("No watering scheduled")
		time.sleep(1)

	conn.close()
