#import module: install with 'easy_install -U pyserial'
import serial

#Set end of file
eof = b'\xff\xff\xff'

#setup text for writing
txt = b'Hello world'

#setup connection
con = serial.Serial(

    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
)
#serm = str.encode(b't0.txt=\"Hello world\"')
dato="Hello world"
#write text to Page 0 t0 txt variable(check the id of your text box) plus EOF
con.write(b't0.txt="' + str(dato).encode() + b'"\xFF\xFF\xFF')