"""
main.py - Boot loader for ESP32 MQTT subscriber
Automatically executed after boot.py to initialize and run the main application
"""
import time
import gc
from machine import Pin

# ===== CONFIGURATION =====
# These constants make it easy to modify key parameters
LED_PIN = 2                # Built-in LED for status indication
STARTUP_DELAY = 0.1        # Seconds to wait for system stabilization
MODULE_NAME = "esp32_sub"  # Module to import and run

# LED patterns for different status indicators
SUCCESS_PATTERN = [(0.1, 0.1), 3]  # Format: [(on_time, off_time), repetitions]
ERROR_PATTERN = [(0.5, 0.2), 5]    # Longer blinks for errors


def blink_led(led, pattern):
    """
    Blink the LED in a specific pattern to indicate status
    
    Args:
        led: Pin object for the LED
        pattern: Tuple containing (timing_tuple, repetitions)
    """
    timing, repetitions = pattern
    for _ in range(repetitions):
        led.on()
        time.sleep(timing[0])
        led.off()
        time.sleep(timing[1])


def import_and_run():
    """
    Import the main module and run its main function
    
    Returns:
        bool: True if successful, False if an error occurred
    """
    try:
        # Free memory before importing module
        gc.collect()
        
        # Import the main module dynamically
        print(f"Importing {MODULE_NAME} module...")
        module = __import__(MODULE_NAME)
        print(f"Successfully imported {MODULE_NAME}")
        
        # Run the main function from the imported module
        print("Starting main application...")
        module.main()
        return True
        
    except ImportError:
        # Handle missing module error
        print(f"Error: Could not find module '{MODULE_NAME}'")
        return False
        
    except AttributeError:
        # Handle missing main function error
        print(f"Error: Module '{MODULE_NAME}' has no 'main' function")
        return False
        
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Error during startup: {e}")
        return False


def main():
    """Main boot sequence"""
    # Initialize status LED
    led = Pin(LED_PIN, Pin.OUT)
    led.off()  # Ensure LED starts off
    
    print("Starting boot sequence...")
    
    # Wait for system to stabilize
    time.sleep(STARTUP_DELAY)
    
    # Import and run the main application
    if import_and_run():
        # Success - indicate with quick blinks
        blink_led(led, SUCCESS_PATTERN)
    else:
        # Error - indicate with slower blinks
        blink_led(led, ERROR_PATTERN)


# Execute the boot sequence
if __name__ == "__main__":
    main()
