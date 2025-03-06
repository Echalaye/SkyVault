from machine import Pin
import network
import dht
import time
import umqtt.simple as MQTT

# Configuration du WiFi
SSID = "iPhone de Nathoo"
PASSWORD = "RERT2070"
mqtt_topic = "data/humidty"

# Connexion au WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("\nConnexion en cours...")
    
    while not wlan.isconnected():
        print("Non connecté au Wifi, nouvelle tentative...\n", end="")
        time.sleep(0.5)
    
    print("\nConnecté au réseau WiFi")
    print("Adresse IP:", wlan.ifconfig()[0])
    
    
mqtt = MQTT.MQTTClient("esp32", "skyvault.local", 1883, user="esp32-pub", password="pub-pswd")
def connect_to_mqtt_broker():
    #print("Connecting to MQTT broker")
    try:
        mqtt.connect()
        print("I'm connected to the MQTT server Bitch!!!")
    except MQTT.MQTTException as e:
        print("An MQTT error occured while trying to connect to the MQTT broker")
        print("Note: Check your connection parameters")
        print("Context:", e)
        mqtt.reset()
        
    except Exception as e:
        print("An unknown error occured while trying to connect to the MQTT broker")
        print("Note: the connection most probably timed out")
        print("Context:", e)
        mqtt.reset()


# Initialisation du capteur DHT11
sensor = dht.DHT11(Pin(32))

def read_sensor():
    while True:
        try:
            sensor.measure()
            humidity = sensor.humidity()
            mqtt.publish(mqtt_topic, str(humidity).encode())
            print(f"Humidité : {humidity} %")
        except Exception as e:
            print("Erreur de lecture du capteur:", e)
        time.sleep(2)


# Exécution
connect_wifi()
connect_to_mqtt_broker()
read_sensor()
