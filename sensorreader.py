#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import spidev
import os
import time
import http.client
import datetime
import traceback
import shared

delay = 10

GPIO.setmode(GPIO.BCM)

led_pin = shared.transmit_led_pin
error_pin = shared.error_led_pin

GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(error_pin, GPIO.OUT)
conn = http.client.HTTPConnection("000raspberry.ddns.net:80", timeout=2) #2 seconds timeout

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

def readChannel(channel):
  val = spi.xfer2([1,(8+channel)<<4,0])
  data = ((val[1]&3) << 8) + val[2]
  return data

def updateDbContent(sensorId, value):
  GPIO.output(led_pin, GPIO.HIGH)

  headers = {
      'content-type': "application/json",
  }
  body = ""

  timestamp = str(int(datetime.datetime.now().timestamp()))
  conn.request("PUT", "/cultivates/api/sensors?username=ubuntu&password=12345678&id="+str(sensorId+1)+"&value="+str(value)+"&updated_at="+timestamp , body, headers)

  res = conn.getresponse()
  data = res.read()
  #print(data)

  conn.close()

  time.sleep(0.125)
  GPIO.output(led_pin, GPIO.LOW)
  time.sleep(0.125)

if __name__ == "__main__":
  GPIO.output(error_pin, GPIO.LOW)
  try:
    while True:
      for i in range(8):
          val = 0
          for j in range(50):
            val = val + readChannel(i)
          value = int(val / 50)
          print(value)
          try:
            updateDbContent(i, value)
          except Exception as e:
            GPIO.output(led_pin, GPIO.LOW)
            GPIO.output(error_pin, GPIO.HIGH)
            traceback.print_exc()
      print("")
      time.sleep(delay)
  except KeyboardInterrupt:
    print("Cancel.")
