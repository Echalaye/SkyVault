import network
import time
import umqtt.simple as MQTT
import machine
import sys
from machine import Pin, PWM
from time import sleep
from esp32_gpio_lcd import GpioLcd

contrast_pin = PWM(Pin(2))

# Configurer la fréquence et la résolution du signal PWM
contrast_pin.freq(5000)  # 5 kHz
contrast_pin.duty_u16(32768)

# Configuration LCD
rs_pin = Pin(19, Pin.OUT)
enable_pin = Pin(23, Pin.OUT)
d4_pin = Pin(18, Pin.OUT)
d5_pin = Pin(17, Pin.OUT)
d6_pin = Pin(16, Pin.OUT)
d7_pin = Pin(15, Pin.OUT)

# LCD dimensions
LCD_ROWS = 2
LCD_COLS = 16

# Initialize LCD
lcd = GpioLcd(rs_pin=rs_pin, enable_pin=enable_pin,
              d4_pin=d4_pin, d5_pin=d5_pin,
              d6_pin=d6_pin, d7_pin=d7_pin,
              num_lines=LCD_ROWS, num_columns=LCD_COLS)

# Configuration WiFi
# Configuration du WiFi
WifiHosts = [
    {
        'SSID': "A15 de Etienne",
        'PASSWORD': "lustucrU"
    },
    {
        'SSID': "iPhone de Nathoo",
        'PASSWORD': "RERT2070"
        }
]

# Configuration MQTT
mqtt_server = "skyvault.local"  # Remplacez par l'IP de votre broker MQTT
mqtt_port = 1883
mqtt_client_id = "ESP32_Subscriber"
mqtt_topic = b"data/humidity"
mqtt = MQTT.MQTTClient(mqtt_client_id, mqtt_server, mqtt_port, keepalive=30)


led = Pin(2, Pin.OUT)


# Connexion au WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    connected = False

    # Essayer de se connecter à chaque hôte WiFi
    for host in WifiHosts:
        SSID = host['SSID']
        PASSWORD = host['PASSWORD']

        # Déconnecter d'abord si déjà connecté
        if wlan.isconnected():
            wlan.disconnect()
            time.sleep(1)

        wlan.connect(SSID, PASSWORD)

        max_wait = 15  # Timeout de 15 secondes
        while max_wait > 0 and not wlan.isconnected():
            max_wait -= 1
            time.sleep(1)

        # Vérifier si la connexion a réussi
        if wlan.isconnected():
            connected = True
            break  # Sortir de la boucle si connecté
    
    if not connected:
        # Clignoter 2 fois (long) si la connexion échoue
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(0.1)
        led.on()
        time.sleep(1)
        led.off()
        sys.exit()
    return wlan

# Fonction de rappel pour les messages MQTT reçus
def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    msg_str = msg.decode()
    lcd.clear()
    contrast_pin.duty_u16(32768)
    # Afficher le topic et le message sur le LCD
    lcd.putstr(f"{topic_str.split('/')[-1]}: {msg_str}")
    if int(msg_str) > 50:
        lcd.move_to(0, 1)
        lcd.putstr(f"Alert !")

# Fonction pour se connecter au broker MQTT
def connect_to_mqtt_broker():
    # Définir la fonction de rappel
    mqtt.set_callback(mqtt_callback)
    try:
        mqtt.connect()        
        # S'abonner au sujet
        mqtt.subscribe(mqtt_topic)
        
    except Exception as e:
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(0,1)
        led.on()
        time.sleep(1)
        led.off()
        sys.exit()
    return mqtt



# Exécution
connect_wifi()
mqtt_client = connect_to_mqtt_broker()
while True:
    mqtt_client.check_msg()
    time.sleep(1)