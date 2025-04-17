"""
main.py - Entry point loaded automatically after boot.py
Responsible for initializing and executing the main application
"""
import time
from machine import Pin
import gc  # Import garbage collector for memory optimization

# ===== CONFIGURATION =====
LED_PIN = 2          # Built-in LED pin
STARTUP_DELAY = 1    # Seconds to wait before starting (system stabilization)
MODULE_NAME = "esp32_pub"  # Name of the main application module to import

# ===== LED PATTERNS =====
# Format: [(on_time, off_time), repetitions]
LED_PATTERNS = {
    "success": [(0.1, 0.1), 3],  # Fast blinks for success
    "error": [(0.5, 0.2), 5]     # Slow blinks for error
}

def blink_led(led, pattern_name):
    """
    Blink the LED according to predefined patterns
    
    Args:
        led: Pin object for the LED
        pattern_name: String key for the pattern in LED_PATTERNS dictionary
    """
    if pattern_name in LED_PATTERNS:
        timing, repetitions = LED_PATTERNS[pattern_name]
        for _ in range(repetitions):
            led.on()
            time.sleep(timing[0])
            led.off()
            time.sleep(timing[1])

def main():
    """Main program entry point"""
    # Initialize built-in LED for status indication
    led = Pin(LED_PIN, Pin.OUT)
    led.off()  # Ensure LED starts in OFF state
    
    print("Starting main program...")
    
    # Wait for system stabilization
    time.sleep(STARTUP_DELAY)
    
    try:
        # Free memory before importing modules
        gc.collect()
        
        # Dynamically import the application module
        module = __import__(MODULE_NAME)
        print(f"Successfully imported {MODULE_NAME} module")
        
        # Signal successful import
        blink_led(led, "success")
        
        # Start the main application
        print("Launching main application...")
        module.main()
        
    except ImportError:
        print(f"Error: Could not import {MODULE_NAME} module")
        blink_led(led, "error")
        
    except AttributeError:
        print(f"Error: {MODULE_NAME} module has no 'main' function")
        blink_led(led, "error")
        
    except Exception as e:
        print(f"Error during startup: {e}")
        blink_led(led, "error")

# Execute the main function
if __name__ == "__main__":
    main()
