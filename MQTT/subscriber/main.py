# main.py - Fichier principal qui sera exécuté après boot.py
import time
from machine import Pin

# Initialiser la LED comme indicateur
led = Pin(2, Pin.OUT)
print("Démarrage du programme principal...")

# Attendre un peu avant de démarrer pour stabiliser le système
time.sleep(0.1)

try:
    # Importer notre module et exécuter la fonction principale
    import MQTT.subscriber.esp32_pub as esp32_pub
    print("Module esp32_sub importé avec succès")
    
    # Signaler le succès avec un clignotement rapide
    for _ in range(3):
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)
    
    # Lancer le programme principal
    esp32_pub.main()
except Exception as e:
    print(f"Erreur lors du démarrage: {e}")
    # Signaler l'erreur avec un clignotement spécifique
    for _ in range(5):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.2)

