#include <Wire.h>
#include <Adafruit_VL6180X.h>   //TOF sensor library
#include <Adafruit_MLX90614.h> //IR Temp Sensor

Adafruit_VL6180X vl = Adafruit_VL6180X();
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

char data[20];
String serial_input;

void setup() {
  Serial.begin(115200);

  // wait for serial port to open on native usb devices
  while (!Serial) {
    delay(1);
  }

  //  Init temperature sensor
  Serial.println("Connecting to MLX90614 IR Temperature Sensor...");  
  if (! mlx.begin()) {
    Serial.println("Failed to find TEMP sensor");
    while (1);
  }
  Serial.println("Temperature Sensor found!");
  
  //  Init TOF Sensor  
  Serial.println("Connecting to VL6180x TOF Sensor...");
  if (! vl.begin()) {
    Serial.println("Failed to find sensor");
    while (1);
  }
  Serial.println("Range Sensor found!");

  Serial.println("### Sensors online! ###");  
  Serial.println("Send 'tmp' or 'rng' via serial to get data from the desired sensor");  


}

void loop() {

  // send data upon request
  if (Serial.available() > 0) {

    // read the incoming byte:
    serial_input = Serial.readStringUntil('\n');

    // // say what you got:
    // Serial.print("I received: ");
    // Serial.println(serial_input);

    // read temperature
    if (serial_input == "tmp"){
      //  Get Data from Temp Sensor
      float amb_tmp = mlx.readAmbientTempC(); 
      float obj_tmp = mlx.readObjectTempC();
      Serial.print(amb_tmp);
      Serial.print(",");
      Serial.println(obj_tmp);
    }

    // read range
    if (serial_input == "rng"){
      
      //  Get Data from TOF Sensor
      float lux = vl.readLux(VL6180X_ALS_GAIN_5);
      uint8_t range = vl.readRange();
      uint8_t status = vl.readRangeStatus();

      

      if (status == VL6180X_ERROR_NONE) {
        Serial.println(range);
      }

      // Some error occurred, print it out!
      if  ((status >= VL6180X_ERROR_SYSERR_1) && (status <= VL6180X_ERROR_SYSERR_5)) {
        Serial.println("System error");
      }
      else if (status == VL6180X_ERROR_ECEFAIL) {
        Serial.println("ECE failure");
      }
      else if (status == VL6180X_ERROR_NOCONVERGE) {
        Serial.println("No convergence");
      }
      else if (status == VL6180X_ERROR_RANGEIGNORE) {
        Serial.println("Ignoring range");
      }
      else if (status == VL6180X_ERROR_SNR) {
        Serial.println("Signal/Noise error");
      }
      else if (status == VL6180X_ERROR_RAWUFLOW) {
        Serial.println("Raw reading underflow");
      }
      else if (status == VL6180X_ERROR_RAWOFLOW) {
        Serial.println("Raw reading overflow");
      }
      else if (status == VL6180X_ERROR_RANGEUFLOW) {
        Serial.println("Range reading underflow");
      }
      else if (status == VL6180X_ERROR_RANGEOFLOW) {
        Serial.println("Range reading overflow");
      }

    }

  }  


  // delay(500);

}
