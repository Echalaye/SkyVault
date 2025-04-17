"""
ESP32 Publisher Script
This script connects to WiFi, reads sensor data, and publishes it to an MQTT broker.
It also sends alerts via Pushover API when certain thresholds are exceeded.
"""
from machine import Pin, ADC
import network
import dht
import time
import umqtt.simple as MQTT
import urequests
import gc
import machine

# ===== CONFIGURATION =====
# WiFi settings
WIFI_HOSTS = [
    {"SSID": "iPhone de Nathoo", "PASSWORD": "N397b7nh"},
    {"SSID": "A15 de Etienne", "PASSWORD": "lustucrU"}
]

# MQTT settings
MQTT_SERVER = "skyvault.local"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "ESP32_Publisher"
MQTT_TOPICS = {
    "humidity": b"sensors/humidity",
    "gas": b"sensors/gas",
    "free_ram": b"kpi/free_ram",
    "cpu_freq": b"kpi/cpu_freq",
    "uptime": b"kpi/uptime",
}

# Sensor pins
PIN_DHT = 32
PIN_GAS = 34
PIN_LED = 2

# Notification settings
PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"
PUSHOVER_USER_KEY = "ujjexh4xz6zntxf2up9v8hedqxr2ch"
PUSHOVER_API_TOKEN = "ajqsdqge6g3ve8vojsiwv4h376pbsa"

# Alert thresholds
HUMIDITY_THRESHOLD = 60
GAS_THRESHOLD = 200
ALERT_COOLDOWN = 300  # 5 minutes between alerts

# Global variables
mqtt_client = None
last_humidity_alert = 0


# ===== HARDWARE INITIALIZATION =====
def init_hardware():
    """Initialize all hardware components"""
    # Initialize LED
    led = Pin(PIN_LED, Pin.OUT)
    
    # Initialize sensors
    dht_sensor = dht.DHT11(Pin(PIN_DHT))
    gas_sensor = ADC(Pin(PIN_GAS))
    gas_sensor.atten(ADC.ATTN_11DB)  # Configure for 0-3.3V range
    
    return led, dht_sensor, gas_sensor


# ===== CONNECTIVITY =====
def connect_wifi():
    """Connect to any available WiFi network from the configured list"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Try each WiFi network until connected
    for host in WIFI_HOSTS:
        ssid, password = host["SSID"], host["PASSWORD"]
        
        # Disconnect if already connected
        if wlan.isconnected():
            wlan.disconnect()
            time.sleep(1)
        
        try:
            print(f"\nAttempting to connect to {ssid}...")
            wlan.connect(ssid, password)
            
            # Wait for connection with timeout
            for _ in range(15):  # 15 second timeout
                if wlan.isconnected():
                    print(f"Connected to {ssid}")
                    print(f"IP address: {wlan.ifconfig()[0]}")
                    return wlan
                print(".", end="")
                time.sleep(1)
                
        except Exception as e:
            print(f"Connection error to {ssid}: {e}")
    
    print("Failed to connect to all WiFi networks")
    return None


def connect_mqtt():
    """Connect to MQTT broker"""
    global mqtt_client
    
    try:
        print(f"Connecting to MQTT broker {MQTT_SERVER}:{MQTT_PORT}...")
        mqtt_client = MQTT.MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, MQTT_PORT)
        mqtt_client.connect()
        print("Connected to MQTT broker")
        return True
    except Exception as e:
        print(f"MQTT connection error: {e}")
        return False


# ===== DATA FUNCTIONS =====
def get_system_stats():
    """Collect system information"""
    return {
        "free_ram": gc.mem_free(),
        "cpu_freq": machine.freq(),
        "uptime": time.ticks_ms()
    }


def calculate_ppm(adc_value):
    """Convert ADC reading to estimated PPM"""
    try:
        if adc_value < 500:
            return 0
        elif adc_value < 1000:
            return round(((adc_value - 500) / 500) * 50, 1)
        elif adc_value < 1500:
            return round(50 + ((adc_value - 1000) / 500) * 150, 1)
        else:
            return 201  # Value above threshold
    except Exception as e:
        print(f"PPM calculation error: {e}")
        return -1


# ===== NOTIFICATION =====
def send_pushover_notification(title, message, priority=0):
    """Send notification via Pushover API"""
    try:
        data = {
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "title": title,
            "message": message,
            "priority": priority
        }
        
        response = urequests.post(PUSHOVER_API_URL, json=data)
        print(f"Notification sent, response: {response.text}")
        response.close()
        return True
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False


# ===== LED CONTROL =====
def blink_led(led, count=1, on_time=0.1, off_time=0.1):
    """Blink LED a specified number of times"""
    for _ in range(count):
        led.on()
        time.sleep(on_time)
        led.off()
        time.sleep(off_time)


# ===== SENSOR READING =====
def read_sensors(led, dht_sensor, gas_sensor):
    """Main loop to read sensors and publish data"""
    global last_humidity_alert
    
    while True:
        gc.collect()  # Free memory each cycle
        
        try:
            # Read humidity sensor
            dht_sensor.measure()
            humidity = dht_sensor.humidity()
            print(f"Humidity: {humidity}%")
            
            # Publish humidity data
            if mqtt_client:
                try:
                    mqtt_client.publish(MQTT_TOPICS["humidity"], str(humidity).encode())
                except Exception as e:
                    print(f"MQTT humidity publish error: {e}")
                    # Reconnect on failure
                    connect_mqtt()
            
            # Check humidity threshold
            current_time = time.time()
            if humidity > HUMIDITY_THRESHOLD and (current_time - last_humidity_alert > ALERT_COOLDOWN):
                notification_title = "Humidity Alert"
                notification_message = f"Humidity level is {humidity}% (threshold: {HUMIDITY_THRESHOLD}%)"
                
                if send_pushover_notification(notification_title, notification_message, 1):
                    last_humidity_alert = current_time
                    print("Humidity alert sent")
            
            # Read gas sensor
            gas_value = gas_sensor.read()
            ppm = calculate_ppm(gas_value)
            print(f"Gas: {gas_value} | Propane estimate: {ppm} ppm")
            
            # Publish gas data
            if mqtt_client:
                try:
                    mqtt_client.publish(MQTT_TOPICS["gas"], str(ppm).encode())
                except Exception as e:
                    print(f"MQTT gas publish error: {e}")
                    # Reconnect on failure
                    connect_mqtt()
            
            # Check gas threshold
            if ppm > GAS_THRESHOLD:
                notification_title = "Gas Alert"
                notification_message = f"High gas level: {ppm} ppm (threshold: {GAS_THRESHOLD} ppm)"
                
                send_pushover_notification(notification_title, notification_message, 2)
                print("Gas alert sent")
            
            # Publish system stats
            try:
                stats = get_system_stats()
                stats_info = f"\n> Free RAM: {stats['free_ram']} bytes \n> CPU freq: {stats['cpu_freq']} Hz \n> Uptime: {stats['uptime']} ms"
                print(f"Stats: {stats_info}")
                
                if mqtt_client:
                    # mqtt.publish(mqtt_topics["data"], ujson.dumps(kpi_data).encode())
                    mqtt_client.publish(MQTT_TOPICS["free_ram"], str(stats['free_ram']).encode())
                    mqtt_client.publish(MQTT_TOPICS["cpu_freq"], str(stats['cpu_freq']).encode())
                    mqtt_client.publish(MQTT_TOPICS["uptime"], str(stats['uptime']).encode())
                    
            except Exception as e:
                print(f"Stats publishing error: {e}")
            
            # Indicate successful cycle
            blink_led(led, 1, 0.1, 0.1)
            
        except Exception as e:
            print(f"Sensor reading error: {e}")
            blink_led(led, 2, 0.2, 0.2)  # Signal error
        
        # Wait before next reading
        time.sleep(2)


# ===== MAIN FUNCTION =====
def main():
    """Main program entry point"""
    led, dht_sensor, gas_sensor = init_hardware()
    
    try:
        # Connect to WiFi
        wlan = connect_wifi()
        if not wlan:
            blink_led(led, 2, 1, 0.5)  # Signal WiFi error
            print("Cannot continue without WiFi connection")
            return
        
        # Connect to MQTT broker
        if not connect_mqtt():
            blink_led(led, 3, 0.5, 0.5)  # Signal MQTT error
            print("Cannot continue without MQTT connection")
            return
        
        # Start sensor reading loop
        print("Starting sensor readings")
        read_sensors(led, dht_sensor, gas_sensor)
        
    except Exception as e:
        print(f"Main error: {e}")
        blink_led(led, 5, 0.1, 0.1)  # Signal critical error


# Only run when executed directly
if __name__ == "__main__":
    main()
