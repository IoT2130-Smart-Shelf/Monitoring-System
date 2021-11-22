# Import packages
import os
import cv2
import numpy as np
import tensorflow as tf
import argparse
import sys
import ssl, smtplib
from datetime import date
from datetime import datetime
import threading                # modulo para implementacion de temporizadores
from picamera import PiCamera   # modulo para el manejo de la camara raspberry
import os         
import dropbox
from utils import label_map_util
from utils import visualization_utils as vis_util
import re
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from firebase import firebase
import time
from time import sleep
import requests
import paho.mqtt.publish as publish

firebaseDB= firebase.FirebaseApplication("https://smart-shelf-44c69-default-rtdb.firebaseio.com/", None)
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
    
    def _str_(self):
        print("Producto", self.id)
        print("    Cantidad =", self.cantidad)
        print("    Fabricante =", self.fabricante)
        print("    Imagen =", self.imagen)
        print("    Nombre =", self.nombre)
        print("    Precio =", self.precio)
        print("    Tamano =", self.tamano)
        print("    UnidadMedida =", end=" ")
        return self.unidadMedida

#   Function: downloadDataDB() 
#   Purpose: Download data of productos from Firebase Realtime DB
#   Argument:
#       void
#   Return:
#       void
productos = []
def downloadDataDB():
    resultData = firebaseDB.get('/Tiendas/MaxiDespensa/Productos/', '')
    productos.clear()
    for data in resultData.values():
  
        producto = Producto(data)
        productos.append(producto)


def currentTime():
    '''
    Genera la estampa de tiempo de la hora de la toma de la imagen

    Returns
    -------
    current_time : String
        Hora_Minuto_Segundo.

    '''
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")
    #print("Current Time =", current_time)
    return current_time

def currentDate():
    '''
    Genera la estampa de tiempo del dia de la toma de la imagen

    Returns
    -------
    d1 : String
        Day_Month_year.

    '''
    today = date.today()
    d1 = today.strftime("%d_%m_%Y")
    #print("d1 =", d1)
    return d1

def printit():
    '''
    Inicializa un timer y envia la imagen de una raspberry a otra por SSH cuando el timer se cumple

    Returns
    -------
    None.

    '''
    camera = PiCamera()
    camera.rotation = 180   # rotacion de la imagen tomada
    # Se realiza la captura de la imagen
    img_path = '/home/pi/Desktop/ImagenesEstante/EstanteDD.jpg'
    camera.capture(img_path)
    os.remove(img_path)
    img_path = '/home/pi/Desktop/ImagenesEstante/EstanteDD.jpg'
    camera.capture(img_path)
    os.remove(img_path)

    time = currentTime()                   # Genero el texto de la hora
    date = currentDate()                   # Genero el texto de la fecha
    img_path = '/home/pi/Desktop/ImagenesEstante/EstanteDD'+str(date)+'HH'+str(time)+'.jpg'
    camera.capture(img_path)
    camera.close()

    return img_path, time, date


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

def sendFlag():
    tTransport = "websockets" # Protocol comunication
    tTLS = {'ca_certs':"/etc/ssl/certs/ca-certificates.crt",'tls_version':ssl.PROTOCOL_TLSv1} # Security for comunication by MQTT
    tPort = 443 # Port for MQTT
    channelID = "1579372" # Channel ID of ThingSpeak
    writeApiKey = "A444YRSEAZKLS3KB" # Write API Key of ThingSpeak
    mqttHost = "mqtt.thingspeak.com" # Host of ThingSpeak
    topic = "channels/" + channelID + "/publish/" + writeApiKey # Topic of MQTT for ThingSpeak

    # build the payload string
    tPayload = "field1=" + str(1)

    # attempt to publish this data to the topic
    try:
        publish.single(topic, payload=tPayload, hostname=mqttHost, port=tPort, tls=tTLS, transport=tTransport)
        return "bandera bajada"
    except (Exception):
        return "Hubo un error al publicar los datos."

def receiveFlag():
    URL_FLAG = "https://api.thingspeak.com/channels/1579372/fields/1.json?api_key=EKAFOKYZTBQ3DUKL&results=1"
    r = requests.get(url = URL_FLAG)
    data = r.json() # extracting data in json format
    return data['feeds'][0]['field1']

downloadDataDB()
URL = "https://api.thingspeak.com/update.json?api_key=75RJHS14YYDV4XEU&/json"
initial_time = time.perf_counter()

token = "/t/"
for prod in productos:
    message = str(prod.cantidad) + token + str(prod.fabricante) + token + str(prod.id) + token + str(prod.imagen) + token + str(prod.nombre) + token + str(prod.precio) + token + str(prod.tamano) + token + str(prod.unidadMedida)
    PARAMS = { "field1": message}
    # sending post request and saving the response as response object
    r = requests.post(url = URL, params = PARAMS)
    # extracting data in json format
    data = r.json()
    print(data)
    print("Record sent to ThingSpeak")
    sleep(20)
# api-endpoint
cap_time_init = time.perf_counter() 
while True:
    
    end_time = time.perf_counter()
    if(end_time-initial_time >40):
        initial_time = end_time
        flag_control = receiveFlag()

        if(flag_control == 2):
            downloadDataDB()
            token = "/t/"
            for prod in productos:
                message = str(prod.cantidad) + token + str(prod.fabricante) + token + str(prod.id) + token + str(prod.imagen) + token + str(prod.nombre) + token + str(prod.precio) + token + str(prod.tamano) + token + str(prod.unidadMedida)
                PARAMS = { "field1": message}
                # sending post request and saving the response as response object
                r = requests.post(url = URL, params = PARAMS)
                # extracting data in json format
                data = r.json()
                print(data)
                print("Record sent to ThingSpeak")
                sleep(20)
            sendFlag()
    
    #get product list
    downloadDataDB()
    prod_list = []
    for pr in productos:
        prod_list.append([pr.id,pr.nombre])

    prod_list= sorted(prod_list, key=lambda x: x[0])
    #print(prod_list)
    prod_list_new = []
    ind = 0
    for i in prod_list:
        prod_list_new.append(prod_list[ind][1])
        ind += 1

    for item in range(0,len(prod_list_new)):
        if 'Coca Cola Zero' in prod_list_new[item]:
            prod_list_new[item] = 'CocaColaZero400'
        if 'Margarita' in prod_list_new[item]:
            prod_list_new[item] = 'papasMarglimon'
        if 'Chocoramo' in prod_list_new[item]:
            prod_list_new[item] = 'chocoramo'
    #print(prod_list_new)


    # Name of the directory containing the object detection module we're using
    MODEL_NAME = 'shelf_model'
    #IMAGE_NAME = 'IMG_20211114_101438.jpg'
    # Grab path to current working directory
    CWD_PATH = os.getcwd()

    # Path to frozen detection graph .pb file, which contains the model that is used
    # for object detection.
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,'data','shelf_labelmap.pbtxt')

    imgpath, time_cap, date_cap = printit()
    # Path to image
    PATH_TO_IMAGE = imgpath #os.path.join(CWD_PATH,IMAGE_NAME)
    #PATH_TO_IMAGE = '/home/pi/Desktop/ImagenesEstante/EstanteDD21_11_2021HH13_29_04.jpg'
    # Number of classes the object detector can identify
    NUM_CLASSES = 3

    ## Load the label map.
    # Label maps map indices to category names, so that when the convolution
    # network predicts `5`, we know that this corresponds to `airplane`.
    # Here we use internal utility functions, but anything that returns a
    # dictionary mapping integers to appropriate string labels would be fine
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    # Load the Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        sess = tf.Session(graph=detection_graph)


    # Define input and output tensors (i.e. data) for the object detection classifier

    # Input tensor is the image
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Output tensors are the detection boxes, scores, and classes
    # Each box represents a part of the image where a particular object was detected
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represents level of confidence for each of the objects.
    # The score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

    # Number of objects detected
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')


    # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
    # i.e. a single-column array, where each item in the column has the pixel RGB value
    frame = cv2.imread(PATH_TO_IMAGE)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_expanded = np.expand_dims(frame_rgb, axis=0)
    os.remove(imgpath)
    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})

    # Draw the results of the detection (aka 'visulaize the results')
    image, bx_list = vis_util.visualize_boxes_and_labels_on_image_array(
        frame,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.40)

    cv2.putText(image, str(date_cap)+"_"+str(time_cap), (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4)
    
    cv2.imwrite('last_shelf.jpg',image)

    bx_list= sorted(bx_list, key=lambda x: x[0])

    bx_list_new = []
    ind = 0
    for i in bx_list:
        bx_list_new.append(bx_list[ind][1])
        ind += 1

    for item in range(0,len(bx_list_new)):
        if 'CocaColaZero400' in bx_list_new[item][0]:
            bx_list_new[item] = 'CocaColaZero400'
        if 'papasMarglimon' in bx_list_new[item][0]:
            bx_list_new[item] = 'papasMarglimon'
        if 'chocoramo' in bx_list_new[item][0]:
            bx_list_new[item] = 'chocoramo'

    #print(bx_list_new)
    try:
        if bx_list_new != prod_list_new:
            if bx_list_new[0] != prod_list_new[0]:
                p1 = "posicion 1"
            else:
                p1 = "-"
            if bx_list_new[1] != prod_list_new[1]:
                p2 = "posicion 2"
            else:
                p2 = "-"
            if bx_list_new[2] != prod_list_new[2]:
                p3 = "posicion 3"
            else:
                p3 = "-"
            msg = "Los productos se encuentran mal ubicados en el estante en las siguientes posiciones:"+"\n"+p1+"\n"+p2+"\n"+p3
            print(msg)
            sendAlert(msg, 2)
    except (Exception):
        pass


    dbx = dropbox.Dropbox('lTXzWAG-aj4AAAAAAAAAATZtcTgsjvv2ureUpiWDwE6WAxk_30Tz9yqGgVMKlePl')

    with open("last_shelf.jpg", "rb") as f:
        dbx.files_upload(f.read(), '/Smart Shelf/last_shelf.jpg', mute = True, mode=dropbox.files.WriteMode.overwrite)

    sleep(120)

'''
# All the results have been drawn on the frame, so it's time to display it.
cv2.imshow('Object detector', frame)

# Press any key to close the image
cv2.waitKey(0)

# Clean up
cv2.destroyAllWindows()
'''
