import network
import time
from umqtt.simple import MQTTClient
import machine
import sys
from machine import Pin
from time import sleep
from esp32_gpio_lcd import GpioLcd

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
ssid = "A15 de Etienne"
password = "lustucrU"

# Configuration MQTT
mqtt_server = "skyvault.local"  # Remplacez par l'IP de votre broker MQTT
mqtt_port = 1883
mqtt_client_id = "ESP32_Subscriber"
mqtt_topic = b"data/humidity"

# Fonction pour se connecter au WiFi
def connect_wifi():
    print("Connexion au réseau WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connexion à {ssid}...")
        wlan.connect(ssid, password)
        
        # Attendre la connexion avec timeout
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print(".", end="")
            time.sleep(1)
            
        if not wlan.isconnected():
            print("\nÉchec de connexion au WiFi. Redémarrage...")
            time.sleep(1)
            machine.reset()
    
    print("\nConnecté au WiFi!")
    print(f"Adresse IP: {wlan.ifconfig()[0]}")
    return wlan

# Fonction de rappel pour les messages MQTT reçus
def mqtt_callback(topic, msg):
    topic_str = topic.decode()
    msg_str = msg.decode()
    print(f"Message reçu sur le sujet [{topic_str}]: {msg_str}")
    lcd.clear()
    lcd.putstr(f"Humidity: {msg_str}")
    if int(msg_str) > 50:
        lcd.move_to(0, 1)
        lcd.putstr(f"Alerte !")

# Fonction pour se connecter au broker MQTT
def connect_to_mqtt_broker():
    print("Connexion au broker MQTT...")
    client = MQTTClient(mqtt_client_id, mqtt_server, mqtt_port, keepalive=30)
    
    # Définir la fonction de rappel
    client.set_callback(mqtt_callback)
    
    try:
        client.connect()
        print(f"Connecté au broker MQTT: {mqtt_server}")
        
        # S'abonner au sujet
        client.subscribe(mqtt_topic)
        print(f"Abonné au sujet: {mqtt_topic.decode()}")
        
    except Exception as e:
        print(f"Échec de connexion au broker MQTT: {e}")
        print("Redémarrage dans 5 secondes...")
        time.sleep(5)
        machine.reset()
    
    return client

# Fonction principale
connect_wifi()
# Connexion au broker MQTT
mqtt_client = connect_to_mqtt_broker()
print("En attente de messages...")
# Boucle principale
while True:
    # Vérifier les messages MQTT
    mqtt_client.check_msg()
    # Petite pause pour éviter de surcharger le CPU
    time.sleep(1)