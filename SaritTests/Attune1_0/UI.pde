////////////////////////// //<>// //<>//
// CONTROL P5 Functions
//////////////////////////

void initControls(String[] cams) {

  PFont pfont = createFont("ArialNarrow", 20, true);
  //  println(PFont.list());

  ddlCameras = cp5.addDropdownList("cameras")
    .setPosition(10, height-200) //900
    .setSize(240, 100)
    //    .setFont(pfont)
    ;

  customizeCamerasDdl(ddlCameras, cams); // customize the first list

  cp5.addButton("Start")
    .setValue(100)
    .setPosition(10, 40)
    .setSize(90, 50)
    .setColorLabel(100)
    //    .setUpper(false);
    .setFont(pfont)
    //    .hide()
    ;


  cp5.addTextfield("ID")
    .setPosition(10, 100)
    .setSize(90, 60)
    .setAutoClear(false)
    .setFocus(true)
    .setFont(pfont)
    ;
  cp5.addBang("clear")
    .setPosition(10, 160)
    //   .setPosition(170, 100)
    .setSize(90, 40)
    .getCaptionLabel().align(ControlP5.CENTER, ControlP5.CENTER)
    .setFont(pfont)
    ;    

  cTimer = new ControlTimer();
  cTimer.setSpeedOfTime(1);
  timerText = new Textlabel(cp5, "--", 100, 100);
  timerText.setPosition(10, 220);
  messageText = new Textlabel(cp5, "  ", 100, 100);
  messageText.setPosition(offset+20, 100);
  //  messageText.setColorValue(color(255,0,0));
  messageText.setFont(pfont);
  //frameText = new Textlabel(cp5, "  ", 100, 100);
  //frameText.setPosition(10, 10);
  cp5.addFrameRate().setInterval(10).setPosition(0, height - 10);

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
      frameRate(inFps);

      startMicroscopeImage();
      messageText.setValue("Enter uID to Start");
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
    freezeImage = false;
  } else {
    messageText.setValue("Turn Image ON!");
  }
}

public void clear() {
  if (curState < NEW_SESSION) {
    cp5.get(Textfield.class, "ID").clear();
    cp5.get(Button.class, "Start").setLabel("start");
    cp5.get(Button.class, "Start").setColorLabel(100);
  }
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
    microscope.start();
    micStopped = false;
  } else {
    cp5.get(Button.class, "Start").setLabel("start");
    clear();
    closeSession();
  }
}

void closeSession() {
  if (useROI) {
    setOpenCVFrame();
  }
  curState = NO_STATE;
  messageText.setValue("Enter uID to Start");
  freezeImage = false;
  brightnessValue = 0;
  cTimer.reset();
  pauseTime = millis();
}

void keyPressed() {
  if (key == 'r' || key == 'R') {
    if (curState == NEW_SESSION || curState == PROCESS_SESSION) {
      curState = RECORD_SESSION;
      messageText.setValue("Recording...");
      videoExport = new VideoExport(this, sessionFolder+cTimer.millis()+".mp4", microscope);
      videoExport.setFrameRate(inFps*0.6);  //assuming a drop of 60% of frames or frame rate
      videoExport.setQuality(100, 128);//100% quality
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
      messageText.setValue("Printing...");
    }
  }

  if (key == 'o' || key == 'O') {
    if (curState == PROCESS_SESSION) {
      curState = NEW_SESSION;
    }
  }

  if (key == 'f' || key == 'F') {
    if (curState == PROCESS_SESSION) {
      freezeImage = !freezeImage;
      if (freezeImage) {
        messageText.setValue("Press f/F to UNFREEZE IMAGE");
      } else {
        messageText.setValue("Press f/F to FREEZE IMAGE");
      }
    }
  }

  if (key == 'b' || key == 'B') {
    if (curState == PROCESS_SESSION) {
      brightnessValue-=5;
      //      println(brightnessValue);
    }
  }

  if (key == 'v' || key == 'V') {
    if (curState == PROCESS_SESSION) {
      brightnessValue+=5;
      //      println(brightnessValue);
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

  link = "https://attune-app.herokuapp.com/tune_downloader";
  // example: www.servername.com/?uid=zx1234&cp=127|127|127|127
  // 1. density 2. diameter 3. width 4. length
  textToEncode = link + "?uid=" + sessionID + "&cp=" + mDe + "|" + mDi + "|" + mW + "|" + mL;

  try {
    QRCode = zxing4p.generateQRCode(textToEncode, 150, 150);
    fullQRgifPath = sessionFolder+sessionID+cTimer.millis()+".gif";

    PGraphics pg;
    QRCode.save(fullQRgifPath);
    QRCode = loadImage(fullQRgifPath);
    pg = createGraphics(150, 165);
    pg.beginDraw();
    pg.background(255);
    pg.image(QRCode, 0, 0); 
    pg.fill(0);
    PFont mono = createFont("Helvetica", 12, true);
    pg.textFont(mono);
    pg.textSize(12);
    float tw = textWidth(sessionID);
    pg.text(sessionID, (150-tw)/2, 155);
    pg.endDraw();
    fullQRgifPath = sessionFolder+sessionID+cTimer.millis()+"t.gif";
    pg.save(fullQRgifPath);
    //    QRCode.save(fullQRgifPath);
    //    QRCode = loadImage(fullQRgifPath);
    // lp -o media=Custom.WIDTHxLENGTHmm filename 100x180

    String params[] = {"lp", "-o media=Custom.100x98mm", fullQRgifPath};
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
