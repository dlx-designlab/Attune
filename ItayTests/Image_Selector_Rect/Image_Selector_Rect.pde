import java.io.File;

ArrayList<PImage> imgContainer;
IntList points[];
String[] fileNames;
int n=3;
int index=0; 
File dir; 
File [] files;
File f;
int num = 0;
PImage ref;
PImage cropped;
int prevX=0;
int prevY=0;
int currX=0;
int currY=0;
int imgXpos = 640;
String state = "normal";
String[] stateList;
color[] stateColor;
int[] rectList;
int tempNum;
int imgCount;
boolean trashSample = false;
String fileName;

String lastImg;

void setup() {  
  size(1280, 530);
  colorMode(HSB, 360, 360, 360);

  imgContainer=new ArrayList<PImage>();
  fileNames = new String[]{};
  dir= new File(dataPath(""));
  files= dir.listFiles();
  loadImagesFromFolder();  
  stateList = new String[]{
    "Normal", 
    "Curled", 
    "Dotted"
  };

  stateColor = new color[stateList.length];
  points = new IntList[imgCount];
  for (int i = 0; i<imgCount; i++) {
    points[i] = new IntList();
  }
  println(imgCount);
  noFill();
  stroke(0, 255, 0);
  strokeWeight(2);
  for (int i = 0; i<stateColor.length; i++) {
    stateColor[i] = color(i*20, 360, 360);
  }
}

void draw() { 
  background(0);
  PImage tempPic = imgContainer.get(num); 
  tempPic.resize(width/2, 0);
  image(tempPic, 0, 50);
  if (cropped != null) {
    text(state, 640, 20);
    image(cropped, imgXpos+10, 50);
  }
  textSize(20);
  text("File Name: " + fileNames[num], 10, 20);
  drawRects();
}




void loadImagesFromFolder() {
  for (int i = 0; i <= files.length - 1; i++)
  {
    String path = files[i].getAbsolutePath();
    if (path.toLowerCase().endsWith(".png") || path.toLowerCase().endsWith(".jpg") || path.toLowerCase().endsWith(".jpeg") || path.toLowerCase().endsWith(".gif"))
    {
      PImage imageFile;
      imageFile = loadImage(""+files[i]);
      imgContainer.add(imageFile);
      fileNames = append(fileNames, files[i].getName());
      imgCount = i;
    }
  }
}



void mousePressed() {
  noFill();
  stroke(255, 0, 0);
  prevX=mouseX;
  prevY=mouseY;
}

void mouseDragged() {
  rect(prevX, prevY, mouseX-prevX, mouseY-prevY);
}

void mouseReleased() {
  int x, y, w, h;
  x = min(prevX, mouseX);
  y = min(prevY, mouseY);
  if (mouseX > prevX) w = mouseX - prevX;
  else w = prevX - mouseX;
  if (mouseY > prevY) h = mouseY - prevY;
  else h = prevY - mouseY;

  points[num].append(x);
  points[num].append(y);
  points[num].append(w);
  points[num].append(h);
  printArray(points[num]);
  noStroke();
  cropped = get(x+2, y+2, w-2, h-2);
  lastImg = state+"/"+state+""+year()+""+month()+""+day()+""+hour()+""+minute()+""+second()+".png";
  fileName = state+""+year()+""+month()+""+day()+""+hour()+""+minute()+""+second()+".png";
  cropped.save(lastImg);
  //fileName = dataPath(lastImg);
  //println(fileName);
}



void keyPressed() {
  if (key == '1') {
    state = "normal";
    stroke(0, 255, 0);
  } else if (key == '2') {
    state = "curled";
    stroke(255, 0, 0);
  } else if (key == '3') {
    state = "dotted";
    stroke(0, 0, 255);
  } else if (key==CODED) {
    if (keyCode == RIGHT && num < imgContainer.size()-1) {
      num++;
      println(num + ". working on File: " + fileNames[num]);
    } else if (keyCode == LEFT && num > 0) {
      num--;
      println(num + ". working on File: " + fileNames[num]);
    } else if (keyCode == DOWN) {
            
      //f = new File(dataPath(lastImg));
      //System.gc();
      //f.delete();
      //println(f);
      //if (f.exists()) {
      //  println("Found file to trash");
        
      //  println("Image Trashed...");
      //} else {println("Can't find file in folder...");}
      //cropped = null;
      
    }
  }

  //println(imgContainer.size(),num);
}


void drawRects() {
  noStroke();
  fill(stateColor[1], 80);

  for (int i = 0; i < points[num].size()/4; i++) {
    int a = points[num].get(i*4);
    int b = points[num].get(i*4+1);
    int c = points[num].get(i*4+2);
    int d = points[num].get(i*4+3);
    rect(a, b, c, d);
  }
  noFill();
  stroke(stateColor[1]);
}
