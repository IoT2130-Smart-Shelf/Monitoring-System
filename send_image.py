# -*- coding: utf-8 -*-
"""
Created on Sun Sep 26 19:40:26 2021
    Script para realizar el envio iterado de fotografias entre dos tarjetas raspberry cada cierto tiempo
    haciendo uso del protocolo SSHv2 para el envio de archivos de forma segura.

@author: edwin
"""

from datetime import date
from datetime import datetime
from picamera import PiCamera
import threading                # modulo para implementacion de temporizadores
from picamera import PiCamera   # modulo para el manejo de la camara raspberry
import os                       # modulo para el borrado de archivos
import paramiko    # libreria para poder utilizar el protocolo SSHv2 entre las raspbrerys


def sftp_upload_file(host, port, user, password, server_path, local_path, timeout=10):
    '''
    Parameters
    ----------
    host : TYPE
         sftp server host name or ip.
    port : TYPE
        sftp server listening port nubmer.
    user : TYPE
        sftp user name.
    password : TYPE
        sftp account password.
    server_path : TYPE
        remote server file path，for example：/root/test/test.txt
    local_path : TYPE
        local file path (c:/test.txt).
    timeout : TYPE, optional
        upload connection timeout number ( an integer value, default is 10 ).
        
    Returns
    -------
    bool
        True for correct send, False for incorret send.

    '''
    try:
        # create transport object.
        t = paramiko.Transport((host, port))
        
        # set connection timeout number.
        t.banner_timeout = timeout
        
        # connect to remote sftp server
        t.connect(username=user, password=password)
        
        # get the SFTP client object.
        sftp = paramiko.SFTPClient.from_transport(t)
        
        # upload local file to remote server path.
        sftp.put(local_path, server_path)
        # close the connection.
        t.close()
        return True
    except Exception as e:
        print(e)
        return False

camera = PiCamera()
camera.rotation = 180   # rotacion de la imagen tomada

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
    print("Current Time =", current_time)
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
    print("d1 =", d1)
    return d1

def printit():
    '''
    Inicializa un timer y envia la imagen de una raspberry a otra por SSH cuando el timer se cumple

    Returns
    -------
    None.

    '''
    threading.Timer(5, printit).start()    # se inicializa el timer
    time = currentTime()                   # Genero el texto de la hora
    date = currentDate()                   # Genero el texto de la fecha
    # Se realiza la captura de la imagen
    camera.capture('/home/pi/Desktop/ImagenesEstante/EstanteDD'+str(date)+'HH'+str(time)+'.jpg')
    # Se realiza la transferencia del archivo por SSH
    sftp_upload_file('192.168.20.61',22,'pi','carolina',
                       '/home/pi/Desktop/ImagesCamera/EstanteDD'+str(date)+'HH'+str(time)+'.jpg',
                       '/home/pi/Desktop/ImagenesEstante/EstanteDD'+str(date)+'HH'+str(time)+'.jpg')
    # Se elimina el archivo luego del envio
    os.remove('/home/pi/Desktop/ImagenesEstante/EstanteDD'+str(date)+'HH'+str(time)+'.jpg')
    print("Imagen enviada al nodo")

camera.capture('/home/pi/Desktop/ImagenesEstante/estante.jpg')
os.remove('/home/pi/Desktop/ImagenesEstante/estante.jpg')
printit()   # se ejecuta iteradamente el temporizador
