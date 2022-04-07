/**
 * Scratch 
 * by Andres Colubri. 
 * 
 * Move the cursor horizontally across the screen to set  
 * the position in the movie file.
 */

import processing.video.*;

boolean pause = false;
boolean hinge = false;
boolean hLine = false;
int px;
int py;
float r=0.0;
int u = 0;
int a = 2;
int b = 0;
Movie mov;

void setup() {
  size(1280, 360);

  mov = new Movie(this, "cap.mov");

  // Pausing the video at the first frame. 
  mov.play();
  mov.jump(0);
  mov.pause();
}

void draw() {
  background(0);
  if (mov.available()) {
    mov.read();
    //// A new time position is calculated using the current mouse location:
    //float f = map(mouseX, 0, width, 0, 1);
    //float t = mov.duration() * f;
    mov.play();
    mov.loop();
    //mov.jump(t);
    //mov.pause();
  }  
  translate(width/4, height/2 + u);

  rotate(r);
  mov.filter(BLUR, b);
  mov.filter(POSTERIZE, constrain(a,2,50));

  image(mov, -width/4, -height/2);

  if (hinge && px > 0) {
    line(px, py, mouseX, mouseY);
  }
}

void keyPressed() {
  if (key==CODED) {
    println("turn: "+r, "tilt: "+u);
    if (keyCode == RIGHT) {
      r+=.05;
    } else if (keyCode == LEFT) {
      r-=.05;
    } else if (keyCode == UP) {
      u+=5;
    } else if (keyCode == DOWN) {
      u-=5;
    }
  } else if (key == ' ') {
    println("Spacebar Pressed! " + pause);
    if (!pause) {
      mov.pause();
      pause = true;
    } else if (pause) {
      mov.play();
      mov.loop();
      pause = false;
    }
  } else if (key == 'h' || key == 'H') {
    hinge = !hinge;
    println("hinge: " + hinge);
  } else if (key == 'k' || key == 'K') {
    b+=1;
    println(b);
  } else if (key == ';') {
    b-=1;
    println(b);
  } else if (key == 'O' || key == 'o') {
    a+=1;
  } else if (key == 'l' || key == 'L') {
    a-=1;
  }
}

void mouseClicked() {
  if (hinge) {
    if (!hLine) {
      px = mouseX;
      py = mouseY;
      hLine=true;
    } else {
      hinge=false;
      px=-1;
      py=-1;
      hLine=false;
    }
  }
}
