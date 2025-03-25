from machine import Pin
import network
import dht
import time
import umqtt.simple as MQTT
import sys

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
mqtt_server = "skyvault.local"
mqtt_port = 1883
mqtt_client_id = "ESP32_Publisher"
mqtt_topic = b"data/humidity"
mqtt = MQTT.MQTTClient(mqtt_client_id, mqtt_server, mqtt_port, keepalive=30)

# Initialisation du capteur DHT11
sensor = dht.DHT11(Pin(32))

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
            print(".", end="")
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


def connect_to_mqtt_broker():
    try:
        mqtt.connect()        
    except Exception as e:
        led.on()
        time.sleep(1)
        led.off()
        time.sleep(0.1)
        led.on()
        time.sleep(1)
        led.off()
        sys.exit()


def read_humidity_sensor():
    while True:
        try:
            sensor.measure()
            humidity = sensor.humidity()
            mqtt.publish(mqtt_topic, str(humidity).encode())
        except Exception as e:
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(0,1)
            led.on()
            time.sleep(1)
            led.off()
        time.sleep(2)


# Exécution
connect_wifi()
connect_to_mqtt_broker()
read_humidity_sensor()
