////////////////////////// //<>//
// CONTROL P5 Functions
//////////////////////////

void initControls(String[] cams) {

  PFont pfont = createFont("ArialNarrow", 20, true);
  //  println(PFont.list());

  ddlCameras = cp5.addDropdownList("cameras")
    .setPosition(20, 420)
    .setSize(240, 100)
    //    .setFont(pfont)
    ;

  customizeCamerasDdl(ddlCameras, cams); // customize the first list

  cp5.addButton("Start")
    .setValue(100)
    .setPosition(20, 40)
    .setSize(100, 50)
    .setColorLabel(100)
    //    .setUpper(false);
    .setFont(pfont)
    //    .hide()
    ;


  cp5.addTextfield("ID")
    .setPosition(20, 100)
    .setSize(140, 60)
    .setAutoClear(false)
    .setFocus(true)
    .setFont(pfont)
    ;
  cp5.addBang("clear")
    .setPosition(170, 100)
    .setSize(100, 60)
    .getCaptionLabel().align(ControlP5.CENTER, ControlP5.CENTER)
    .setFont(pfont)
    ;    

  cTimer = new ControlTimer();
  cTimer.setSpeedOfTime(1);
  timerText = new Textlabel(cp5, "--", 100, 100);
  timerText.setPosition(20, 360);
  messageText = new Textlabel(cp5, "  ", 100, 100);
  messageText.setPosition(20, 380);
  //  messageText.setColorValue(color(255,0,0));
  messageText.setFont(pfont);
  frameText = new Textlabel(cp5, "  ", 100, 100);
  frameText.setPosition(10, 10);
//  frameText.setFont
//  textFont(pfont);
}

void customizeCamerasDdl(DropdownList ddl, String[] cams) {
  ddl.setItemHeight(20);
  ddl.setBarHeight(15);
  ddl.getCaptionLabel().set("Cameras");
  ddl.addItems(cams);
  ddl.setColorBackground(color(150, 150));
  ddl.setColorActive(color(100, 100));
}

void controlEvent(ControlEvent theEvent) {
  if (theEvent.isGroup()) {
  } else if (theEvent.isController()) {
    if (theEvent.getController() == ddlCameras) {
      curCam = cameras[(int)(theEvent.getController().getValue())];
      String[] curCamElements = split(curCam, ",");
      camName = curCamElements[0];
      String[] tmpName = split(camName, "=");
      camName = tmpName[1];

      String[] tmpSize = split(curCamElements[1], "=");
      String[] tmpSize2 = split(tmpSize[1], "x");
      inImageWidth = int(tmpSize2[0]);
      inImageHeight = int(tmpSize2[1]);
      roiWidth = inImageWidth/2;
      roiHeight = inImageHeight/2;


      String[] tmpFps = split(curCamElements[2], "=");
      inFps = int(tmpFps[1]);
      //      frameRate(inFps);

      startMicroscopeImage();
    }
  }
}

public void startNewSession() {
  saveFrame(sessionFolder+"#1-"+cTimer.millis()+".png");
  if (live) {
    curState = NEW_SESSION;
    messageText.setValue("Press R/r to RECORD");
    cTimer.reset();
    available = false;
  } else {
    messageText.setValue("Turn Image ON!");
  }
}

public void clear() {
  cp5.get(Textfield.class, "ID").clear();
  cp5.get(Button.class, "Start").setLabel("start");
  cp5.get(Button.class, "Start").setColorLabel(100);
}

public void ID(String theText) {
  sessionID = theText;
  sessionFolder = dataPath("")+"/"+sessionID+"/";
  cp5.get(Button.class, "Start").setLabel(sessionID);
  cp5.get(Button.class, "Start").setColorLabel(255);
  cp5.getController("Start").getCaptionLabel().toUpperCase(false);
  available = true;
}

public void Start() {
  cp5.getController("Start").getCaptionLabel().toUpperCase(true);
  if (available) {
    cp5.get(Button.class, "Start").setLabel("stop");
    startNewSession();
  } else {
    cp5.get(Button.class, "Start").setLabel("start");
    clear();
  }
}

void keyPressed() {
  if (key == 'r' || key == 'R') {
    if (curState == NEW_SESSION || curState == PROCESS_SESSION) {
      curState = RECORD_SESSION;
      messageText.setValue("Recording...");
      videoExport = new VideoExport(this, sessionFolder+cTimer.millis()+".mp4", microscope);
      videoExport.startMovie();
      startRecordingTime = millis();
    }
  }

  if (key == 's' || key == 'S') {
    if (curState == PROCESS_SESSION) {
      setOpenCVFrame();
    }
  }

  if (key == 'm' || key == 'M') {
    if (curState == PROCESS_SESSION) {
      parametersToMusic = true;
    }
  }

  if (curState == PROCESS_SESSION) {
    if (key == CODED) {
      if (keyCode == UP) {
        if (roiY > 0) {
          roiY -= moveFramePixels;
        }
      }
      if (keyCode == DOWN) {
        if (roiY < inImageHeight/2) {
          roiY += moveFramePixels;
        }
      }
      if (keyCode == LEFT) {
        if (roiX > 0) {
          roiX -= moveFramePixels;
        }
      }
      if (keyCode == RIGHT) {
        if (roiX < inImageWidth/2) {
          roiX += moveFramePixels;
        }
      }
    }
  }
}

void mousePressed() {
  if (curState == PROCESS_SESSION) {
    if (mouseX > roiX + offset && mouseX < roiX + roiWidth*scaleView + offset) {
      movingRoi = true;
      tmpRoiX = mouseX - moveFramePixels - offset;
      tmpRoiY = mouseY - moveFramePixels;
    }
  }
}

void mouseDragged() {
  if (movingRoi) {
    if (tmpRoiX >= moveFramePixels && tmpRoiX <= inImageWidth-roiWidth*scaleView+moveFramePixels) {
      tmpRoiX = mouseX - moveFramePixels - offset;
    }
    if (tmpRoiY >= moveFramePixels && tmpRoiY <= inImageHeight-roiHeight*scaleView+moveFramePixels) {
      tmpRoiY = mouseY - moveFramePixels;
    }
  }
}

void mouseReleased() {
  if (movingRoi) {
    movingRoi = false;
    roiX = tmpRoiX;
    roiY = tmpRoiY;
  }
}

void saveAndSendData(Parameters avgP) {
  float mappedLength = 0;
  float mappedWidth = 0;
  float mappedDiameter = 0;
  float mappedDensity = 0;
  mappedLength = map((float)avgP.pLength, minLength, maxLength, 0, 127);
  mappedLength = constrain(mappedLength, 0, 127);
  mappedWidth = map((float)avgP.pWidth, minWidth, maxWidth, 0, 127);
  mappedWidth = constrain(mappedWidth, 0, 127);
  mappedDiameter = map((float)avgP.pDiameter, minDiameter, maxDiameter, 0, 127);
  mappedDiameter = constrain(mappedDiameter, 0, 127);
  mappedDensity = map((float)avgP.pDensity, minDensity, maxDensity, 0, 127);
  mappedDensity = constrain(mappedDensity, 0, 127);
  println("no of cap. " + parametersData.size() + " avg length " + avgP.pLength + " avg width " + avgP.pWidth + " avg diameter " + avgP.pDiameter + " avg density " + avgP.pDensity);
  println("snd length " + mappedLength + " snd width " + mappedWidth + " snd diameter " + mappedDiameter + " snd density " + mappedDensity);

  String[] lines = new String[4];
  lines[0] = "mLength " + str(mappedLength);
  lines[1] = "mWidth " + str(mappedWidth);
  lines[2] = "mDiameter " + str(mappedDiameter);
  lines[3] = "mDensity " + str(mappedDensity);

  String logFileName = sessionFolder+"MFD-" +cTimer.millis() + ".txt";
  saveStrings(logFileName, lines);
  saveFrame(sessionFolder+"MFD-"+cTimer.millis()+".png");

  createQRCode(mappedLength, mappedWidth, mappedDiameter, mappedDensity);
}

void createQRCode(float mL, float mW, float mDi, float mDe) {
  PImage  QRCode;
  String  textToEncode = "";
  String  link = "";
  String fullQRgifPath;
  

  // example: www.servername.com/?uid=zx1234&cp=127|127|127|127
  // 1. density 2. diameter 3. width 4. length
  textToEncode = link + "/?uid=" + sessionID + "&cp=" + mDe + "|" + mDi + "|" + mW + "|" + mL;

  try {
    QRCode = zxing4p.generateQRCode(textToEncode, 100, 100);
    fullQRgifPath = sessionFolder+sessionID+cTimer.millis()+".gif";
    QRCode.save(fullQRgifPath);
    QRCode = loadImage(fullQRgifPath);
    String params[] = {"lpr", fullQRgifPath};
    exec(params);
  } 
  catch (Exception e) {  
    println("Exception: "+e);
    QRCode = null;
  }
  
  /*  String ts = timeStamp();
   saveFrame(dataPath("")+"/"+sessionID+ts+".gif");*/
}

String timeStamp() {
  return year()+nf(month(), 2)+nf(day(), 2)+nf(hour(), 2)+nf(minute(), 2)+nf(second(), 2);
} 
