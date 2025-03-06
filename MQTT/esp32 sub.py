import network
import time
from umqtt.simple import MQTTClient
import machine
import sys

# Configuration WiFi
ssid = "iPhone de Nathoo"
password = "RERT2070"

# Configuration MQTT
mqtt_server = "skyvault.local"  # Remplacez par l'IP de votre broker MQTT
mqtt_port = 1883
mqtt_client_id = "ESP32_Subscriber"
mqtt_topic = b"data/humidty"

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
    time.sleep(0.1)