"""Monitoring System Smart Shelf

Members:
    - Juan Sebastián Barreto Jimenéz
    - Carolina María Burgos Anillo
    - Edwin Alejandro Caicedo Palacios
"""

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