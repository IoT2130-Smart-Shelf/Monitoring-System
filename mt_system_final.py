"""Monitoring System Smart Shelf

Members:
    - Juan Sebastián Barreto Jimenéz
    - Carolina María Burgos Anillo
    - Edwin Alejandro Caicedo Palacios
"""

# Imports of the necessary libraries
import paho.mqtt.publish as publish
import ssl, smtplib
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
def send_mqtt_thingsSpeak(distanceSoundOne, distanceSoundTwo, distanceSoundThree):
    tTransport = "websockets" # Protocol comunication
    tTLS = {'ca_certs':"/etc/ssl/certs/ca-certificates.crt",'tls_version':ssl.PROTOCOL_TLSv1} # Security for comunication by MQTT
    tPort = 443 # Port for MQTT
    channelID = "1481979" # Channel ID of ThingSpeak
    writeApiKey = "R6KP5RUYDZOS6XKO" # Write API Key of ThingSpeak
    mqttHost = "mqtt.thingspeak.com" # Host of ThingSpeak
    topic = "channels/" + channelID + "/publish/" + writeApiKey # Topic of MQTT for ThingSpeak

    # build the payload string
    tPayload = "field1=" + str(distanceSoundOne) + "&field2=" + str(distanceSoundTwo)  + "&field3=" + str(distanceSoundThree)

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

downloadDataDB() # download data from firebase first time

# Initial Measure
distance_laser_initial = laser_linearization(laser_sensor.range)
distance_laser_prev = distance_laser_initial
distance_ultrasound_one_initial = readUltraSoundSensor(TRIG_ONE, ECHO_ONE)
distance_ultrasound_one_prev = distance_ultrasound_one_initial
distance_ultrasound_two_initial = readUltraSoundSensor(TRIG_TWO, ECHO_TWO)
distance_ultrasound_two_prev = distance_ultrasound_two_initial
distance_ultrasound_three_initial = readUltraSoundSensor(TRIG_THREE, ECHO_THREE)
distance_ultrasound_three_prev = distance_ultrasound_three_initial

initial_time = time.perf_counter()

while True:
    try:
        GPIO.setmode(GPIO.BCM)
        
        # Read laser sensor
        distance_laser = laser_linearization(laser_sensor.range)

        end_time = time.perf_counter()
        if end_time - initial_time > 120:
            initial_time = end_time
            # Send data to thingSpeak by mqtt
            print(send_mqtt_thingsSpeak(productos[0].cantidad,productos[1].cantidad,productos[2].cantidad))

        if distance_laser < 64:
            print("Laser Sensor Range: {0}cm".format(distance_laser))

            # Read ultrasound sensor one
            distance_ultrasound_one = readUltraSoundSensor(TRIG_ONE, ECHO_ONE)
            print("Distance Ultrasound One: ", distance_ultrasound_one," cm")
            if(distance_ultrasound_one - distance_ultrasound_one_prev > 2):
                productos[0].cantidad -= 1
            if((distance_ultrasound_one_initial - 1 < distance_ultrasound_one) and  (distance_ultrasound_one < distance_ultrasound_one_initial +1) and (productos[0].cantidad < 2)):
                productos[0].cantidad = 0
                email_string = "Hola!\n\nSmart Shelf le avisa que la " + productos[0].nombre + " esta agotada.\n\nGracias por ser parte de nosotros"
                sendAlert(email_string, 1)
            distance_ultrasound_one_prev = distance_ultrasound_one

            # Read ultrasound sensor two
            distance_ultrasound_two = readUltraSoundSensor(TRIG_TWO, ECHO_TWO)
            print("Distance Ultrasound Two: ", distance_ultrasound_two," cm")
            if(distance_ultrasound_two - distance_ultrasound_two_prev > 2):
                productos[1].cantidad -= 1
            if((distance_ultrasound_two_initial - 1 < distance_ultrasound_two) and  (distance_ultrasound_two < distance_ultrasound_two_initial +1) and (productos[1].cantidad < 2)):
                productos[1].cantidad = 0
                email_string = "Hola!\n\nSmart Shelf le avisa que la " + productos[1].nombre + " esta agotada.\n\nGracias por ser parte de nosotros"
                sendAlert(email_string, 1)
            distance_ultrasound_two_prev = distance_ultrasound_two

            # Read ultrasound sensor three
            distance_ultrasound_three = readUltraSoundSensor(TRIG_THREE, ECHO_THREE)
            print("Distance Ultrasound Three: ", distance_ultrasound_three," cm")
            if(distance_ultrasound_three - distance_ultrasound_three_prev > 2):
                productos[2].cantidad -= 1
            if((distance_ultrasound_three_initial - 1 < distance_ultrasound_three) and  (distance_ultrasound_three < distance_ultrasound_three_initial +1) and (productos[2].cantidad < 2)):
                productos[2].cantidad = 0
                email_string = "Hola!\n\nSmart Shelf le avisa que la " + productos[2].nombre + " esta agotada.\n\nGracias por ser parte de nosotros"
                sendAlert(email_string, 1)
            distance_ultrasound_three_prev = distance_ultrasound_three

    except (KeyboardInterrupt):
        break