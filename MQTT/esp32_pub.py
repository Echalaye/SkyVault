from machine import Pin, ADC
import network
import dht
import time
import umqtt.simple as MQTT
import sys
import webrepl
import urequests

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
mqtt_topics = {
    "humidity": b"data/humidity",
    "gas": b"data/gas"
}
mqtt = MQTT.MQTTClient(mqtt_client_id, mqtt_server, mqtt_port, keepalive=30)

# Configuration Pushover
PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"
PUSHOVER_USER_KEY = "ujjexh4xz6zntxf2up9v8hedqxr2ch"  # Remplacez par votre clé utilisateur Pushover
PUSHOVER_API_TOKEN = "ajqsdqge6g3ve8vojsiwv4h376pbsa"  # Remplacez par votre token d'API Pushover
# Seuils d'alerte
HUMIDITY_THRESHOLD = 50
GAS_THRESHOLD = 2000
# Variables pour éviter les notifications répétées
last_humidity_alert = 0  # Timestamp de la dernière alerte
alert_cooldown = 300     # 5 minutes entre les alertes

# Initialisation des capteurs
sensor_dht = dht.DHT11(Pin(32))
sensor_gas = ADC(Pin(34))  # GPIO34 pour le capteur MQ2
sensor_gas.atten(ADC.ATTN_11DB)  # Configuration pour une plage de 0-3.3V

led = Pin(2, Pin.OUT)

# Connexion au WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.ifconfig(('192.168.234.96','255.255.255.0','192.168.234.1','8.8.8.8'))
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

def send_pushover_notification(title, message, priority=0):
    """
    Envoie une notification via Pushover
    
    Args:
        title: Titre de la notification
        message: Contenu de la notification
        priority: Priorité (-2 à 2, 0 par défaut)
    """
    try:
        data = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "title": title,
            "message": message,
            "priority": priority
        }
        
        response = urequests.post(PUSHOVER_API_URL, json=data)
        print(f"Notification envoyée, réponse: {response.text}")
        response.close()
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de la notification: {e}")
        return False

def read_sensors():
    global last_humidity_alert
    
    while True:
        try:
            current_time = time.time()
            
            # Lecture du capteur d'humidité
            sensor_dht.measure()
            humidity = sensor_dht.humidity()
            mqtt.publish(mqtt_topics["humidity"], str(humidity).encode())
            print(f"Humidité: {humidity}%")

            # Si l'humidité dépasse le seuil et qu'on n'a pas envoyé d'alerte récemment
            if humidity > HUMIDITY_THRESHOLD and (current_time - last_humidity_alert) > alert_cooldown:
                notification_title = "Alerte Humidité"
                notification_message = f"Le taux d'humidité est de {humidity}% (seuil: {HUMIDITY_THRESHOLD}%)"
                
                # Envoi de la notification avec une priorité haute (1)
                if send_pushover_notification(notification_title, notification_message, 1):
                    last_humidity_alert = current_time
                    print("Alerte humidité envoyée")

            # Lecture du capteur de gaz
            gas_value = sensor_gas.read()
            mqtt.publish(mqtt_topics["gas"], str(gas_value).encode())
            print(f"Gaz: {gas_value}")
            
            # Alerte si le niveau de gaz est trop élevé
            if gas_value > GAS_THRESHOLD:
                notification_title = "Alerte Gaz"
                notification_message = f"Niveau de gaz élevé: {gas_value} (seuil: {GAS_THRESHOLD})"
                
                # Envoi de la notification avec une priorité d'urgence (2)
                send_pushover_notification(notification_title, notification_message, 2)
                print("Alerte gaz envoyée")

        except Exception as e:
            print(f"Erreur: {e}")
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(0.1)
            led.on()
            time.sleep(1)
            led.off()
        time.sleep(2)

# Exécution
connect_wifi()
webrepl.start()
connect_to_mqtt_broker()
read_sensors()

