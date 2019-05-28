/*
Attune Open Campus, Tokyo May 31st-June 1st
 */

import gab.opencv.*;
import java.awt.Rectangle;
import processing.video.*;
import controlP5.*;
import java.util.Date;
import org.opencv.imgproc.Imgproc;
import org.opencv.core.MatOfPoint2f;
import org.opencv.core.Point;
import org.opencv.core.RotatedRect;
import com.hamoid.*;
import com.cage.zxing4p3.*;
import java.io.InputStreamReader;

// QR code
ZXING4P zxing4p;

// Control vars
ControlP5 cp5;
DropdownList ddlCameras;
ControlTimer cTimer;
Textlabel timerText;
Textlabel messageText;
Textlabel frameText;

String[] cameras;
String camName;
int inImageWidth;
int inImageHeight;
int inFps;
OpenCV opencv;
Capture microscope;
VideoExport videoExport;
boolean live = false;
boolean display = false;
boolean available = false;
boolean parametersToMusic = false;
PGraphics pg;
float scaleView;
PImage curImage;
PImage croppedImage;
PImage img;
PImage src, preProcessedImage, processedImage, contoursImage, g, s;
int offset = 300;
String curCam;
String sessionID = "";
String sessionFolder = "";

float pixels2um = 0.6184;
float minLength = 12.6984127*pixels2um;
float maxLength = 368.8740741*pixels2um;
float minWidth = 3.720634921*pixels2um;
float maxWidth = 33.10617284*pixels2um;
float minDiameter = 3.439153439*pixels2um;
float maxDiameter = 31.11111111*pixels2um;
float minDensity = 2.5*pixels2um;
float maxDensity = 21.8*pixels2um;
float thresholdLength = 115;
int roiX = 0;
int roiY = 0;
int tmpRoiX = 0;
int tmpRoiY = 0;
int roiWidth = 0;
int roiHeight = 0;
int prevRoiX;
int prevRoiY;
boolean useROI = false;
ArrayList<Contour> contours;
ArrayList<Parameters> parametersData;
double densityPerFrame = 0;
float contrast = 1.8;//1.35;
int thresholdBlockSize = 151;//241;
int thresholdConstant = 5;
int blobSizeThreshold = int(thresholdLength*pixels2um);
int blurSize = 0;//4
int moveFramePixels = 10;

int startRecordingTime = 0;
int timeToRecord = 6000; //6seconds
boolean movingRoi = false;

// STATES
int NO_STATE = 999;
int NEW_SESSION = 0;
int RECORD_SESSION = 1;
int PROCESS_SESSION = 2;
int QR_SESSION =3;
int curState = NO_STATE;

void setup() {
  size(1260, 540);
  String initFileName = "init.txt";  
  String[] lines = loadStrings(initFileName);
  if (lines != null) {
    /*    imageWidth = int(lines[2]);
     imageHeight = int(lines[3]);
     pathLen = int(lines[4]);
     contrast = float(lines[5]);
     thresholdBlockSize = int(lines[6]);
     pixels2um = float(lines[7]);*/
  }

  cp5 = new ControlP5(this);
  cameras = Capture.list();

  initControls(cameras);
  zxing4p = new ZXING4P();
}

void draw() {
  background(128);

  if (live) {
    if (microscope.available() == true) {
      microscope.read();
      curImage = microscope.get(0, 0, inImageWidth, inImageHeight);
      if (useROI) {
        croppedImage = curImage.get(roiX, roiY, roiWidth, roiHeight);
      }
      if (curState == PROCESS_SESSION) {
        processOpenCV();
      }
      display = true;
    }
  }
  if (display/* && curState != RECORD_SESSION*/) {
    pushMatrix();
    translate(offset, 0);
    pushMatrix();
    scale(scaleView);
    if (useROI) {
      image(croppedImage, 0, 0);
    } else {
      image(curImage, 0, 0);
    }
    /*    if (curState == PROCESS_SESSION) {
     image(contoursImage, 0, 0);
     } else {
     image(curImage, 0, 0);
     }*/
    if (curState == PROCESS_SESSION && !useROI) {
      noFill();
      stroke(255, 0, 0);
      strokeWeight(2);
      strokeJoin(ROUND);
      if (movingRoi) {
        rect(tmpRoiX, tmpRoiY, roiWidth, roiHeight);
      } else {
        rect(roiX, roiY, roiWidth, roiHeight);
      }
    }
    if (curState == PROCESS_SESSION) {
      displayContours();

//      if ((frameCount % 50)/ (float)50 == 0) {
      if (frameCount%10 == 0) {
        messageText.setValue("Use arrows & mouse to MOVE FRAME");
      } else 
        messageText.setValue("Press s/S to SET FRAME");
    }
    popMatrix();
    popMatrix();
  }

  timerText.setValue(cTimer.toString());
  timerText.draw(this);
  messageText.draw(this);
  frameText.setValue(str(frameRate));
  frameText.draw(this);
  if (curState == RECORD_SESSION) {
    if (frameCount%2 == 0) {
      fill(255, 0, 0);
      noStroke();
      ellipse(offset + 40, 40, 40, 40);
    }
    videoExport.saveFrame();
  }

//  text(frameRate, 10, 10);

  //  text(cp5.get(Textfield.class,"ID").getText(), 360,130);
  //  text(sessionID, 360,180);

  if (curState == RECORD_SESSION && (millis() - startRecordingTime > timeToRecord)) {
    curState = PROCESS_SESSION;
    videoExport.endMovie();
  }
}




void startMicroscopeImage() {
  //  microscope = new Capture(this, curCam);
  microscope = new Capture(this, inImageWidth, inImageHeight, camName, inFps);
  microscope.start();
  opencv = new OpenCV(this, inImageWidth, inImageHeight);
  pg = createGraphics(inImageWidth, inImageHeight);
  scaleView = (float)height/inImageHeight;
  live = true;
  if (available) {
    startNewSession();
  }
}

void processOpenCV() {
  pg.beginDraw();
  if (useROI) {
    opencv.loadImage(curImage);
    opencv.setROI(roiX, roiY, roiWidth, roiHeight);
  } else {
    pg.image(curImage, 0, 0);
    img = pg.get();
    opencv.loadImage(img);
  }
  src = opencv.getSnapshot();

  ///////////////////////////////
  // <1> PRE-PROCESS IMAGE
  // - Grey channel 
  // - Brightness / Contrast
  ///////////////////////////////
  // Green channel
  g = opencv.getSnapshot(opencv.getG());
  opencv.loadImage(g);
  opencv.contrast(contrast);
  preProcessedImage = opencv.getSnapshot();
  ///////////////////////////////
  // <2> PROCESS IMAGE
  // - Threshold
  // - Noise Supression
  ///////////////////////////////
  opencv.adaptiveThreshold(thresholdBlockSize, thresholdConstant);
  // Invert (black bg, white blobs)
  opencv.invert();
  opencv.morphX(Imgproc.MORPH_GRADIENT, Imgproc.MORPH_RECT, 3, 3);//not bad
  // Blur
  //  opencv.blur(blurSize);
  // Save snapshot for display
  processedImage = opencv.getSnapshot();

  ///////////////////////////////
  // <3> FIND CONTOURS  
  ///////////////////////////////
  pg.background(0);
  pg.image(processedImage, 0, 0);
  img = pg.get();
  opencv.loadImage(img); 
  contours = opencv.findContours(false, true);
  contoursImage = opencv.getSnapshot();
  pg.endDraw();
}

void setOpenCVFrame() {
  if (useROI) {
    useROI = false;
    opencv.releaseROI();
    roiX = prevRoiX;
    roiY = prevRoiY;
    scaleView = (float)height/inImageHeight;
    blobSizeThreshold = int(thresholdLength*pixels2um);
  } else {
    prevRoiX = roiX;
    prevRoiY = roiY;
    croppedImage = curImage.get(roiX, roiY, roiWidth, roiHeight);
    useROI = true;
    scaleView = (float)height/roiHeight;
    blobSizeThreshold *= inImageHeight/roiHeight;
  }
}
