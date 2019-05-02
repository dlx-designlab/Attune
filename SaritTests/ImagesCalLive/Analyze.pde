void displayContours() {

  parametersData = new ArrayList<Parameters>();

  for (int i=0; i<contours.size(); i++) {

    Contour contour = contours.get(i);
    //    double factor = contour.getPolygonApproximationFactor();
    //    println("factor = ", factor);
    //   contour.setPolygonApproximationFactor(0.9);
    //   contour = contour.getPolygonApproximation();

    noFill();
    stroke(0, 255, 0);
    strokeWeight(1);
    contour.draw();
    Contour convexHullCuntor = contour.getConvexHull();
    stroke(0, 0, 255);
    convexHullCuntor.draw();
    float contourArea = 0;
    contourArea = contour.area();
    Rectangle r = contour.getBoundingBox();
//    double contourSat = getSaturation(r);


    if (//(contour.area() > 0.9 * src.width * src.height) ||
      (/*r.width < blobSizeThreshold ||*/ r.height < blobSizeThreshold))
      continue;

    stroke(255, 0, 0);
    /*    beginShape();
     for (PVector point : contour.getConvexhull().getPoints()) {
     vertex(point.x, point.y);
     }
     endShape();*/

    /*    stroke(255, 0, 0);
     fill(255, 0, 0, 150);
     strokeWeight(2);*/
    //    rect(r.x, r.y, r.width, r.height);
    Parameters contourParameters = new Parameters();
    contourParameters.pLength = r.height;
    contourParameters.pWidth = r.width;
 //   contourParameters.pDensity = (float)contourSat; // check that is not chopped
    parametersData.add(contourParameters);

    /*    int RL = calculateLength(contour);
     if (calibrated && parametersPrintout) {
     println("contour " + i + " vertexs " + contour.numPoints() + " area " + contourArea + " saturation " + contourSat + " RL " + RL);
     }*/
  }
  parametersAnalysis();
}

void displayContoursBoundingBoxes() {

  for (int i=0; i<contours.size(); i++) {

    Contour contour = contours.get(i);
    Rectangle r = contour.getBoundingBox();

    if (//(contour.area() > 0.9 * src.width * src.height) ||
      (/*r.width < blobSizeThreshold ||*/ r.height < blobSizeThreshold))
      continue;

    stroke(255, 0, 0);
    fill(255, 0, 0, 100);
    strokeWeight(1);
    rect(r.x, r.y, r.width, r.height);
  }
}

double getSaturation(Rectangle tempRect) {
  double saturationValue = 0;
  if (live) {
    microscope.loadPixels();
  } else {
    curImage.loadPixels();
  }
  for (int x = tempRect.x; x < tempRect.x+tempRect.width; x++) {
    for (int y = tempRect.y; y< tempRect.y+tempRect.height; y++) {
      if (x+y*height < curImage.pixels.length) {
        saturationValue += saturation(curImage.pixels[x+y*height]);
        //      saturationValue += red(src.pixels[x+y*]);
      }
    }
  }
  saturationValue /= tempRect.width*tempRect.height;
  return saturationValue;
  //  myImage.updatePixels();
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
  float avgLength = 0;
  float avgWidth = 0;
  float avgDiameter = 0;
  float avgDensity = 0;
  float mappedLength = 0;
  float mappedWidth = 0;
  float mappedDiameter = 0;
  float mappedDensity = 0;

  for (int i=0; i<parametersData.size(); i++) {
    Parameters par = parametersData.get(i);
    avgLength += par.pLength;
    avgWidth += par.pWidth;
    avgDiameter += par.pDiameter;
    avgDensity += par.pDensity;
  }
  avgLength /= parametersData.size();
  avgWidth /= parametersData.size();
  avgDiameter /= parametersData.size();
  //  avgDensity /= parametersData.size(); // for desity - not avg rather the amount of all contours saturation.
  if (calibrated && parametersPrintout) {
    mappedLength = map(avgLength, minLength, maxLength, 0, 127);
    mappedWidth = map(avgWidth, minLength, maxLength, 0, 127);
    mappedDiameter = map(avgDiameter, minLength, maxLength, 0, 127);
    mappedDensity = map(avgDensity, minLength, maxLength, 0, 127);
    println("length " + mappedLength + " width " + mappedWidth + " diameter " + mappedDiameter + " density " + mappedDensity);
    parametersPrintout = false;
  }
}

class Parameters {
  float pLength;
  float pWidth;
  float pDiameter;
  float pDensity;

  Parameters() {
    pLength = 0;
    pWidth = 0;
    pDiameter = 0;
    pDensity = 0;
  }
}
