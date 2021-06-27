#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import spidev
import os
import time
import http.client
import datetime
import traceback

delay = 10

GPIO.setmode(GPIO.BCM)

measuringLedPin = 22
errorLedPin = 4

GPIO.setup(measuringLedPin, GPIO.OUT)
GPIO.setup(errorLedPin, GPIO.OUT)

conn = http.client.HTTPConnection("000raspberry.ddns.net", timeout=2) #2 seconds timeout

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

def readChannel(channel):
  val = spi.xfer2([1,(8+channel)<<4,0])
  data = ((val[1]&3) << 8) + val[2]
  return data

def updateDbContent(sensorId, value):
  GPIO.output(measuringLedPin, GPIO.HIGH)

  conn = http.client.HTTPConnection("000raspberry.ddns.net", timeout=2)

  headers = {
      'content-type': "application/json",
  }
  body = ""

  timestamp = str(int(datetime.datetime.now().timestamp()))
  conn.request("PUT", "/cultivates/api/sensors?username=ubuntu&password=12345678&id="+str(sensorId+1)+"&value="+str(value)+"&updated_at="+timestamp , body, headers)

  res = conn.getresponse()
  data = res.read()

  conn.close()

  time.sleep(0.125)
  GPIO.output(measuringLedPin, GPIO.LOW)
  time.sleep(0.125)

if __name__ == "__main__":
  try:
    while True:
      GPIO.output(errorLedPin, GPIO.LOW)
      GPIO.output(measuringLedPin, GPIO.LOW)

      for i in range(8):
          val = 0
          for j in range(50):
            val = val + readChannel(i)
          value = int(val / 50)
          print(value)
          try:
            updateDbContent(i, value)
          except Exception as e:
            GPIO.output(measuringLedPin, GPIO.LOW)
            GPIO.output(errorLedPin, GPIO.HIGH)
            traceback.print_exc()
            time.sleep(1)
            GPIO.output(errorLedPin, GPIO.LOW)
      print("")
      time.sleep(delay)
  except KeyboardInterrupt:
    print("Cancel.")


