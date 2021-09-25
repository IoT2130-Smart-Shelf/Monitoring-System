from datetime import date
from datetime import datetime
from picamera import PiCamera
import threading
from picamera import PiCamera
import os

import paramiko
"""
    Para la instalación de paramiko usar pip3 install paramiko
    Upload file, can not upload directory.
    :param host: sftp server host name or ip.
    :param port: sftp server listening port nubmer.
    :param user: sftp user name
    :param password: sftp account password
    :param server_path: remote server file path，for example：/root/test/test.txt
    :param local_path: local file path (c:/test.txt)
    :param timeout: upload connection timeout number ( an integer value, default is 10 )
    :return: bool
"""
def sftp_upload_file(host, port, user, password, server_path, local_path, timeout=10):
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
    
#sftp_upload_file('192.168.20.61',22,'pi','carolina','/home/pi/Desktop/image/ImagesCamera.jpg','/home/pi/Desktop/image.jpg')


camera = PiCamera()
camera.rotation = 180

def currentTime():
    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")
    print("Current Time =", current_time)
    return current_time

def currentDate():
    today = date.today()
    d1 = today.strftime("%d_%m_%Y")
    print("d1 =", d1)
    return d1

def printit():
  threading.Timer(5, printit).start()
  time = currentTime()
  date = currentDate()
  camera.capture('/home/pi/Desktop/ImagenesEstante/EstanteDD'+str(date)+'HH'+str(time)+'.jpg')
  sftp_upload_file('192.168.20.61',22,'pi','carolina',
                   '/home/pi/Desktop/ImagesCamera/EstanteDD'+str(date)+'HH'+str(time)+'.jpg',
                   '/home/pi/Desktop/ImagenesEstante/EstanteDD'+str(date)+'HH'+str(time)+'.jpg')
  os.remove('/home/pi/Desktop/ImagenesEstante/EstanteDD'+str(date)+'HH'+str(time)+'.jpg')
  print("Imagen enviada al nodo")

camera.capture('/home/pi/Desktop/ImagenesEstante/estante.jpg')
os.remove('/home/pi/Desktop/ImagenesEstante/estante.jpg')
printit()

