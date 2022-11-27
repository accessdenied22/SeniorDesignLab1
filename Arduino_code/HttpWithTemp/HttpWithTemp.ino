#include <Arduino.h>

#include <WiFi.h>
#include <WiFiMulti.h>

#include <HTTPClient.h>

#include <LiquidCrystal.h>
#include <OneWire.h>
#include <DallasTemperature.h>

WiFiMulti wifiMulti;

// LCD interface pins
LiquidCrystal lcd(19, 23, 18, 17, 16, 15);

// GPIO pin where the DS18B20 is connected
const int oneWireBus = 4;     
// GPIO pin connected to the button which controls LCD lighting
const int btnPin = 27;

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(oneWireBus);
// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

// Login details for Wifi
const char* ssid = "MRJ";
const char* password = "poiuy123";

// INITIAL SETUP
void setup() {
    pinMode(btnPin, OUTPUT);
    // set up the LCD's number of columns and rows:
    lcd.begin(16, 2);
    // Start the Serial Monitor
    Serial.begin(115200);
    // Start the DS18B20 sensor
    sensors.begin();

    Serial.println();
    Serial.println();
    Serial.println();

    Serial.println("[SETUP] WAIT...\n");
    Serial.flush();
    delay(1000);

    wifiMulti.addAP(ssid, password);
    sensors.setResolution(9);
    sensors.requestTemperatures();
    sensors.getTempCByIndex(0); // Discard first data point
    if((wifiMulti.run() == WL_CONNECTED)) { 
      HTTPClient http;
      String url = "http://accessdenied.pythonanywhere.com/up?val=start";
      http.begin(url);
      int httpCode = http.GET();   
      if(httpCode > 0) {
          // HTTP header has been send and Server response header has been handled
          Serial.printf("[HTTP] GET response code: %d\n", httpCode);
  
          // file found at server
          if(httpCode == HTTP_CODE_OK) {
              String payload = http.getString();
              Serial.println(payload);
              if (payload[0] == '1') {
                 digitalWrite(btnPin, HIGH);
              } else {
                 digitalWrite(btnPin, LOW);
              }
          }
      } else {
          Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }   
    }
}

// MAIN LOOP
void loop() {
    sensors.setResolution(9);
    sensors.requestTemperatures(); 
    int tempC = int(sensors.getTempCByIndex(0));
    if (tempC <= -100) {
      // set the cursor to column 0, line 0
      // (note: line 1 is the second row, since counting begins with 0):
      lcd.setCursor(0, 0);
      lcd.print("Error: Sensor");
      lcd.setCursor(0, 1);
      lcd.print("Disconnected");
    } else {
      lcd.setCursor(0, 0);
      lcd.print("Current temp:");
      lcd.setCursor(0, 1);
      lcd.print(tempC);
      lcd.print(" deg C     ");  
//      Serial.println(tempC);
    }
    
    if((wifiMulti.run() == WL_CONNECTED)) { 
        HTTPClient http;
        
        String url = "http://accessdenied.pythonanywhere.com/up?val=";
        http.begin(url+tempC);
        
        // start connection and send HTTP header
        int httpCode = http.GET();

        // httpCode will be negative on error
        if(httpCode > 0) {
            // HTTP header has been send and Server response header has been handled
            Serial.printf("[HTTP] GET response code: %d\n", httpCode);

            // file found at server
            if(httpCode == HTTP_CODE_OK) {
                String payload = http.getString();
                Serial.println(payload);
                
                // turn on LCD if the server response is '1', turn off otherwise
                if (payload[0] == '1') {
                   digitalWrite(btnPin, HIGH);
                } else {
                   digitalWrite(btnPin, LOW);
                }
            }
        } else {
            Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
        }

        http.end();
          
    }
}
