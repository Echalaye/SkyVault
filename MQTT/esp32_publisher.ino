#include <WiFi.h>
#include <PubSubClient.h>

// Configuration WiFi
const char* ssid = "VOTRE_SSID";
const char* password = "VOTRE_MOT_DE_PASSE";

// Configuration MQTT
const char* mqtt_server = "ADRESSE_IP_DE_VOTRE_MACHINE"; // Remplacez par l'IP de votre machine hôte
const int mqtt_port = 1883;
const char* mqtt_client_id = "ESP32_Publisher";
const char* mqtt_topic = "esp32/data"; // Sujet sur lequel publier

// Objets WiFi et MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// Variables pour les capteurs
const int buttonPin = 0; // Bouton BOOT de l'ESP32
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

// Fonction pour se connecter au WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connexion à ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connecté");
  Serial.println("Adresse IP: ");
  Serial.println(WiFi.localIP());
}

// Fonction pour se reconnecter au broker MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentative de connexion MQTT...");
    if (client.connect(mqtt_client_id)) {
      Serial.println("connecté");
    } else {
      Serial.print("échec, rc=");
      Serial.print(client.state());
      Serial.println(" nouvelle tentative dans 5 secondes");
      delay(5000);
    }
  }
}

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(115200);
  setup_wifi();
  
  // Configuration du serveur MQTT
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  // Si déconnecté, tenter de se reconnecter
  if (!client.connected()) {
    reconnect();
  }
  
  // Maintenir la connexion MQTT
  client.loop();
  
  // Lire l'état du bouton
  int reading = digitalRead(buttonPin);
  
  // Vérifier si l'état du bouton a changé
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  // Si l'état est stable depuis suffisamment longtemps
  if ((millis() - lastDebounceTime) > debounceDelay) {
    // Si le bouton est pressé (LOW pour un bouton avec pull-up)
    if (reading == LOW) {
      // Alterner entre ON et OFF à chaque pression
      static bool ledState = false;
      ledState = !ledState;
      
      // Publier le message
      if (ledState) {
        Serial.println("Publication du message: ON");
        client.publish(mqtt_topic, "ON");
      } else {
        Serial.println("Publication du message: OFF");
        client.publish(mqtt_topic, "OFF");
      }
    }
  }
  
  // Sauvegarder l'état du bouton
  lastButtonState = reading;
  
  // Délai pour éviter les rebonds
  delay(10);
} 