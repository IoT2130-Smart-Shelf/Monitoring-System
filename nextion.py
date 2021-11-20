#import module: install with 'easy_install -U pyserial'
import serial
import RPi.GPIO as GPIO

# Initialize numeric pins for SELECT sensors
SELECT_A = 16
SELECT_B = 20

GPIO.setmode(GPIO.BCM)

GPIO.setup(SELECT_A, GPIO.OUT)
GPIO.setup(SELECT_B, GPIO.OUT)

#Set end of file
eof = b'\xff\xff\xff'

#setup connection
con = serial.Serial(

    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
)

dato="Coke"
#SELECT Y0
GPIO.output(SELECT_A, GPIO.LOW)
GPIO.output(SELECT_B, GPIO.LOW)

#SELECT Y1
GPIO.output(SELECT_A, GPIO.HIGH)
GPIO.output(SELECT_B, GPIO.LOW)

#SELECT Y2
GPIO.output(SELECT_A, GPIO.LOW)
GPIO.output(SELECT_B, GPIO.HIGH)
#write text to Page 0 t0 txt variable(check the id of your text box) plus EOF
con.write(b't0.txt="' + str(dato).encode() + b'"\xFF\xFF\xFF')