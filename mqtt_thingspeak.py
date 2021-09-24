from __future__ import print_function
import paho.mqtt.publish as publish

channelID = "1481979" # Channel ID of ThingSpeak

writeApiKey = "R6KP5RUYDZOS6XKO" # Write API Key of ThingSpeak

useUnsecuredTCP = False

useUnsecuredWebsockets = False

useSSLWebsockets = True

mqttHost = "mqtt.thingspeak.com"

if useUnsecuredTCP:
    tTransport = "tcp"
    tPort = 1883
    tTLS = None

if useUnsecuredWebsockets:
    tTransport = "websockets"
    tPort = 80
    tTLS = None

if useSSLWebsockets:
    import ssl
    tTransport = "websockets"
    tTLS = {'ca_certs':"/etc/ssl/certs/ca-certificates.crt",'tls_version':ssl.PROTOCOL_TLSv1}
    tPort = 443

topic = "channels/" + channelID + "/publish/" + writeApiKey

distanceSound = 300
distanceLaser = 100
print (" Distance Sound =", distanceSound, "   Distance Laser =", distanceLaser)

# build the payload string
tPayload = "field1=" + str(distanceSound) + "&field2=" + str(distanceLaser)
# attempt to publish this data to the topic
try:
    publish.single(topic, payload=tPayload, hostname=mqttHost, port=tPort, tls=tTLS, transport=tTransport)
except (KeyboardInterrupt):
    #break
    pass
except (Exception):
    print ("There was an error while publishing the data.")