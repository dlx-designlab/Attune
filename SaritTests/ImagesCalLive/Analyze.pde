void displayContours() {

  parametersData = new ArrayList<Parameters>();
  densityPerFrame = 0;
  for (int i=0; i<contours.size(); i++) {

    Contour contour = contours.get(i);

    noFill();
    stroke(0, 255, 0);
    strokeWeight(1);
    contour.draw();
/*    Contour convexHullCuntor = contour.getConvexHull();
    stroke(0, 0, 255);
    convexHullCuntor.draw();*/
    Rectangle r = contour.getBoundingBox();

    stroke(255, 0, 0);
    fill(255, 0, 0, 100);
    strokeWeight(1);
    rect(r.x, r.y, r.width, r.height);    
    double contourSat = getSaturation(r);
    float contourArea = 0;
    contourArea = contour.area();
    densityPerFrame += contourArea;

    if (//(contour.area() > 0.9 * src.width * src.height) ||
      (/*r.width < minWidth && */r.height < blobSizeThreshold))
      continue;

    Point[] cPoints = new Point[contour.numPoints()];
    ArrayList <PVector> cPointsList;
    cPointsList = contour.getPoints();
    for (int j=0;j<contour.numPoints();j++) {
      cPoints[j] = new Point();
      cPoints[j].x = cPointsList.get(j).x;
      cPoints[j].y = cPointsList.get(j).y;
    }
    MatOfPoint2f mat = new MatOfPoint2f();
    mat.fromArray(cPoints);
    double cLen = Imgproc.arcLength(mat, true);
//    float contourArea = 0;
    double area = Imgproc.contourArea(mat);
 //   contourArea = contour.area();

    Parameters contourParameters = new Parameters();
    contourParameters.pLength = r.height;
    contourParameters.pDiameter = area/(cLen/2);
    contourParameters.pWidth = (r.width-(contourParameters.pDiameter*2))/2;
//    contourParameters.pDensity = area; //contourSat;
    parametersData.add(contourParameters);
  }
  if (parametersData.size()>0) {
    parametersAnalysis();
  }
}

void displayContoursBoundingBoxes() {

  for (int i=0; i<contours.size(); i++) {

    Contour contour = contours.get(i);
    Rectangle r = contour.getBoundingBox();

    if (//(contour.area() > 0.9 * src.width * src.height) ||
      (r.width < minWidth || r.height < blobSizeThreshold))
      continue;

    stroke(255, 0, 0);
    fill(255, 0, 0, 100);
    strokeWeight(1);
    rect(r.x, r.y, r.width, r.height);
  }
}

double getSaturation(Rectangle tempRect) {
  double saturationValue = 0;
  curImage.loadPixels();
  for (int x = tempRect.x; x < tempRect.x+tempRect.width; x++) {
    for (int y = tempRect.y; y< tempRect.y+tempRect.height; y++) {
//      if (x+y*curImage.width < curImage.pixels.length) {
        saturationValue += saturation(curImage.pixels[x+y*curImage.width]);
        //      saturationValue += red(src.pixels[x+y*]);
    //  }
    }
  }
  saturationValue /= tempRect.width*tempRect.height;
  return saturationValue;
}

////////////////////
// Blob Detection
////////////////////

void detectBlobs() {

  // Contours detected in this frame
  // Passing 'true' sorts them by descending area.
  contours = opencv.findContours(true, true);

  newBlobContours = getBlobsFromContours(contours);

  //println(contours.length);

  // Check if the detected blobs already exist are new or some has disappeared. 

  // SCENARIO 1 
  // blobList is empty
  if (blobList.isEmpty()) {
    // Just make a Blob object for every face Rectangle
    for (int i = 0; i < newBlobContours.size(); i++) {
      //      println("+++ New blob detected with ID: " + blobCount);
      blobList.add(new Blob(this, blobCount, newBlobContours.get(i)));
      blobCount++;
    }

    // SCENARIO 2 
    // We have fewer Blob objects than face Rectangles found from OpenCV in this frame
  } else if (blobList.size() <= newBlobContours.size()) {
    boolean[] used = new boolean[newBlobContours.size()];
    // Match existing Blob objects with a Rectangle
    for (Blob b : blobList) {
      // Find the new blob newBlobContours.get(index) that is closest to blob b
      // set used[index] to true so that it can't be used twice
      float record = 50000;
      int index = -1;
      for (int i = 0; i < newBlobContours.size(); i++) {
        float d = dist(newBlobContours.get(i).getBoundingBox().x, newBlobContours.get(i).getBoundingBox().y, b.getBoundingBox().x, b.getBoundingBox().y);
        //float d = dist(blobs[i].x, blobs[i].y, b.r.x, b.r.y);
        if (d < record && !used[i]) {
          record = d;
          index = i;
        }
      }
      // Update Blob object location
      used[index] = true;
      b.update(newBlobContours.get(index));
    }
    // Add any unused blobs
    for (int i = 0; i < newBlobContours.size(); i++) {
      if (!used[i]) {
        //       println("+++ New blob detected with ID: " + blobCount);
        blobList.add(new Blob(this, blobCount, newBlobContours.get(i)));
        //blobList.add(new Blob(blobCount, blobs[i].x, blobs[i].y, blobs[i].width, blobs[i].height));
        blobCount++;
      }
    }

    // SCENARIO 3 
    // We have more Blob objects than blob Rectangles found from OpenCV in this frame
  } else {
    // All Blob objects start out as available
    for (Blob b : blobList) {
      b.available = true;
    } 
    // Match Rectangle with a Blob object
    for (int i = 0; i < newBlobContours.size(); i++) {
      // Find blob object closest to the newBlobContours.get(i) Contour
      // set available to false
      float record = 50000;
      int index = -1;
      for (int j = 0; j < blobList.size(); j++) {
        Blob b = blobList.get(j);
        float d = dist(newBlobContours.get(i).getBoundingBox().x, newBlobContours.get(i).getBoundingBox().y, b.getBoundingBox().x, b.getBoundingBox().y);
        //float d = dist(blobs[i].x, blobs[i].y, b.r.x, b.r.y);
        if (d < record && b.available) {
          record = d;
          index = j;
        }
      }
      // Update Blob object location
      Blob b = blobList.get(index);
      b.available = false;
      b.update(newBlobContours.get(i));
    } 
    // Start to kill any left over Blob objects
    for (Blob b : blobList) {
      if (b.available) {
        b.countDown();
        if (b.dead()) {
          b.delete = true;
        }
      }
    }
  }

  // Delete any blob that should be deleted
  for (int i = blobList.size()-1; i >= 0; i--) {
    Blob b = blobList.get(i);
    if (b.delete) {
      blobList.remove(i);
    }
  }
}

ArrayList<Contour> getBlobsFromContours(ArrayList<Contour> newContours) {

  ArrayList<Contour> newBlobs = new ArrayList<Contour>();

  // Which of these contours are blobs?
  for (int i=0; i<newContours.size(); i++) {

    Contour contour = newContours.get(i);
    Rectangle r = contour.getBoundingBox();

    if (//(contour.area() > 0.9 * src.width * src.height) ||
      (/*r.width < blobSizeThreshold ||*/ r.height < blobSizeThreshold))
      continue;

    newBlobs.add(contour);
  }

  return newBlobs;
}
void displayBlobs() {

  for (Blob b : blobList) {
    strokeWeight(1);
    b.display();
  }
}

void displayLines() {
  for (Line line : linesData) {
    // lines include angle in radians, measured in double precision
    // so we can select out vertical and horizontal lines
    // They also include "start" and "end" PVectors with the position
    if (line.angle >= radians(0) && line.angle < radians(1)) {
      stroke(255, 0, 255);
      line(line.start.x, line.start.y, line.end.x, line.end.y);
    }

    /*   if (line.angle > radians(89) && line.angle <= radians(91)) {
     stroke(255, 0, 0);
     line(line.start.x, line.start.y, line.end.x, line.end.y);
     }*/
  }
}

int analyzeLines(ArrayList<Line> lines) {
  int count = 0;
  for (Line line : lines) {
    println(line.angle);
    if (line.angle >= radians(0) && line.angle < radians(1)) {
      count++;
    }
  }
  return count;
}

int calculateLength (Contour c) {
  ArrayList<PVector> cPoints = c.getPoints();
  PVector prevP = cPoints.get(0);
  //  prevP.x = cPoints.get(0).x;
  //  prevP.y = cPoints.get(0).y;
  int totalCDist = 0;
  for (PVector p : cPoints) {
    totalCDist += dist(p.x, p.y, prevP.x, prevP.y);
    prevP.x = p.x;
    prevP.y = p.y;
  }
  return totalCDist;
}

void parametersAnalysis() {
  double avgLength = 0;
  double avgWidth = 0;
  double avgDiameter = 0;
  double avgDensity = 0;
  float mappedLength = 0;
  float mappedWidth = 0;
  float mappedDiameter = 0;
  float mappedDensity = 0;

  for (int i=0; i<parametersData.size(); i++) {
    Parameters par = parametersData.get(i);
    avgLength += par.pLength;
    avgWidth += par.pWidth;
    avgDiameter += par.pDiameter;
//    avgDensity += par.pDensity;
  }
  avgLength /= parametersData.size();
  avgWidth /= parametersData.size();
  avgDiameter /= parametersData.size();
  if (useROI) {
    avgDensity = (roiWidth*roiHeight)/densityPerFrame; 
  } else {
    avgDensity =  (curImage.width*curImage.height)/densityPerFrame; 
  }
  if ((calibrated && parametersPrintout) || (live && parametersPrintout)) {
    mappedLength = map((float)avgLength, minLength, maxLength, 0, 127);
    mappedLength = constrain(mappedLength, 0, 127);
    mappedWidth = map((float)avgWidth, minWidth, maxWidth, 0, 127);
    mappedWidth = constrain(mappedWidth, 0, 127);
    mappedDiameter = map((float)avgDiameter, minDiameter, maxDiameter, 0, 127);
    mappedDiameter = constrain(mappedDiameter, 0, 127);
    mappedDensity = map((float)avgDensity, minDensity, maxDensity, 0, 127);
    println("no of cap. " + parametersData.size() + " avg length " + avgLength + " avg width " + avgWidth + " avg diameter " + avgDiameter + " avg density " + avgDensity);
    println("snd length " + mappedLength + " snd width " + mappedWidth + " snd diameter " + mappedDiameter + " snd density " + mappedDensity);
    parametersPrintout = false;
    saveFrame("frame-######.png");
  }
}

float getDiameter(Contour contour, Rectangle r) {
  int tmpX = int(r.x);
  int tmpY = int(r.y+r.height-1);
  while (!contour.containsPoint(tmpX, tmpY) && (tmpY > r.y)) {
    tmpY--;
  }  
  return (tmpY-r.y);
}

class Parameters {
  double pLength;
  double pWidth;
  double pDiameter;
  double pDensity;

  Parameters() {
    pLength = 0;
    pWidth = 0;
    pDiameter = 0;
    pDensity = 0;
  }
}
