# Sistema de monitoreo
Sistema de monitoreo para el control de los productos de una estantería para etiquetado electrónico.

## Construido con  🛠️
* [Python 3] - The programming language used

## Autores ✒️
**Grupo I**<br />
**Juan Sebastian Barreto Jiménez** - *Equipo principal* - [jsebastianbarretoj99](https://github.com/jsebastianbarretoj99)<br />
**Carolina María Burgos Anillo** - *Equipo principal* - [cmba-alt ](https://github.com/cmba-alt)<br />
**Edwin Alejandro Caidedo Palacios** - *Equipo principal* - [Edwin99pal](https://github.com/Edwin99pal)<br />

## Proyecto: Smart Shelf 
Smart Shelf es un sistema de control y monitoreo de estanterías en tiendas como supermercados y minimercados. Smart Shelf implementa etiquetas de precio electrónicas donde se encuentran el precio y la información de los productos. Se implementa un monitoreo de los estantes utilizando cámaras y sensores de distancia con tecnologías de ultrasonido y láser, con esta información notificará cuando sea necesario reaprovisionar los productos en una estantería específica o cuando un producto esté ubicado en el estante incorrecto. Por medio de un sitio web, la persona encargada de la tienda puede actualizar la información de las etiquetas de manera remota. Se puede consultar también tendencias de precios e información sobre los productos que se agotan con mayor frecuencia en las estanterías, teniendo en cuenta los días y las horas en las que los clientes los retiran.

### Arquitectura de alto nivel
![alt arquitetura](images/highlevel.gif)

## Implementación

El sistema de monitoreo se compone de dos partes principales: un arreglo de sensores para llevar el conteo de productos en el estante y una cámara para detectar productos mal ubicados. El arreglo de sensores viene acompañado de las pantallas Nextion para colocar la información de las etiquetas, todo esto conectado a una Raspberry Pi 3B+
El funcionamiento de la cámara se implementó con un módulo de cámara conectado a una Raspberry Pi 4, en la cual se corre un modelo de detección de objetos.

## Instrucciones de uso
Para la Raspberry Pi 3B+ se necesita instalar dependencias en Python:

`python3 -m pip install paho-mqtt`
`python3 -m pip install adafruit-circuitpython-vl53l0x`

Para el detector de objetos, se siguieron las instrucciones del [repositorio de EdjeElectronics](https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi) para utilizar la API de detección de objetos de Tensorflow. Se entrenó un detector según se indica en [otro repositorio](https://github.com/EdjeElectronics/TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10) parte de esta serie de tutoriales, con imágenes de los productos utilizados en el prototipo. Los archivos necesarios para utilizar el detector entrenado para el prototipo se encuentran en [este enlace](https://www.dropbox.com/sh/scf9e9j9fpet1ys/AAAKz_HdsfjLn25Vv2Q1a90la?dl=0)


