// This is used to test which light color is best to observe capillaries
// We used a Neopixel 12 LED ring, hooked up to and arduino uno.
// The color RGB values (r,g,b) are sent via a serial from the processing sketch: color_test_pr.pde

#include <Adafruit_NeoPixel.h>

#define LED_PIN    9
#define LED_COUNT 12

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);
// Argument 1 = Number of pixels in NeoPixel strip
// Argument 2 = Arduino pin number (most are valid)
// Argument 3 = Pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)

String command;

void setup() {

  Serial.begin(9600); // Start serial communication at 9600 bps
  
  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(250); // Set BRIGHTNESS to about 1/5 (max = 255)

}

void loop() {


  if (Serial.available()) 
  { // If data is available to read,
    command = Serial.readString();
    //command.trim();
    parseCommand(command);
  }
  
  delay(10); // Wait 10 milliseconds for next reading  

}


void parseCommand(String comm)
{
  //Parse String to Array
  String tmpStr = "";
  int commaIndex = 0;
  int nextValIndex = 0;
  int i = 0;
  int vals[3]={0,0,0};
  
  while (commaIndex > -1)
  {
    if(comm.indexOf(',', commaIndex+1) > -1)
      tmpStr = comm.substring(nextValIndex, comm.indexOf(',', commaIndex+1));
    else
      tmpStr = comm.substring(nextValIndex, comm.indexOf(NULL));
                
    vals[i] = tmpStr.toInt();
    i++;
    commaIndex = comm.indexOf(',', commaIndex+1);
    nextValIndex = commaIndex + 1;   
  } 

  // Apply LED Colors to strip
  for(int i=0; i<strip.numPixels(); i++) { 
    strip.setPixelColor(i, strip.Color(vals[0],   vals[1],   vals[2]));         
  }
  
  strip.show();       

}


void colorWipe(uint32_t color, int wait) {
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }
}
