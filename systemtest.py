import shared
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(shared.error_led_pin, GPIO.OUT)
GPIO.setup(shared.watering_led_pin, GPIO.OUT)
GPIO.setup(shared.transmit_led_pin, GPIO.OUT)
GPIO.setup(shared.watering_pin, GPIO.OUT)

for i in range(1000):
	GPIO.output(shared.error_led_pin, GPIO.HIGH)
	GPIO.output(shared.watering_led_pin, GPIO.HIGH)
	GPIO.output(shared.transmit_led_pin, GPIO.HIGH)
	GPIO.output(shared.watering_pin, GPIO.HIGH)

	time.sleep(0.5)

	GPIO.output(shared.error_led_pin, GPIO.LOW)
	GPIO.output(shared.watering_led_pin, GPIO.LOW)
	GPIO.output(shared.transmit_led_pin, GPIO.LOW)
	GPIO.output(shared.watering_pin, GPIO.LOW)

	time.sleep(0.5)
