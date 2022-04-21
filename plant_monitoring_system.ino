#include "DHT.h"
#include <LightDependentResistor.h>

#define DHTPIN 2                                      // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11                                 // DHT 11
#define OTHER_RESISTOR 10000                          // ohms
#define USED_PIN A0                                   // analog pin connected to the light sensor
#define USED_PHOTOCELL LightDependentResistor::GL5516 // Photocell used

// pins controlling relay
const int lampToRelayPin = 3;
const int fanToRelayPin = 4;
const int pumpToRelayPin = 5;

// parameter for toggling different relays
int footcandleLampOn = 4;
int hotTemperature = 30;
int moistSoil = 50;
int pumpDuration = 1;

// calibrate the soil moisture sensor
const int AirValue = 540;
const int WaterValue = 327;

// initial soil moisture values
int soilMoistureValue = 0;
int soilmoisturepercent = 0;

// Create a GL5516 photocell instance (on A0 pin)
LightDependentResistor photocell(USED_PIN,
                                 OTHER_RESISTOR,
                                 USED_PHOTOCELL,
                                 10,  // Default ADC resolution
                                 10); // Default linear smooth (if used)

// Create a DHT instance
DHT dht(DHTPIN, DHTTYPE);

// default setting of different parts
boolean watering = false;
boolean lampOn = false;
boolean fanOn = false;
boolean autoLampOn = true;
boolean autoFanOn = true;
boolean autoPumpOn = true;
String readString;
int incomingAction;
String header;
void setup()
{
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(lampToRelayPin, OUTPUT);
  pinMode(fanToRelayPin, OUTPUT);
  pinMode(pumpToRelayPin, OUTPUT);

  photocell.setPhotocellPositionOnGround(false);

  Serial.begin(9600);

  dht.begin();
}

void loop()
{

  delay(2000);
  incomingAction = 0;
  readString = "";
  header = "";
  soilMoistureValue = analogRead(A1);                                         // get reading from soil moisture sensor
  soilmoisturepercent = map(soilMoistureValue, AirValue, WaterValue, 0, 100); // map the value to percentage

  // get incoming data and get perform actions

  while (Serial.available())
  {
    delay(3); // delay to allow buffer to fill
    if (Serial.available() > 0)
    {
      char c = Serial.read(); // gets one byte from serial buffer
      readString += c;        // makes the string readString
    }
  }

  if (readString.length() > 0)
  {
    Serial.println(readString.length());

    header = readString.substring(0, 2); // get the first two characters

    if (header == "10")
    {
      incomingAction = (readString.substring(2, 4)).toInt(); // get the next four characters
    }
    else if (header == "20")
    {
      footcandleLampOn = (readString.substring(2, 5)).toInt();
      hotTemperature = (readString.substring(5, 8)).toInt();
      moistSoil = (readString.substring(8, 11)).toInt();
      pumpDuration = (readString.substring(11, 14)).toInt();
      autoLampOn = true;
      autoFanOn = true;
      autoPumpOn = true;
    }
  }

  //  int incomingAction = Serial.parseInt();
  switch (incomingAction)
  {
  case 1: //  water plant
    watering = !watering;
    autoPumpOn = false;
    digitalWrite(pumpToRelayPin, HIGH);
    delay(pumpDuration * 1000);
    digitalWrite(pumpToRelayPin, LOW);
    break;
  case 2: //  toggle lamp
    lampOn = !lampOn;
    autoLampOn = false;
    digitalWrite(lampToRelayPin, !digitalRead(lampToRelayPin));
    break;
  case 3: //  toggle fan
    fanOn = !fanOn;
    autoFanOn = false;
    digitalWrite(fanToRelayPin, !digitalRead(fanToRelayPin));
    break;
  case 4: //  toggle auto lamp
    autoLampOn = !autoLampOn;
    break;
  case 5: // toggle auto fan
    autoFanOn = !autoFanOn;
    break;
  case 6: //  toggle auto pump
    autoPumpOn = !autoPumpOn;
    break;
  case 7:
    //  reset
    autoLampOn = true;
    autoFanOn = true;
    autoPumpOn = true;
    footcandleLampOn = 4;
    hotTemperature = 30;
    moistSoil = 50;
    pumpDuration = 1;
    break;
  default:
    break;
  }

  // Converting the reading from LDR to footcandle
  float footcandle = LightDependentResistor::luxToFootCandles(photocell.getCurrentLux());

  // Read temperature and humidity from DHT sensor
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t))
  {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // print to serial monitor to be fetch by the web app
  Serial.print(h);
  Serial.print("|");
  Serial.print(t);
  Serial.print("|");
  Serial.print(footcandle);
  Serial.print("|");
  if (soilmoisturepercent >= 100)
  {
    Serial.print("100");
  }
  else if (soilmoisturepercent <= 0)
  {
    Serial.print("0");
  }
  else if (soilmoisturepercent > 0 && soilmoisturepercent < 100)
  {
    Serial.print(soilmoisturepercent);
  }
  Serial.print("|");
  Serial.print(digitalRead(lampToRelayPin));
  Serial.print("|");
  Serial.print(digitalRead(fanToRelayPin));
  Serial.print("|");
  Serial.print(digitalRead(pumpToRelayPin));

  Serial.print("|");
  Serial.print(autoLampOn);
  Serial.print("|");
  Serial.print(autoFanOn);
  Serial.print("|");
  Serial.println(autoPumpOn);

  // turn the lamp on if the intended light intensity is achieved
  if (autoLampOn == true)
  {
    if (footcandle < footcandleLampOn)
    {
      digitalWrite(lampToRelayPin, LOW);
    }
    else
    {
      digitalWrite(lampToRelayPin, HIGH);
    }
  }

  // turn the fan on if the temperature is above the threshold
  if (autoFanOn == true)
  {
    if (t > hotTemperature)
    {
      digitalWrite(fanToRelayPin, LOW);
    }
    else
    {
      digitalWrite(fanToRelayPin, HIGH);
    }
  }

  // turn the pump on for 0.7 second if the soil is dry
  if (autoPumpOn == true)
  {
    if (soilmoisturepercent < moistSoil)
    {
      digitalWrite(pumpToRelayPin, HIGH);
      delay(pumpDuration * 1000);
      digitalWrite(pumpToRelayPin, LOW);
    }
    else
    {
      digitalWrite(pumpToRelayPin, LOW);
    }
  }
}
