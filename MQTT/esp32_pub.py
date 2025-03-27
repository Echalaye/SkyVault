from machine import Pin, ADC
import network
import dht
import time
import umqtt.simple as MQTT
import sys
import webrepl

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

# Initialisation des capteurs
sensor_dht = dht.DHT11(Pin(32))
sensor_gas = ADC(Pin(36))  # GPIO36 pour le capteur MQ2
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

def read_sensors():
    while True:
        try:
            # Lecture du capteur d'humidité
            sensor_dht.measure()
            humidity = sensor_dht.humidity()
            mqtt.publish(mqtt_topics["humidity"], str(humidity).encode())
            print(f"Humidité: {humidity}%")

            # Lecture du capteur de gaz
            gas_value = sensor_gas.read()
            mqtt.publish(mqtt_topics["gas"], str(gas_value).encode())
            print(f"Gaz: {gas_value}")

        except Exception as e:
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
