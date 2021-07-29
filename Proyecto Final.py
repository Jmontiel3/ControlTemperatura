## Librerias importadas de los dispositivos utilizados##

from machine import Pin,I2C,PWM
from ssd1306 import SSD1306_I2C
from dht import DHT11
import utime
import network, time, urequests
######################################################

## Datos de la pantalla Oled
ancho = 128
alto = 64
###################################

#Pines y variables que llegan a la ESP32
i2c = I2C(0, scl=Pin(22), sda=Pin(21))#Pines conexión pantalla oled
oled = SSD1306_I2C(ancho, alto, i2c)  #Pines conexión pantalla oled
sensorDHT = DHT11(Pin(15))            #Conexión del sensor DTH11
color1 = Pin(12, Pin.OUT)             #Conexión RGB
color2 = Pin(13, Pin.OUT)             #Conexión RGB
color3 = Pin(14, Pin.OUT)             #Conexión RGB
color4 = Pin(4, Pin.OUT)              #Led el cual nos genera la alerta
#############################################################################
 
#Definimos unas variables para el RGB
def leds (a,b,c):
      color1.value(a)
      color2.value(b)
      color3.value(c)
     
print (i2c.scan())
############################################################################ 

#Conexion Wi-Fi para tener acceso a nuestra Api y poder enviar información a la nube.
def conectaWifi (red, password):
      global miRed
      miRed = network.WLAN(network.STA_IF)     
      if not miRed.isconnected():              #Si no está conectado…
          miRed.active(True)                   #activa la interface
          miRed.connect('VELA', '1033745063')         #Intenta conectar con la red
          print('Conectando a la red', red +"…")
          timeout = time.time ()
          while not miRed.isconnected():           #Mientras no se conecte..
              if (time.ticks_diff (time.time (), timeout) > 10):
                  return False
    
      return True
    
sensorDHT = DHT11 (Pin(15)) #Pin sensor de temperatura

if conectaWifi ("VELA", "1033745063"):

    print ("Conexión exitosa!")
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())
      
    web = "https://maker.ifttt.com/trigger/sensor_dth/with/key/eSYBfrAQ8fUTI-jspxZGw?" # Conexión a API evento donde se lleva registro de temperatura
    url = "https://maker.ifttt.com/trigger/alarma/with/key/eSYBfrAQ8fUTI-jspxZGw?"     # Conexión a API evento que nos genera una alerta via correo
    
    while (True):
        time.sleep(1)
        sensorDHT.measure()
        temp = sensorDHT.temperature()
        hum = sensorDHT.humidity()
        
        print ("T={:02d} ºC, H={:02d} %".format (temp,hum))
                
        oled.text("T = {:02d}ºC".format(temp),0,0)
        oled.text("H = {:02d}%".format(hum),0,10)
        oled.show()
        oled.fill(0)
        time.sleep(0.03)
        
        respuesta = urequests.get(web+"&value1="+str(temp)+"&value2="+str(hum))
        respuesta.close ()
        time.sleep(0.05)

#En este apartado dependiendo la temperatura el RGB encendera en azul, verde o rojo#
        if temp > 26:
            leds(0,255,0)
        elif temp >= 22 and temp <= 25:
            leds(255,0,0)           
        elif temp < 22:
            leds(0,0,255)            
            
        time.sleep(0.5)
        
        if temp >= 27:   
            color4.value(1)            
            
            respuesta = urequests.get(url+"&value1="+str(temp)+"&value2="+str(hum))
            print(respuesta.text)
            print (respuesta.status_code)
            respuesta.close ()
        
        elif temp < 26:
            color4.value(0)
                       
else:
    print ("Imposible conectar")
    miRed.active (False)
    
#if _name==("_main_"):
    #main ()

