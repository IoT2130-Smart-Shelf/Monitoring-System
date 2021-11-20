"""Monitoring System Smart Shelf

Members:
    - Juan Sebastián Barreto Jimenéz
    - Carolina María Burgos Anillo
    - Edwin Alejandro Caicedo Palacios
"""

# Imports of the necessary libraries
import paho.mqtt.publish as publish
import ssl
from firebase import firebase
import adafruit_vl53l0x as av
import busio
import RPi.GPIO as GPIO
import time

# Definition of classes
class Producto:
    def __init__(self, data):
        self.cantidad = data['Cantidad']
        self.fabricante = data['Fabricante']
        self.id = data['Id']
        self.imagen = data['Imagen']
        self.nombre = data['Nombre']
        self.precio = data['Precio']
        self.tamano = data['Tamano']
        self.unidadMedida = data['UnidadMedida']
    
    def __str__(self):
        print("Producto", self.id)
        print("    Cantidad =", self.cantidad)
        print("    Fabricante =", self.fabricante)
        print("    Imagen =", self.imagen)
        print("    Nombre =", self.nombre)
        print("    Precio =", self.precio)
        print("    Tamano =", self.tamano)
        print("    UnidadMedida =", end=" ")
        return self.unidadMedida

# Use firebase
firebaseDB= firebase.FirebaseApplication("https://smart-shelf-44c69-default-rtdb.firebaseio.com/", None)
productos = []

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

#   Function: readUltrasoundSensor() 
#   Purpose: Read distance from Ultrasound Sensor
#   Argument:
#       trig: Pin of TRIG
#       echo: Pin of ECHO
#   Return:
#       distance in cm
def readUltraSoundSensor(trig, echo):
    # Read ultrasound sensor
    GPIO.output(trig, GPIO.LOW)
    time.sleep(2)
    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig, GPIO.LOW)
    while GPIO.input(echo)==0:
        pulse_start_one = time.time()
    while GPIO.input(echo)==1:
        pulse_end_one = time.time()
    pulse_duration_one = pulse_end_one - pulse_start_one
    return round(pulse_duration_one*17150,2)

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

#   Function: downloadDataDB() 
#   Purpose: Download data of productos from Firebase Realtime DB
#   Argument:
#       void
#   Return:
#       void
def downloadDataDB():
    resultData = firebaseDB.get('/Tiendas/MaxiDespensa/Productos/', '')
    productos = []
    for data in resultData.values():
        producto = Producto(data)
        productos.append(producto)

downloadDataDB() # download data from firebase first time

while True:
    try:
        GPIO.setmode(GPIO.BCM)
        
        # Read laser sensor
        distance_laser = laser_linearization(laser_sensor.range)

        if distance_laser < 64:
            print("Laser Sensor Range: {0}cm".format(distance_laser))

            # Read ultrasound sensor one
            distance_ultrasound_one = readUltraSoundSensor(TRIG_ONE, ECHO_ONE)
            print("Distance Ultrasound One: ", distance_ultrasound_one," cm")

            # Read ultrasound sensor two
            distance_ultrasound_two = readUltraSoundSensor(TRIG_TWO, ECHO_TWO)
            print("Distance Ultrasound Two: ", distance_ultrasound_two," cm")

            # Read ultrasound sensor three
            distance_ultrasound_three = readUltraSoundSensor(TRIG_THREE, ECHO_THREE)
            print("Distance Ultrasound Three: ", distance_ultrasound_three," cm")

            # Send data to thingSpeak by mqtt
            print(send_mqtt_thingsSpeak(distance_ultrasound_one, distance_ultrasound_two, distance_ultrasound_three, distance_laser))

    except (KeyboardInterrupt):
        break