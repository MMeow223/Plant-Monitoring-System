#include "DHT.h"
#include <LightDependentResistor.h>

#define DHTPIN 2                                      // Digital pin connected to the DHT sensor
#define DHTTYPE DHT11                                 // DHT 11
#define OTHER_RESISTOR 10000                          // ohms
#define USED_PIN A0                                   // analog pin connected to the light sensor
#define USED_PHOTOCELL LightDependentResistor::GL5516 // Photocell used

const int lampToRelayPin = 3;
const int fanToRelayPin = 4;
const int pumpToRelayPin = 5;
const float footcandleLampOn = 4;
const int hotTemperature = 30;
const int moistSoil = 20;
const int AirValue = 540;   // you need to replace this value with Value_1
const int WaterValue = 327; // you need to replace this value with Value_2

int soilMoistureValue = 0;
int soilmoisturepercent = 0;

// Create a GL5516 photocell instance (on A0 pin)
LightDependentResistor photocell(USED_PIN,
                                 OTHER_RESISTOR,
                                 USED_PHOTOCELL,
                                 10,  // Default ADC resolution
                                 10); // Default linear smooth (if used)

DHT dht(DHTPIN, DHTTYPE);

boolean watering = false;
boolean lampOn = false;
boolean fanOn = false;
boolean autoLampOn = true;
boolean autoFanOn = true;
boolean autoPumpOn = true;

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
  //  Serial.println(F("DHTxx test!"));

  dht.begin();
}

void loop()
{

  delay(2000);

  soilMoistureValue = analogRead(A1); // put Sensor insert into soil
  soilmoisturepercent = map(soilMoistureValue, AirValue, WaterValue, 0, 100);

  int incomingAction = Serial.parseInt();

  switch (incomingAction)
  {
  case 1: //  water plant
    watering = !watering;
    autoPumpOn = false;
    digitalWrite(8, !digitalRead(8));
    digitalWrite(pumpToRelayPin, HIGH);
    delay(700);
    digitalWrite(pumpToRelayPin, LOW);

    break;
  case 2: //  toggle lamp
    lampOn = !lampOn;
    autoLampOn = false;
    digitalWrite(9, !digitalRead(9));
    digitalWrite(lampToRelayPin, !digitalRead(lampToRelayPin));
    break;
  case 3: //  toggle fan
    fanOn = !fanOn;
    autoFanOn = false;
    digitalWrite(10, !digitalRead(10));
    digitalWrite(fanToRelayPin, !digitalRead(fanToRelayPin));
    break;
  case 4: //  toggle auto lamp
    autoLampOn = !autoLampOn;
    digitalWrite(11, !digitalRead(11));
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
    digitalWrite(8, !digitalRead(8));
    digitalWrite(9, !digitalRead(9));
    digitalWrite(10, !digitalRead(10));
    digitalWrite(11, !digitalRead(11));
    break;
  default:
    break;
  }

  // Converting the reading from LDR to footcandle
  float footcandle = LightDependentResistor::luxToFootCandles(photocell.getCurrentLux());
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t))
  {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);

  // Serial.print(F(" Humidity: "));
  // Serial.print(h);
  // Serial.print(F("%  Temperature: "));
  // Serial.print(t);
  // Serial.print(F("C "));
  // Serial.print(hic);
  // Serial.print(F("C "));
  // Serial.print("FootCandle");
  // Serial.println(footcandle);

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
  Serial.println(digitalRead(pumpToRelayPin));

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

  if (autoPumpOn == true)
  {
    if (soilmoisturepercent < moistSoil)
    {
      digitalWrite(pumpToRelayPin, HIGH);
      delay(700);
      digitalWrite(pumpToRelayPin, LOW);
    }
    else
    {
      digitalWrite(pumpToRelayPin, LOW);
    }
  }
}
