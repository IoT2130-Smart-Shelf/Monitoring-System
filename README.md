# Sistema de monitoreo
Sistema de monitoreo para el control de los productos de una estantería para etiquetado electrónico.

## Construido con  🛠️
* [Python 3] - The programming language used

## Autores ✒️
**Grupo I**<br />
**Juan Sebastian Barreto Jiménez** - *Equipo principal* - [jsebastianbarretoj99](https://github.com/jsebastianbarretoj99)<br />
**Carolina María Burgos Anillo** - *Equipo principal* - [cmba-alt ](https://github.com/cmba-alt)<br />
**Edwin Alejandro Caidedo Palacios** - *Equipo principal* - [Edwin99pal](https://github.com/Edwin99pal)<br />

## Instrucciones de uso
To use it you need to install dependencies in python:<br />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;paramiko <br />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;paho-mqtt <br />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;adafruit-circuitpython-vl53l0x <br />
<br />
Commands to install dependencies:<br />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;paramiko: python3 -m pip install paramiko<br />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;paho-mqtt: python3 -m pip install paho-mqtt<br />
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;adafruit-circuitpython-vl53l0x: python3 -m pip install adafruit-circuitpython-vl53l0x

## Proyecto: Smart shelf 
Smart Shelf es un sistema de control y monitoreo de estanterías en tiendas como supermercados y minimercados. Smart Shelf implementa etiquetas de precio electrónicas donde se encuentran el precio y un código QR para que los clientes consulten información de los productos. Se implementará un monitoreo de los estantes utilizando cámaras y sensores de distancia con tecnologías de ultrasonido y láser, con esta información notificará cuando sea necesario reaprovisionar los productos en una estantería específica o cuando un producto esté ubicado en el estante incorrecto. Por medio de un sitio web, la persona encargada de la tienda puede actualizar la información de las etiquetas de manera remota y podrá verificar si hacen falta productos, además de consultar información sobre todos los productos. Se puede consultar también tendencias de precios e información sobre los productos que se agotan con mayor frecuencia en las estanterías, teniendo en cuenta los días y las horas en las que los clientes los retiran.

### Arquitectura de alto nivel
![alt arquitetura](images/highlevel.gif)

### Diagrama de bloques
![alt diagrama](images/diagrama_bloques.jpg)
