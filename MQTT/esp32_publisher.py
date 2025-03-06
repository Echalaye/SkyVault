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
mqtt_client_id = "ESP32_Publisher"
mqtt_topic = b"esp32/data"  # Sujet sur lequel publier

# Configuration du bouton
button_pin = 0  # Bouton BOOT de l'ESP32
button = Pin(button_pin, Pin.IN, Pin.PULL_UP)
last_button_state = 1
last_debounce_time = 0
debounce_delay = 50

# Variable pour l'état de la LED
led_state = False

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
    
    try:
        client.connect()
        print("Connecté au broker MQTT")
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
    global last_button_state, last_debounce_time, led_state
    
    # Configuration
    wlan, client = setup()
    
    try:
        while True:
            # Lire l'état du bouton
            reading = button.value()
            
            # Vérifier si l'état du bouton a changé
            if reading != last_button_state:
                last_debounce_time = time.ticks_ms()
            
            # Si l'état est stable depuis suffisamment longtemps
            if time.ticks_diff(time.ticks_ms(), last_debounce_time) > debounce_delay:
                # Si le bouton est pressé (0 pour un bouton avec pull-up)
                if reading == 0:
                    # Alterner entre ON et OFF à chaque pression
                    led_state = not led_state
                    
                    # Publier le message
                    if led_state:
                        print("Publication du message: ON")
                        client.publish(mqtt_topic, b"ON")
                    else:
                        print("Publication du message: OFF")
                        client.publish(mqtt_topic, b"OFF")
            
            # Sauvegarder l'état du bouton
            last_button_state = reading
            
            # Délai pour éviter les rebonds
            time.sleep(0.01)
            
    except Exception as e:
        print(f"Erreur: {e}")
        client.disconnect()

if __name__ == "__main__":
    main() 