// libraries
import processing.serial.*;
// serial connection
Serial port;
 
 
void setup() {
  // init serial-port
  print("Available Ports:");
  printArray(Serial.list());
  String port_name = Serial.list()[5];
  port = new Serial(this, port_name, 9600);  
  print("Connected to: " + port_name);
  
  size(783, 391);
  colorMode(RGB);
    
  PImage myImage = loadImage("spectrum.jpg");
  image(myImage, 0, 0);
  
}

 
void draw() {

}

 
void mousePressed() {
  
  color c = get(mouseX, mouseY);
  
  String msg = int(red(c)) + "," + int(green(c)) + "," + int(blue(c));
  
  // debug
  println("now sending: " + msg);
  // send number
  port.write(msg);
  
}
 
 
// this part is executed, when serial-data is received
void serialEvent(Serial p) {
  try {
    // get message till line break (ASCII > 13)
    String message = p.readStringUntil(13);
    // just if there is data
    if (message != null) {
      println("message received: "+trim(message));
    }
  }
  catch (Exception e) {
  }
}
