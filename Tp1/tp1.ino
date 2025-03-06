#include <LiquidCrystal.h>

// Définition des broches du LCD (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(7, 8, 9, 10, 11, 12);

const int gasSensorPin = A1;  // Entrée analogique du capteur de gaz
const int ledPin = LED_BUILTIN;  // LED intégrée pour alerte
const int valeurAirPur = 150;  // À ajuster selon ton capteur !

void setup() {
    pinMode(ledPin, OUTPUT);
    lcd.begin(16, 2);
    Serial.begin(9600);
    lcd.setCursor(0, 0);
    lcd.print("Capteur...");
    delay(2000);
}

void loop() {
    int gasValue = analogRead(gasSensorPin) - valeurAirPur; // Normalisation
    gasValue = max(gasValue, 0); // Évite d’avoir des valeurs négatives

    Serial.print("Valeur normalisée : ");
    Serial.println(gasValue); // Affiche la valeur normali
    lcd.clear();
    lcd.setCursor(0, 0);

    if (gasValue < 50) {
        lcd.print("Air propre !");
        digitalWrite(ledPin, LOW);
    } else if (gasValue < 200) {
        lcd.print("Qualite moyenne");
        digitalWrite(ledPin, LOW);
    } else {
        lcd.print("Qualite mauvaise");
        digitalWrite(ledPin, HIGH);
    }

    delay(500); // Pause avant mise à jour
}