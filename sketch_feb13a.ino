// #include <LiquidCrystal.h>

// LiquidCrystal lcd(7,8,9,10,11,12);

// void setup() {
//   lcd.begin(16, 2);
//   // you can now interact with the LCD, e.g.:
//   Serial.begin(9600);
//   lcd.setCursor(0, 0);
//   lcd.print("Hello World!");
//   delay(500);
// }

// void loop() {

  
// }


#include <LiquidCrystal.h>
#include <dht_nonblocking.h>

#define DHT_SENSOR_TYPE DHT_TYPE_11

static const int DHT_SENSOR_PIN = 4;
DHT_nonblocking dht_sensor( DHT_SENSOR_PIN, DHT_SENSOR_TYPE );

// Définition des broches du LCD (RS, E, D4, D5, D6, D7)
LiquidCrystal lcd(7,8,9,10,11,12);

const int ledPin = LED_BUILTIN;  // LED intégrée pour alerte 

void setup() {
  pinMode(ledPin, OUTPUT);
  lcd.begin(16, 2);
  Serial.begin(9600);
  lcd.setCursor(0, 0);
  lcd.clear();
  lcd.print("Capteur...");
  delay(500);
}

/*
 * Poll for a measurement, keeping the state machine alive.  Returns
 * true if a measurement is available.
 */
static bool measure_environment( float *temperature, float *humidity )
{
  static unsigned long measurement_timestamp = millis( );

  /* Measure once every four seconds. */
  if( millis( ) - measurement_timestamp > 4000ul )
  {
    if( dht_sensor.measure( temperature, humidity ) == true )
    {
      measurement_timestamp = millis( );
      return( true );
    }
  }

  return( false );
}



/*
 * Main program loop.
 */
void loop( )
{
  float temperature;
  float humidity;
  lcd.clear();
  lcd.setCursor(0, 0);


  /* Measure temperature and humidity.  If the functions returns
     true, then a measurement is available. */
  if( measure_environment( &temperature, &humidity ) == true )
  {
      Serial.print( "T = " );
      Serial.print( temperature, 1 );
      Serial.print( " °C, H = " );
      Serial.print( humidity, 1 );
      Serial.println( "%" );

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Temp: ");
      lcd.print(temperature, 1);
      lcd.print(" C");
      lcd.setCursor(0, 1);
      lcd.print("Hum: ");
      lcd.print(humidity, 1);
      lcd.print(" %");
  } 
  else 
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Echec lec. hum");
    Serial.println("Lecture capteur échouée !");
  }
  delay(2000);
}
