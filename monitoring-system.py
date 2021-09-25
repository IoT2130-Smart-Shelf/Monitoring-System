"""Monitoring System Smart Shelf

Members:
    - Juan Sebastián Barreto Jimenéz
    - Carolina María Burgos Anillo
    - Edwin Alejandro Caicedo Palacios
"""

# Imports of the necessary libraries
from mqtt_thingspeak import send_mqtt_thingsSpeak
from Laser_Sensor.laser_linear import laser_linearization
import adafruit_vl53l0x as av
import busio
import RPi.GPIO as GPIO
import time

# Initialize number pins of I2C for Laser Sensor
SCL = 3
SDA = 2

# Initialize I2C bus and sensor.
i2c = busio.I2C(SCL, SDA)
laser_sensor = av.VL53L0X(i2c)

# Initialize numeric pins for ultrasound sensors
TRIG_ONE = 23
ECHO_ONE = 24
TRIG_TWO = 17
ECHO_TWO = 27
TRIG_THREE = 5
ECHO_THREE = 6

# Initialize GPIO for ultrasound sensors
# Ultrasound sensor one
GPIO.setup(TRIG_ONE, GPIO.OUT)
GPIO.setup(ECHO_ONE, GPIO.IN)
# Ultrasound sensor two
GPIO.setup(TRIG_TWO, GPIO.OUT)
GPIO.setup(ECHO_TWO, GPIO.IN)
# Ultrasound sensor three
GPIO.setup(TRIG_THREE, GPIO.OUT)
GPIO.setup(ECHO_THREE, GPIO.IN)

while True:
    try:
        # Read laser sensor
        distance_laser = laser_linearization(laser_sensor.range)

        if(distance_laser < 810):
            print("Laser Sensor Range: {0}cm".format(distance_laser))
            # Read ultrasound sensors
            GPIO.output(TRIG_ONE, GPIO.LOW)
            print("Waiting for ultrasound sensor one to settle") 
            time.sleep(2)
            print("Calculating distance of ultrasound sensors")
            GPIO.output(TRIG_ONE, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_ONE, GPIO.LOW)
            
            while GPIO.input(ECHO_ONE)==0:
                pulse_start_one = time.time()
            while GPIO.input(ECHO_ONE)==1:
                pulse_end_one = time.time()
            
            pulse_duration_one = pulse_end_one - pulse_start_one
            distance_ultrasound_one = round(pulse_duration_one*17150,2)

            print("Distance Ultrasound One: ", distance_ultrasound_one," cm")

            GPIO.output(TRIG_TWO, GPIO.LOW)

            print("Waiting for ultrasound sensor two to settle") 
            time.sleep(2)
            print("Calculating distance of ultrasound sensor two")
            GPIO.output(TRIG_TWO, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_TWO, GPIO.LOW)
            
            while GPIO.input(ECHO_TWO)==0:
                pulse_start_two = time.time()
            while GPIO.input(ECHO_TWO)==1:
                pulse_end_two = time.time()

            pulse_duration_two = pulse_end_two - pulse_start_two
            distance_ultrasound_two = round(pulse_duration_two*17150,2)

            print("Distance Ultrasound Two: ", distance_ultrasound_two," cm")

            GPIO.output(TRIG_THREE, GPIO.LOW)

            print("Waiting for ultrasound sensor three to settle") 

            time.sleep(2)
            print("Calculating distance of ultrasound sensor three")
            GPIO.output(TRIG_THREE, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(TRIG_THREE, GPIO.LOW)
            
            while GPIO.input(ECHO_THREE)==0:
                pulse_start_three = time.time()
            while GPIO.input(ECHO_THREE)==1:
                pulse_end_three = time.time()

            pulse_duration_three = pulse_end_three - pulse_start_three
            distance_ultrasound_three = round(pulse_duration_three*17150,2)

            print("Distance Ultrasound Three: ", distance_ultrasound_three," cm")

            # Send data to thingSpeak by mqtt
            send_mqtt_thingsSpeak(distance_ultrasound_one, distance_ultrasound_two, distance_ultrasound_three, distance_laser)

    except (KeyboardInterrupt):
        break
    finally:
        GPIO.cleanup()