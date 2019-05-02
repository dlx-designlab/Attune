/** //<>// //<>// //<>// //<>// //<>//
 * Image Filtering
 * This sketch performs some image filtering (threshold, blur) and contour detection
 * 
 * @author: Jordi Tost (@jorditost)
 * @url: https://github.com/jorditost/ImageFiltering/tree/master/ImageFiltering
 *
 * University of Applied Sciences Potsdam, 2014
 *
 * It requires the ControlP5 Processing library:
 * http://www.sojamo.de/libraries/controlP5/
 */

import gab.opencv.*;
import java.awt.Rectangle;
import processing.video.*;
import controlP5.*;
import java.util.Date;
import org.opencv.imgproc.Imgproc;

OpenCV opencv;
Capture microscope;
boolean live = false;
//Capture video;
PImage curImage;
PImage cropped;
PImage rotatedImage;
PImage img;
PGraphics pg;
IntList points = new IntList();
int num = 0;
int imageWidth = 0;
int imageHeight = 0;


PImage src, preProcessedImage, processedImage, contoursImage, g, s;
ArrayList<Contour> contours;
ArrayList<Parameters> parametersData;
ArrayList<Contour> contoursDst;
ArrayList<Line> linesData;
int straightLineNum = 0;
boolean firstDraw;
// List of detected contours parsed as blobs (every frame)
ArrayList<Contour> newBlobContours;
ArrayList<Blob> blobList;
// Number of blobs detected over all time. Used to set IDs.
int blobCount = 0;

float pixels2um = 0.8;
float minLength = 12.6984127*pixels2um;
float maxLength = 368.8740741*pixels2um;
float minWidth = 3.720634921*pixels2um;
float maxWidth = 33.10617284*pixels2um;
float minDiameter = 3.439153439*pixels2um;
float maxDiameter = 31.11111111*pixels2um;
float minDensity = 2.5*pixels2um;
float maxDensity = 21.8*pixels2um;
float contrast = 1.8;//1.35;
int brightnessValue = 0;
int threshold = 75;
boolean useAdaptiveThreshold = true; // use Adaptive thresholding
boolean useBrightness = false; // use brightness
int thresholdBlockSize = 150;//241;
int thresholdConstant = 5;
int blobSizeThreshold = int(115*pixels2um);
int blurSize = 0;//4
boolean useChannel = true;
float scaleView;// = 0.5;
int pathLen;

// Control vars
ControlP5 cp5;
DropdownList ddlImageName;
DropdownList ddlID;
//int movieCounter = 37;
int buttonColor;
int buttonBgColor;

String path;
ArrayList<File> allFiles;
StringList allIds = new StringList();
IntList filesPerId = new IntList();
IntList idStartIndex = new IntList();
int idNo = 0;
int startIndex = 0;

String fileName;// = "/volumes/SARIT'S FAT/Projects/Kekkan/3R_VIEWTY Tests/2019-03-18-18-28-29.png"; // first movie 
//String fileName = "/volumes/SARIT'S FAT/Projects/Kekkan/Matsunaga Lab Data/1/cas_20190226131340820.bmp"; // first movie 
//String fileName = "mat_caps.avi";
String folderName;
int movieNumber = 1;

boolean useFileName = false;
boolean calibrated = false;
boolean parametersPrintout = false;
boolean display = false;

int roiX = 0;
int roiY = 0;
int roiWidth = 0;
int roiHeight = 0;
boolean useROI = false;
boolean drawRoi = false;
int offset = 200;


void setup() {
  String initFileName = "init.txt";  
  String[] lines = loadStrings(initFileName);
  if (lines != null) {
    fileName = lines[0];
    path = lines[1];
    imageWidth = int(lines[2]);
    imageHeight = int(lines[3]);
    pathLen = int(lines[4]);
    contrast = float(lines[5]);
    thresholdBlockSize = int(lines[6]);
    pixels2um = float(lines[7]);
  }
  minLength = int(13*pixels2um);
  maxLength = int(368*pixels2um);
  blobSizeThreshold = int(115*pixels2um);

  size(1480, 720);
  int pgw = max(imageWidth, 1280);
  int pgh = max(imageHeight, 720);
  pg = createGraphics(imageWidth, imageHeight);
  int h = height/2;
  scaleView = (float)h/imageHeight;

  initPathData();
  // Init Controls
  cp5 = new ControlP5(this);
  initControls();
  // Set thresholding
  toggleAdaptiveThreshold(useAdaptiveThreshold);
  // Set contrast/brightness
  toggleBrightness(useBrightness);
  // Blobs list
  //  blobList = new ArrayList<Blob>();
  //  contours = new ArrayList<Contour>();

  String[] cameras = Capture.list();

  if (cameras == null) {
    println("Failed to retrieve the list of available cameras, will try the default...");
    //    microscope = new Capture(this, 640, 480);
    initImage();
    reCalculateDisplay();
  } 
  if (cameras.length == 0) {
    println("There are no cameras available for capture.");
    exit();
  } else {
    println("Available cameras:");
    printArray(cameras);

    // The camera can be initialized directly using an element
    // from the array returned by list():
    microscope = new Capture(this, cameras[15]);
    // Or, the settings can be defined based on the text in the list
    //cam = new Capture(this, 640, 480, "Built-in iSight", 30);

    // Start capturing the images from the camera
    microscope.start();
    opencv = new OpenCV(this, 1920, 1080);
    live = true;
  }
}

void initImage() {
  curImage = loadImage(fileName);
  loadCalData();
  opencv = new OpenCV(this, curImage);
  //  reCalculateDisplay();
}

void reCalculateDisplay() {
  processOpenCV();
  displayImages();
}

void loadCalData() {
  String logFileName = "cal" + fileName + ".txt";  
  String[] lines = loadStrings(logFileName);
  if (lines != null) {
    calibrated = true;
    for (int i=0; i<lines.length; i++) {
      String[] pieces = split(lines[i], ' ');
      if (pieces.length == 2) {
        switch(i) {
        case 0: 
          cp5.getController("contrast").setValue(float(pieces[1]));
          break;
        case 1:
          String[] mb = match(pieces[1], "true");
          if (mb != null) {
            useBrightness = true;
          } else {
            useBrightness = false;
          }
          toggleBrightness(useBrightness);
          break;
        case 2: 
          cp5.getController("brightnessValue").setValue(float(pieces[1]));
          break;
        case 3: 
          cp5.getController("threshold").setValue(float(pieces[1]));
          break;
        case 4:
          String[] mat = match(pieces[1], "true");
          if (mat != null) {
            useAdaptiveThreshold = true; // use Adaptive thresholding
          } else {
            useAdaptiveThreshold = false;
          }
          toggleAdaptiveThreshold(useAdaptiveThreshold);
          break;
        case 5: 
          cp5.getController("thresholdBlockSize").setValue(float(pieces[1]));
          break;
        case 6: 
          cp5.getController("thresholdConstant").setValue(float(pieces[1]));
          break;
        case 7: 
          cp5.getController("blobSizeThreshold").setValue(float(pieces[1]));
          break;
        case 8: 
          cp5.getController("blurSize").setValue(float(pieces[1]));
          break;
        }
      }
    }
  } else {
    // if no previous calibration then load default values
    calibrated = false;
    cp5.getController("contrast").setValue(contrast);
    cp5.getController("brightnessValue").setValue(0);
    cp5.getController("threshold").setValue(75);
    cp5.getController("thresholdBlockSize").setValue(thresholdBlockSize);//(241);
    cp5.getController("thresholdConstant").setValue(5);
    cp5.getController("blobSizeThreshold").setValue(int(115*pixels2um));
    cp5.getController("blurSize").setValue(0);//(4);

    useAdaptiveThreshold = true; // use Adaptive thresholding
    toggleAdaptiveThreshold(useAdaptiveThreshold);
    useBrightness = false; // use brightness
    toggleBrightness(useBrightness);
  }
}

void draw() {
  // Draw
  if (microscope.available() == true) {
    microscope.read();
    reCalculateDisplay();
    display = true;
  }

  if (drawRoi) {
    pushMatrix();
    translate(offset, 0);
    pushMatrix();
    scale(scaleView);
    if (live) {
      image(microscope, 0, 0);
    } else {
      image(curImage, 0, 0);
    }
    popMatrix();
    popMatrix();
  }

  fill(128);
  noStroke();
  rect(0, 0, offset, height);

  fill(255);
  text(fileName, 10, height-50); 
  text(frameRate, 10, 40);

  text("Use c/C to toggle channel/gray", 10, height-70);
  text("Use d/D to toggle display mode", 10, height-85);
  text("Use p/P to see parameters", 10, height-100);

  // Display contours in the lower right window
  if (display) {
    pushMatrix();
    translate(offset, 0);
    pushMatrix();
    scale(scaleView);
    /*   if (live) {
     image(microscope, 0, 0);
     }*/
    translate(src.width, src.height);
    displayContours();
    displayContoursBoundingBoxes();
    //    displayBlobs();
    //       displayLines();
    popMatrix();
    popMatrix();
  }


  //noLoop();
}

void processOpenCV() {
  pg.beginDraw();
  if (useROI) {
    if (live) {
      opencv.loadImage(microscope);
    } else {
      opencv.loadImage(curImage);
    }
    opencv.setROI(roiX, roiY, roiWidth, roiHeight);
    /*    pg.image(cropped, 0, 0);
     img = pg.get();
     opencv = new OpenCV(this, img);*/
  } else {
    if (live) {
      pg.image(microscope, 0, 0);
    } else {
      pg.image(curImage, 0, 0);
    }
    img = pg.get();
    opencv.loadImage(img); 
    straightLineNum = 0;
  }
  src = opencv.getSnapshot();

  ///////////////////////////////
  // <1> PRE-PROCESS IMAGE
  // - Grey channel 
  // - Brightness / Contrast
  ///////////////////////////////

  if (useChannel) {
    // Green channel
    g = opencv.getSnapshot(opencv.getG());
    opencv.loadImage(g);
  } else {
    // Gray channel
    opencv.gray();
  }

  if (useBrightness) {
    opencv.brightness(brightnessValue);
  } else {
    opencv.contrast(contrast);
  }

  // Save snapshot for display
  preProcessedImage = opencv.getSnapshot();

  ///////////////////////////////
  // <2> PROCESS IMAGE
  // - Threshold
  // - Noise Supression
  ///////////////////////////////

  // Adaptive threshold - Good when non-uniform illumination
  if (useAdaptiveThreshold) {

    // Block size must be odd and greater than 3
    if (thresholdBlockSize%2 == 0) thresholdBlockSize++;
    if (thresholdBlockSize < 3) thresholdBlockSize = 3;

    opencv.adaptiveThreshold(thresholdBlockSize, thresholdConstant);// maybe 150

    // Basic threshold - range [0, 255]
  } else {
    opencv.threshold(threshold);
  }

  // Invert (black bg, white blobs)
  opencv.invert();
  opencv.morphX(Imgproc.MORPH_GRADIENT, Imgproc.MORPH_RECT, 3, 3);//not bad
  // Blur
  opencv.blur(blurSize);

  // Save snapshot for display
  processedImage = opencv.getSnapshot();

  ///////////////////////////////
  // <3> FIND CONTOURS  
  ///////////////////////////////
  //  pg.pushMatrix();
  //  pg.image(processedImage, 0, 0);

  /*  linesData = opencv.findLines(10, minLength, 20);
   straightLineNum = analyzeLines(linesData);
   while (straightLineNum < 20) {
   pg.rotate(radians(1));
   println("before");
   straightLineNum = analyzeLines(linesData);
   }*/
  //     if (!useROI) {

  pg.background(0);
  pg.image(processedImage, 0, 0);
  img = pg.get();
  //  pg.popMatrix();
  opencv.loadImage(img); 
  //     }
  // Passing 'true' sorts them by descending area.
  contours = opencv.findContours(false, true);
  if (calibrated && parametersPrintout) {
    println("found " + contours.size() + " contours");
  }

  // Save snapshot for display
  contoursImage = opencv.getSnapshot();
  pg.endDraw();
}

void initPathData() {
  allFiles = listFilesRecursive(path);
  println(path, allFiles.size());
  String tempS = "";
  int counter = 0;
  for (File f : allFiles) {
    String fPath = f.getAbsolutePath();
    String[] q = splitTokens(fPath, "/");
    if (q[pathLen].equals(tempS)) {
      filesPerId.increment(filesPerId.size()-1);
      println(filesPerId.get(filesPerId.size()-1), f.getName());
    } else {
      filesPerId.append(1);
      idStartIndex.append(1);
      idStartIndex.set(idStartIndex.size()-1, counter);
      tempS = q[pathLen];
      allIds.append(q[pathLen]);
      println(q[pathLen]);
      println(counter, f.getName());
    }
    counter++;
  }
}

// Function to get a list of all files in a directory and all subdirectories
ArrayList<File> listFilesRecursive(String dir) {
  ArrayList<File> fileList = new ArrayList<File>(); 
  recurseDir(fileList, dir);
  return fileList;
}

// Recursive function to traverse subdirectories
void recurseDir(ArrayList<File> a, String dir) {
  File file = new File(dir);
  if (file.isDirectory()) {
    // If you want to include directories in the list
    //   a.add(file);  
    File[] subfiles = file.listFiles();
    for (int i = 0; i < subfiles.length; i++) {
      // Call this function on all files in this directory
      recurseDir(a, subfiles[i].getAbsolutePath());
    }
  } else {
    String subPath = file.getAbsolutePath();
    String fName = file.getName();  
    if (!fName.toLowerCase().startsWith("._")) 
      if (subPath.toLowerCase().endsWith(".bmp") || 
        subPath.toLowerCase().endsWith(".jpg") || 
        subPath.toLowerCase().endsWith(".png")) {
        a.add(file);
      }
  }
}



/////////////////////
// Display Methods
/////////////////////

void displayImages() {
  background(128);
  pushMatrix();
  // Leave space for ControlP5 sliders
  // translate(width-(src.width*scaleView), 0);
  translate(offset, 0);

  pushMatrix();
  scale(scaleView);
  if (useROI) {
    image(cropped, 0, 0);
  } else if (live) {
    image(microscope, 0, 0);
  } else {
    //  if (!live)
    image(curImage, 0, 0);
  }
  //  }
  if (display) {
    image(preProcessedImage, src.width, 0);
    image(processedImage, 0, src.height);
    //    image(src, src.width, src.height);
    image(pg, src.width, src.height, pg.width, pg.height);
  }
  popMatrix();

  stroke(255);
  fill(255);
  text("Source", 10, 25); 
  String pp;
  if (useChannel) {
    pp = "Pre-processed Image" + "-channel";
  } else {
    pp = "Pre-processed Image" + "-gray";
  }
  text(pp, src.width*scaleView + 10, 25); 
  text("Processed Image", 10, src.height*scaleView + 25); 
  text("Tracked Points", src.width*scaleView + 10, src.height*scaleView + 25);
  popMatrix();
}


//////////////////////////
// CONTROL P5 Functions
//////////////////////////

void initControls() {
  // Slider for contrast
  cp5.addSlider("contrast")
    .setLabel("contrast")
    .setPosition(20, 50)
    .setRange(0.0, 6.0)
    ;

  // Toggle to activae adaptive threshold
  cp5.addToggle("toggleBrightness")
    .setLabel("use brightness")
    .setSize(10, 10)
    .setPosition(20, 80)
    ;

  // Slider for contrast
  cp5.addSlider("brightnessValue")
    .setLabel("brightness")
    .setPosition(20, 120)
    .setRange(-255, 255)
    ;

  // Slider for threshold
  cp5.addSlider("threshold")
    .setLabel("threshold")
    .setPosition(20, 156)
    .setRange(0, 255)
    ;

  // Toggle to activae adaptive threshold
  cp5.addToggle("toggleAdaptiveThreshold")
    .setLabel("use adaptive threshold")
    .setSize(10, 10)
    .setPosition(20, 180)
    ;

  // Slider for adaptive threshold block size
  cp5.addSlider("thresholdBlockSize")
    .setLabel("a.t. block size")
    .setPosition(20, 210)
    .setRange(1, 700)
    ;

  // Slider for adaptive threshold constant
  cp5.addSlider("thresholdConstant")
    .setLabel("a.t. constant")
    .setPosition(20, 240)
    .setRange(-100, 100)
    ;

  // Slider for blur size
  cp5.addSlider("blurSize")
    .setLabel("blur size")
    .setPosition(20, 290)
    .setRange(1, 20)
    ;

  // Slider for minimum blob size
  cp5.addSlider("blobSizeThreshold")
    .setLabel("min blob length")
    .setPosition(20, 320)
    .setRange(minLength, maxLength) // changed to fit min-max length
    ;

  // create a DropdownList, 
  ddlID = cp5.addDropdownList("IDs")
    .setPosition(20, 370)
    .setSize(150, 100)
    ;

  customizeIddl(ddlID); // customize the first list

  // create a DropdownList, 
  ddlImageName = cp5.addDropdownList("images")
    .setPosition(20, 500)
    .setSize(150, 100)
    ;

  //  customize(ddlImageName); // customize the first list


  // create a new button with name 'buttonA'
  cp5.addButton("Calibrate")
    .setValue(0)
    .setPosition(20, 340)
    .setSize(160, 16)
    ;

  // Store the default background color, we gonna need it later
  buttonColor = cp5.getController("contrast").getColor().getForeground();
  buttonBgColor = cp5.getController("contrast").getColor().getBackground();
}

void customize(DropdownList ddl, int sIndex, int eIndex) {
  // a convenience function to customize a DropdownList
  //  ddl.setBackgroundColor(color(190));
  ddl.setItemHeight(20);
  ddl.setBarHeight(15);
  ddl.getCaptionLabel().set("images");
  ddl.clear();
  for (int i = sIndex; i < eIndex; i++) {
    ddl.addItem(allFiles.get(i).getName(), i-sIndex);
  }
  //  fileName = allFiles.get(sIndex).getName();
  //  fileName = "/volumes/SARIT'S FAT/Projects/Kekkan/Matsunaga Lab Data/1/cas_20190226131342.wmv"; 
  ddl.setColorBackground(color(150, 150));
  ddl.setColorActive(color(100, 100));
}

void customizeIddl(DropdownList ddl) {
  // a convenience function to customize a DropdownList
  //  ddl.setBackgroundColor(color(190));
  ddl.setItemHeight(20);
  ddl.setBarHeight(15);
  ddl.getCaptionLabel().set("IDs");
  int i = 0;
  for (String s : allIds) {
    ddl.addItem(s, i);
    i++;
  }
  ddl.setColorBackground(color(150, 150));
  ddl.setColorActive(color(100, 100));
}

void toggleAdaptiveThreshold(boolean theFlag) {

  useAdaptiveThreshold = theFlag;

  if (useAdaptiveThreshold) {

    // Lock basic threshold
    setLock(cp5.getController("threshold"), true);

    // Unlock adaptive threshold
    setLock(cp5.getController("thresholdBlockSize"), false);
    setLock(cp5.getController("thresholdConstant"), false);
  } else {

    // Unlock basic threshold
    setLock(cp5.getController("threshold"), false);

    // Lock adaptive threshold
    setLock(cp5.getController("thresholdBlockSize"), true);
    setLock(cp5.getController("thresholdConstant"), true);
  }
}

void setLock(Controller theController, boolean theValue) {

  theController.setLock(theValue);

  if (theValue) {
    theController.setColorBackground(color(150, 150));
    theController.setColorForeground(color(100, 100));
  } else {
    theController.setColorBackground(color(buttonBgColor));
    theController.setColorForeground(color(buttonColor));
  }
}


void toggleBrightness(boolean theFlag) {

  useBrightness = theFlag;

  if (useBrightness) {

    setLock(cp5.getController("brightnessValue"), false);
    setLock(cp5.getController("contrast"), true);
  } else {

    setLock(cp5.getController("contrast"), false);
    setLock(cp5.getController("brightnessValue"), true);
  }
}

void controlEvent(ControlEvent theEvent) {
  // DropdownList is of type ControlGroup.
  // A controlEvent will be triggered from inside the ControlGroup class.
  // therefore you need to check the originator of the Event with
  // if (theEvent.isGroup())
  // to avoid an error message thrown by controlP5.

  if (theEvent.isGroup()) {
    // check if the Event was triggered from a ControlGroup
    //    println("event from group : "+theEvent.getGroup().getValue()+" from "+theEvent.getGroup());
  } else if (theEvent.isController()) {
    //    println("event from controller : "+theEvent.getController().getValue()+" from "+theEvent.getController());
    if (theEvent.getController() == ddlID) {
      idNo = (int)(theEvent.getController().getValue());
      /*      String ts = allIds.get(idNo);
       if (ts == "1920") {
       scaleView = 0.66;
       }*/
      int noOfFiles = filesPerId.get(idNo);
      startIndex = idStartIndex.get(idNo);
      println(allIds.get(idNo));
      customize(ddlImageName, startIndex, startIndex+noOfFiles); // customize the first list
    } else if (theEvent.getController() == ddlImageName) {
      int fileNo = (int)(theEvent.getController().getValue());
      fileName = allFiles.get(startIndex+fileNo).getAbsolutePath();
      println(fileName);
      initImage();
    }
  }
  reCalculateDisplay();
}

public void Calibrate(int theValue) {

  String[] lines = new String[9];
  lines[0] = "contrast " + str(contrast);
  lines[1] = "useBrightness " + str(useBrightness);
  lines[2] = "brightnessValue " + str(brightnessValue);
  lines[3] = "threshold " + str(threshold);
  lines[4] = "useAdaptiveThreshold " + str(useAdaptiveThreshold);
  lines[5] = "thresholdBlockSize " + str(thresholdBlockSize);
  lines[6] = "thresholdConstant " + str(thresholdConstant);
  lines[7] = "blobSizeThreshold " + str(blobSizeThreshold);
  lines[8] = "blurSize " + str(blurSize);

  String logFileName = "cal" + fileName + ".txt";
  saveStrings(logFileName, lines);
  saveFrame("calibration/" + fileName + "Frames####.png");
  calibrated = true;
}


void keyPressed() {
  if (key == 'p' || key == 'P') {
    parametersPrintout = true;
  }
  if (parametersPrintout && !calibrated) {
    println("This file has not yet calibrated");
  }

  if (key == 'c' || key == 'C') {
    useChannel = !useChannel;
  }
  if (key == 'd' || key == 'D') {
    display = !display;
  }
  if (key == 'r' || key == 'R') {
    useROI = false;
    opencv.releaseROI();
    int h = height/2;
    scaleView = (float)h/imageHeight;
    blobSizeThreshold = int(177*pixels2um);
    cp5.getController("blobSizeThreshold").setValue(blobSizeThreshold);
    reCalculateDisplay();
  }
}

void mousePressed() {
  if (!useROI && (mouseX >= offset)) {
    noFill();
    stroke(255, 0, 0);
    roiX = mouseX;
    roiY = mouseY;

    drawRoi = true;
  }
}

void mouseDragged() {
  if (!useROI && drawRoi) {
    noFill();
    stroke(255, 0, 0);
    rect(roiX, roiY, mouseX-roiX, mouseY-roiY);
  }
}

void mouseReleased() {
  if (!useROI && drawRoi) {
    int x, y, w, h;
    x = min(roiX, mouseX);
    y = min(roiY, mouseY);
    if (mouseX > roiX) w = mouseX - roiX;
    else w = roiX - mouseX;
    if (mouseY > roiY) h = mouseY - roiY;
    else h = roiY - mouseY;

    h = constrain(h, w*height/(width-offset), w*height/(width-offset));

    roiX = (int)((x-offset) / scaleView);
    roiY = (int)(y / scaleView);
    noStroke();
    roiWidth = (int)(w / scaleView);
    roiHeight = (int)(h / scaleView);
    if (live) {
      cropped = microscope.get(roiX, roiY, roiWidth, roiHeight);
    } else {
      cropped = curImage.get(roiX, roiY, roiWidth, roiHeight);
    }
    drawRoi = false;
    useROI = true;
    float t = (width-offset)/2;
    scaleView = t/roiWidth;
    blobSizeThreshold = int(blobSizeThreshold*scaleView);
    cp5.getController("blobSizeThreshold").setValue(blobSizeThreshold);
    reCalculateDisplay();
  }
}
