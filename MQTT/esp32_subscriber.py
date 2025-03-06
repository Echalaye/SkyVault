import network
import time
from umqtt.simple import MQTTClient
from machine import Pin

# Configuration WiFi
ssid = "VOTRE_SSID"
password = "VOTRE_MOT_DE_PASSE"

# Configuration MQTT
mqtt_server = "ADRESSE_IP_DE_VOTRE_MACHINE"  # Remplacez par l'IP de votre machine hôte
mqtt_port = 1883
mqtt_client_id = "ESP32_Subscriber"
mqtt_topic = b"esp32/data"  # Sujet auquel s'abonner

# Configuration de la LED
led_pin = 2  # LED intégrée de l'ESP32
led = Pin(led_pin, Pin.OUT)

# Fonction de rappel pour les messages MQTT reçus
def mqtt_callback(topic, msg):
    print(f"Message reçu [{topic.decode()}] {msg.decode()}")
    
    # Exemple: allumer/éteindre la LED selon le message
    if msg == b"ON":
        led.value(1)
        print("LED allumée")
    elif msg == b"OFF":
        led.value(0)
        print("LED éteinte")

# Fonction pour se connecter au WiFi
def setup_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print(f"Connexion à {ssid}")
    
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        
        # Attendre la connexion
        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")
    
    print("")
    print("WiFi connecté")
    print("Adresse IP:", wlan.ifconfig()[0])
    
    return wlan

# Fonction pour se connecter au broker MQTT
def connect_mqtt():
    client = MQTTClient(mqtt_client_id, mqtt_server, mqtt_port)
    client.set_callback(mqtt_callback)
    
    try:
        client.connect()
        print("Connecté au broker MQTT")
        
        # S'abonner au sujet
        client.subscribe(mqtt_topic)
        print(f"Abonné au sujet: {mqtt_topic.decode()}")
    except Exception as e:
        print(f"Échec de connexion MQTT: {e}")
        time.sleep(5)
        machine.reset()  # Redémarrer en cas d'échec
        
    return client

# Configuration initiale
def setup():
    # Connexion WiFi
    wlan = setup_wifi()
    
    # Connexion MQTT
    client = connect_mqtt()
    
    return wlan, client

# Boucle principale
def main():
    # Configuration
    wlan, client = setup()
    
    try:
        while True:
            # Vérifier les messages MQTT
            client.check_msg()
            
            # Autres tâches périodiques si nécessaire
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Erreur: {e}")
        client.disconnect()

if __name__ == "__main__":
    main() 