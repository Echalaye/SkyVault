# Communication MQTT avec ESP32 en MicroPython

Ce projet contient deux scripts MicroPython pour établir une communication MQTT entre des ESP32 :

- `esp32_publisher.py` : Envoie des messages MQTT lorsqu'un bouton est pressé
- `esp32_subscriber.py` : Reçoit des messages MQTT et contrôle une LED en conséquence

## Prérequis

1. ESP32 avec MicroPython installé
2. Un broker MQTT (comme Mosquitto) installé sur votre ordinateur ou serveur
3. Bibliothèque MQTT pour MicroPython

## Installation

### 1. Installer MicroPython sur votre ESP32

Si ce n'est pas déjà fait, suivez les instructions sur [micropython.org](https://micropython.org/download/esp32/) pour installer MicroPython sur votre ESP32.

### 2. Installer la bibliothèque MQTT

Vous devez installer la bibliothèque `umqtt.simple` sur votre ESP32. Utilisez `mpremote` ou un outil similaire :

```
mpremote connect <PORT> mip install umqtt.simple
```

Ou téléchargez manuellement le fichier depuis [micropython-lib](https://github.com/micropython/micropython-lib/tree/master/micropython/umqtt.simple) et transférez-le sur votre ESP32.

### 3. Configuration des scripts

Avant d'utiliser les scripts, modifiez les paramètres suivants dans les deux fichiers :

```python
# Configuration WiFi
ssid = "VOTRE_SSID"           # Remplacez par le nom de votre réseau WiFi
password = "VOTRE_MOT_DE_PASSE"  # Remplacez par le mot de passe de votre WiFi

# Configuration MQTT
mqtt_server = "ADRESSE_IP_DE_VOTRE_MACHINE"  # Remplacez par l'IP de votre broker MQTT
```

## Utilisation

### 1. Transférer les fichiers sur vos ESP32

Utilisez un outil comme `mpremote`, `ampy`, ou l'extension MicroPython pour VSCode pour transférer les fichiers sur vos ESP32 :

```
mpremote connect <PORT> cp esp32_publisher.py :main.py
```

Pour l'ESP32 qui servira de subscriber :

```
mpremote connect <PORT> cp esp32_subscriber.py :main.py
```

### 2. Fonctionnement

- **Publisher** : Appuyez sur le bouton BOOT (GPIO0) de l'ESP32 pour envoyer alternativement les messages "ON" et "OFF".
- **Subscriber** : La LED intégrée (GPIO2) s'allumera ou s'éteindra en fonction des messages reçus.

## Dépannage

- Assurez-vous que votre broker MQTT est en cours d'exécution et accessible
- Vérifiez que les ESP32 sont connectés au même réseau que le broker MQTT
- Vérifiez les messages de débogage dans la console série (115200 bauds)

## Différences avec la version Arduino

Cette implémentation MicroPython diffère de la version Arduino originale sur quelques points :

- Utilisation de la bibliothèque `umqtt.simple` au lieu de `PubSubClient`
- Gestion des exceptions pour une meilleure robustesse
- Utilisation des fonctionnalités spécifiques à MicroPython comme `time.ticks_ms()` et `time.ticks_diff()`
