#include <WiFi.h>
#include <PubSubClient.h>

// Configuration WiFi
const char* ssid = "VOTRE_SSID";
const char* password = "VOTRE_MOT_DE_PASSE";

// Configuration MQTT
const char* mqtt_server = "ADRESSE_IP_DE_VOTRE_MACHINE"; // Remplacez par l'IP de votre machine hôte
const int mqtt_port = 1883;
const char* mqtt_client_id = "ESP32_Subscriber";
const char* mqtt_topic = "esp32/data"; // Sujet auquel s'abonner

// Objets WiFi et MQTT
WiFiClient espClient;
PubSubClient client(espClient);

// Variables pour les LED ou autres composants
const int ledPin = 2; // LED intégrée de l'ESP32

// Fonction de rappel pour les messages MQTT reçus
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message reçu [");
  Serial.print(topic);
  Serial.print("] ");
  
  // Convertir le payload en chaîne
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Exemple: allumer/éteindre la LED selon le message
  if (message == "ON") {
    digitalWrite(ledPin, HIGH);
    Serial.println("LED allumée");
  } else if (message == "OFF") {
    digitalWrite(ledPin, LOW);
    Serial.println("LED éteinte");
  }
}

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
      // S'abonner au sujet
      client.subscribe(mqtt_topic);
      Serial.print("Abonné au sujet: ");
      Serial.println(mqtt_topic);
    } else {
      Serial.print("échec, rc=");
      Serial.print(client.state());
      Serial.println(" nouvelle tentative dans 5 secondes");
      delay(5000);
    }
  }
}

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(115200);
  setup_wifi();
  
  // Configuration du serveur MQTT et de la fonction de rappel
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void loop() {
  // Si déconnecté, tenter de se reconnecter
  if (!client.connected()) {
    reconnect();
  }
  
  // Maintenir la connexion MQTT
  client.loop();
  
  // Autres tâches périodiques si nécessaire
  delay(100);
} 