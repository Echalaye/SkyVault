from machine import Pin, ADC
import network
import dht
import time
import umqtt.simple as MQTT
import sys
import webrepl
import gc
import machine
import urequests

# Configuration du WiFi
WifiHosts = [
    {
        'SSID': "A15 de Etienne",
        'PASSWORD': "lustucrU"
    },
    {
        'SSID': "iPhone de Nathoo",
        'PASSWORD': "N397b7nh"
    }
]

# Configuration MQTT
mqtt_server = "skyvault.local"
mqtt_port = 1883
mqtt_client_id = "ESP32_Publisher"
mqtt_topics = {
    "humidity": b"sensors/humidity",
    "gas": b"sensors/gas",
    "data": b"data/KPI"
}
mqtt = None  # On l'initialisera à la connexion

# Initialisation des capteurs
sensor_dht = dht.DHT11(Pin(32))
sensor_gas = ADC(Pin(34))  # GPIO34 pour le capteur MQ2
sensor_gas.atten(ADC.ATTN_11DB)  # Configuration pour une plage de 0-3.3V

led = Pin(2, Pin.OUT)

# Configuration Pushover
PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"
PUSHOVER_USER_KEY = "ujjexh4xz6zntxf2up9v8hedqxr2ch"
PUSHOVER_API_TOKEN = "ajqsdqge6g3ve8vojsiwv4h376pbsa"
# Seuils d'alerte
HUMIDITY_THRESHOLD = 60
GAS_THRESHOLD = 200
# Variables pour éviter les notifications répétées
last_humidity_alert = 0  # Timestamp de la dernière alerte
alert_cooldown = 300     # 5 minutes entre les alertes

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

        try:
            print(f"\nTentative connexion à {SSID}...")
            wlan.connect(SSID, PASSWORD)

            max_wait = 15  # Timeout de 15 secondes
            while max_wait > 0 and not wlan.isconnected():
                max_wait -= 1
                print(".", end="")
                time.sleep(1)

            # Vérifier si la connexion a réussi
            if wlan.isconnected():
                connected = True
                print(f"Connecté à {SSID}")
                print(f"Adresse IP: {wlan.ifconfig()[0]}")
                break  # Sortir de la boucle si connecté
        except Exception as e:
            print(f"Erreur de connexion à {SSID}: {e}")
    
    if not connected:
        print(f"Échec de connexion à tous les réseaux WiFi")
        # Clignoter 2 fois (long) si la connexion échoue
        for _ in range(2):
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(0.5)
        return None
    return wlan

def connect_to_mqtt_broker():
    global mqtt
    try:
        print(f"Connexion au broker MQTT {mqtt_server}:{mqtt_port}...")
        mqtt = MQTT.MQTTClient(mqtt_client_id, mqtt_server, mqtt_port)
        mqtt.connect()
        print("Connecté au broker MQTT")
        return True
    except Exception as e:
        print(f"Erreur de connexion MQTT: {e}")
        # Clignoter 3 fois pour erreur MQTT
        for _ in range(3):
            led.on()
            time.sleep(0.5)
            led.off()
            time.sleep(0.5)
        return False

def get_system_stats():
    try:
        return {
            "free_ram": gc.mem_free(),
            "cpu_freq": machine.freq(),
            "uptime": time.ticks_ms()
        }
    except Exception as e:
        print(f"Erreur lors de la récupération des stats: {e}")
        return {
            "free_ram": 0,
            "cpu_freq": 0,
            "uptime": 0
        }

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

def calcul_ppm(val_adc):
    try:
        if val_adc < 500:
            return 0
        elif 500 <= val_adc < 1000:
            return round(((val_adc - 500) / 500) * 50, 1)
        elif 1000 <= val_adc < 1500:
            return round(50 + ((val_adc - 1000) / 500) * 150, 1)
        else:
            return 201  # valeur au-dessus du seuil
    except Exception as e:
        print(f"Erreur calcul PPM: {e}")
        return -1

def read_sensors():
    global last_humidity_alert
    
    while True:
        try:
            # Lecture du capteur d'humidité
            sensor_dht.measure()
            humidity = sensor_dht.humidity()
            print(f"Humidité: {humidity}%")
            
            try:
                if mqtt:
                    mqtt.publish(mqtt_topics["humidity"], str(humidity).encode())
            except Exception as mqtt_err:
                print(f"Erreur envoi MQTT humidité: {mqtt_err}")

            # Si l'humidité dépasse le seuil et qu'on n'a pas envoyé d'alerte récemment
            current_time = time.time()
            if humidity > HUMIDITY_THRESHOLD and (current_time - last_humidity_alert > alert_cooldown):
                notification_title = "Alerte Humidité"
                notification_message = f"Le taux d'humidité est de {humidity}% (seuil: {HUMIDITY_THRESHOLD}%)"
                
                # Envoi de la notification avec une priorité haute (1)
                if send_pushover_notification(notification_title, notification_message, 1):
                    last_humidity_alert = current_time
                    print("Alerte humidité envoyée")

            # Lecture du capteur de gaz
            gas_value = sensor_gas.read()
            ppm = calcul_ppm(gas_value)  # Calcul du ppm
            print(f"Gaz: {gas_value} | Estimation propane : {ppm} ppm")
            
            try:
                if mqtt:
                    mqtt.publish(mqtt_topics["gas"], str(ppm).encode())
            except Exception as mqtt_err:
                print(f"Erreur envoi MQTT gaz: {mqtt_err}")
            
            # Alerte si le niveau de gaz est trop élevé
            if ppm > GAS_THRESHOLD:
                notification_title = "Alerte Gaz"
                notification_message = f"Niveau de gaz élevé: {ppm} (seuil: {GAS_THRESHOLD})"
                
                # Envoi de la notification avec une priorité d'urgence (2)
                send_pushover_notification(notification_title, notification_message, 2)
                print("Alerte gaz envoyée")
            
            # Envoi des données système
            try:
                stats = get_system_stats()
                kpi_data = f"{stats['free_ram']},{stats['cpu_freq']},{stats['uptime']}"
                print(f"Stats: {kpi_data}")
                
                if mqtt:
                    mqtt.publish(mqtt_topics["data"], kpi_data.encode())
            except Exception as stats_err:
                print(f"Erreur envoi stats: {stats_err}")

            # Clignoter brièvement pour signaler le bon fonctionnement
            led.on()
            time.sleep(0.1)
            led.off()

        except Exception as e:
            print(f"Erreur lecture capteurs: {e}")
            # Signaler l'erreur
            for _ in range(2):
                led.on()
                time.sleep(0.2)
                led.off()
                time.sleep(0.2)
        
        # Attendre avant la prochaine lecture
        time.sleep(2)

def main():
    try:
        # Connexion WiFi
        wlan = connect_wifi()
        if not wlan:
            print("Impossible de continuer sans connexion WiFi")
            return
            
        # Connexion MQTT
        print('Connexion MQTT')
        if not connect_to_mqtt_broker():
            print("Impossible de continuer sans connexion MQTT")
            return
            
        # Lecture des capteurs
        print("Démarrage lecture des capteurs")
        read_sensors()
    except Exception as e:
        print(f"Erreur principale: {e}")
        # Signaler l'erreur grave
        for _ in range(5):
            led.on()
            time.sleep(0.1)
            led.off()
            time.sleep(0.1)

# N'exécute pas automatiquement - sera appelé manuellement
if __name__ == "__main__":
    main()
