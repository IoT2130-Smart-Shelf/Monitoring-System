"""Monitoring System Smart Shelf

Members:
    - Juan Sebastián Barreto Jimenéz
    - Carolina María Burgos Anillo
    - Edwin Alejandro Caicedo Palacios
"""

# Imports of the necessary libraries
import paho.mqtt.publish as publish
import smtplib, ssl
from firebase import firebase
import adafruit_vl53l0x as av
import busio
import RPi.GPIO as GPIO
import time

# Time limit of data transfer to ThingSpeak
time_init = 0
time_finish = 15
first_send = False

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

# Functions

#   Function: laser_linearization() 
#   Purpose: Linearize the laser sensor
#   Argument:
#       data: Measured distance
#   Return:
#       Linearized measured distance
def laser_linearization(data):
    if data > 8100:
        return 8190/10
    elif data < 310:
        data_l = (0.9393*data - 23.943)/10
        return round(data_l,2)
    elif data < 500:
        data_l = (1.0238*data - 50.087)/10
        return round(data_l,2)
    elif data < 860:
        data_l = (1.2657*data - 189.03)/10
        return round(data_l,2)
    elif data < 1010:
        data_l = (0.8114*data+279.98)/10
        return round(data_l,2)
    else: 
        data_l = (0.0385*data + 1125.7)/10
        return round(data_l,2)

#   Function: send_mqtt_thingsSpeak() 
#   Purpose: Send data from two fields by mqtt to thingspeak
#   Argument:
#       distanceSound: Measured distance by ultrasound sensor
#       distanceLaser: Measured distance by laser sensor
#   Return:
#       Confirmation or error message
def send_mqtt_thingsSpeak(distanceSoundOne, distanceSoundTwo, distanceSoundThree, distanceLaser):
    tTransport = "websockets" # Protocol comunication
    tTLS = {'ca_certs':"/etc/ssl/certs/ca-certificates.crt",'tls_version':ssl.PROTOCOL_TLSv1} # Security for comunication by MQTT
    tPort = 443 # Port for MQTT
    channelID = "1481979" # Channel ID of ThingSpeak
    writeApiKey = "R6KP5RUYDZOS6XKO" # Write API Key of ThingSpeak
    mqttHost = "mqtt.thingspeak.com" # Host of ThingSpeak
    topic = "channels/" + channelID + "/publish/" + writeApiKey # Topic of MQTT for ThingSpeak

    # build the payload string
    tPayload = "field1=" + str(distanceSoundOne) + "&field2=" + str(distanceSoundTwo)  + "&field3=" + str(distanceSoundThree)  + "&field4=" + str(distanceLaser)
    
    # attempt to publish this data to the topic
    try:
        publish.single(topic, payload=tPayload, hostname=mqttHost, port=tPort, tls=tTLS, transport=tTransport)
        return "Datos enviados"
    except (Exception):
        return "Hubo un error al publicar los datos."
    
def sendAlert(email_string, alerta):
    if alerta == 2:
        subject = "ALERTA PRODUCTO MAL UBICADO"
    else:
        subject = "ALERTA EXISTENCIAS AGOTADAS"
    email_from = 'smart.shelf.iot2021@gmail.com'
    password = 'SMARTshelf2021'
    email_to = 'jsebastian.barretoj99@gmail.com'
    message = 'Subject: {}\n\n{}'.format(subject, email_string)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_from, password)
        server.sendmail(email_from, email_to, message)

while True:
    try:
        GPIO.setmode(GPIO.BCM)
        
        # Read laser sensor
        distance_laser = laser_linearization(laser_sensor.range)

        #if first_send:
        #    time_finish = time.time()

        if distance_laser < 64: #and time_finish - time_init >= 15)):
            first_send = True
            print("Laser Sensor Range: {0}cm".format(distance_laser))

            # Read ultrasound sensor one
            GPIO.output(TRIG_ONE, GPIO.LOW)
            time.sleep(2)
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

            # Read ultrasound sensor two
            GPIO.output(TRIG_TWO, GPIO.LOW)
            time.sleep(2)
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

            # Read ultrasound sensor three
            GPIO.output(TRIG_THREE, GPIO.LOW)
            time.sleep(2)
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
            #time_init = time.time()
            print(send_mqtt_thingsSpeak(distance_ultrasound_one, distance_ultrasound_two, distance_ultrasound_three, distance_laser))

    except (KeyboardInterrupt):
        break
