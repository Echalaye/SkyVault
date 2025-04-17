"""
ESP32 MQTT Subscriber with LCD Display
Subscribes to sensor topics and displays values on an LCD screen
"""
import network
import time
import umqtt.simple as MQTT
from machine import Pin, PWM
import sys
import webrepl
from esp32_gpio_lcd import GpioLcd

# ===== CONFIGURATION =====

# LCD Configuration
LCD_CONFIG = {
    "rs_pin": 19,
    "enable_pin": 23,
    "d4_pin": 18,
    "d5_pin": 17,
    "d6_pin": 16,
    "d7_pin": 15,
    "rows": 2,
    "cols": 16,
    "contrast_pin": 2
}

# WiFi Configuration
WIFI_NETWORKS = [
    {"SSID": "iPhone de Nathoo", "PASSWORD": "N397b7nh", "connect": True},
    {"SSID": "A15 de Etienne", "PASSWORD": "lustucrU", "connect": True}
]

# MQTT Configuration
MQTT_CONFIG = {
    "server": "skyvault.local",
    "port": 1883,
    "client_id": "ESP32_Subscriber",
    "topics": {
        "humidity": b"sensors/humidity",
        "gas": b"sensors/gas"
    }
}

# Alert Thresholds
ALERT_THRESHOLDS = {
    "humidity": 60,
    "gas": 200
}

# Status LED
LED_PIN = 2

# ===== HARDWARE INITIALIZATION =====

def init_lcd():
    """Initialize LCD display and contrast"""
    # Setup contrast PWM
    contrast = PWM(Pin(LCD_CONFIG["contrast_pin"]))
    contrast.freq(5000)  # 5 kHz
    contrast.duty_u16(32768)  # 50% duty cycle
    
    # Initialize LCD pins
    lcd = GpioLcd(
        rs_pin=Pin(LCD_CONFIG["rs_pin"], Pin.OUT),
        enable_pin=Pin(LCD_CONFIG["enable_pin"], Pin.OUT),
        d4_pin=Pin(LCD_CONFIG["d4_pin"], Pin.OUT),
        d5_pin=Pin(LCD_CONFIG["d5_pin"], Pin.OUT),
        d6_pin=Pin(LCD_CONFIG["d6_pin"], Pin.OUT),
        d7_pin=Pin(LCD_CONFIG["d7_pin"], Pin.OUT),
        num_lines=LCD_CONFIG["rows"],
        num_columns=LCD_CONFIG["cols"]
    )
    
    return lcd, contrast

# ===== STATUS INDICATOR =====

def blink_led(led, count=1, on_time=0.5, off_time=0.5):
    """Blink LED to indicate status"""
    for _ in range(count):
        led.on()
        time.sleep(on_time)
        led.off()
        time.sleep(off_time)

# ===== CONNECTIVITY =====

def connect_wifi():
    """Connect to WiFi from the list of networks"""
    print("Connecting to WiFi...")
    
    # Initialize WiFi interface
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Try each network until connected
    for network_config in WIFI_NETWORKS:
        ssid = network_config["SSID"]
        password = network_config["PASSWORD"]
        
        # Disconnect if already connected
        if wlan.isconnected():
            wlan.disconnect()
            time.sleep(1)
        
        print(f"Trying {ssid}...")
        wlan.connect(ssid, password)
        
        # Wait for connection with timeout
        for i in range(15):
            if wlan.isconnected():
                print(f"Connected to {ssid}")
                print(f"IP: {wlan.ifconfig()[0]}")
                return wlan
            print(".", end="")
            time.sleep(1)
    
    # If we got here, no connection was established
    print("\nWiFi connection failed!")
    return None

def connect_webrepl():
    """Start WebREPL for remote access"""
    try:
        print("Starting WebREPL...")
        webrepl.start()
        print("WebREPL started")
        return True
    except Exception as e:
        print(f"WebREPL error: {e}")
        return False

def create_mqtt_client(lcd, contrast):
    """Create and configure MQTT client"""
    # Store values received from MQTT
    sensor_values = {
        "humidity": "N/A",
        "gas": "N/A"
    }
    
    # Create MQTT client
    client = MQTT.MQTTClient(
        MQTT_CONFIG["client_id"],
        MQTT_CONFIG["server"],
        MQTT_CONFIG["port"]
    )
    
    # Define callback function
    def on_message(topic, msg):
        # Convert bytes to strings
        topic_str = topic.decode()
        msg_str = msg.decode()
        
        # Update stored values
        if topic == MQTT_CONFIG["topics"]["humidity"]:
            sensor_values["humidity"] = msg_str
        elif topic == MQTT_CONFIG["topics"]["gas"]:
            sensor_values["gas"] = msg_str
        
        # Update LCD display
        update_lcd(lcd, contrast, sensor_values)
    
    # Set callback
    client.set_callback(on_message)
    
    return client

def connect_mqtt(client):
    """Connect to MQTT broker and subscribe to topics"""
    try:
        print(f"Connecting to MQTT broker {MQTT_CONFIG['server']}...")
        client.connect()
        print("Connected to MQTT broker")
        
        # Subscribe to all topics
        for topic in MQTT_CONFIG["topics"].values():
            client.subscribe(topic)
            print(f"Subscribed to {topic.decode()}")
        
        return True
    except Exception as e:
        print(f"MQTT connection error: {e}")
        return False

# ===== DISPLAY FUNCTIONS =====

def update_lcd(lcd, contrast, values):
    """Update LCD with current sensor values and alert status"""
    # Clear display and reset contrast
    lcd.clear()
    contrast.duty_u16(32768)
    
    # First line: Display sensor values
    lcd.putstr(f"h:{values['humidity']:>3} g:{values['gas']:>3}")
    
    # Second line: Check for alerts
    alert_active = check_alerts(values)
    if alert_active:
        lcd.move_to(0, 1)
        lcd.putstr("Alerte !")

def check_alerts(values):
    """Check if any sensor reading exceeds threshold"""
    for sensor_type, threshold in ALERT_THRESHOLDS.items():
        try:
            value = float(values[sensor_type])
            if value > threshold:
                return True
        except (ValueError, TypeError):
            # Skip if value isn't a valid number
            pass
    return False

# ===== MAIN FUNCTION =====

def main():
    """Main program loop"""
    # Initialize hardware
    status_led = Pin(LED_PIN, Pin.OUT)
    lcd, contrast = init_lcd()
    
    try:
        # Display startup message
        lcd.clear()
        lcd.putstr("Starting...")
        
        # Connect to WiFi
        wlan = connect_wifi()
        if not wlan:
            lcd.clear()
            lcd.putstr("WiFi Failed!")
            blink_led(status_led, 2, 1.0, 0.1)
            return
        
        # Update LCD
        lcd.clear()
        lcd.putstr("WiFi Connected")
        time.sleep(1)
        
        # Start WebREPL
        if connect_webrepl():
            lcd.clear()
            lcd.putstr("WebREPL Active")
            time.sleep(1)
        
        # Create and connect MQTT client
        mqtt_client = create_mqtt_client(lcd, contrast)
        if not connect_mqtt(mqtt_client):
            lcd.clear()
            lcd.putstr("MQTT Failed!")
            blink_led(status_led, 5, 0.5, 0.5)
            return
        
        # Update LCD
        lcd.clear()
        lcd.putstr("Waiting for data")
        
        # Main loop - check for messages
        print("Monitoring MQTT messages...")
        while True:
            mqtt_client.check_msg()
            time.sleep(1)
            
    except Exception as e:
        # Handle general errors
        print(f"Error: {e}")
        lcd.clear()
        lcd.putstr("Error! See log")
        blink_led(status_led, 3, 0.2, 0.2)

# Run the program
if __name__ == "__main__":
    main()
