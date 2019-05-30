void displayContours() {

  parametersData = new ArrayList<Parameters>();
  densityPerFrame = 0;
  for (int i=0; i<contours.size(); i++) {

    Contour contour = contours.get(i);

    noFill();
    stroke(0, 255, 0);
    strokeWeight(1);
    contour.draw();
    Rectangle r = contour.getBoundingBox();

    stroke(255, 0, 0);
    fill(255, 0, 0, 100);
    strokeWeight(1);
    float contourArea = 0;
    contourArea = contour.area();
    densityPerFrame += contourArea;

    if (//(contour.area() > 0.9 * src.width * src.height) ||
      (/*r.width < minWidth && */r.height < blobSizeThreshold))
      continue;

    Point[] cPoints = new Point[contour.numPoints()];
    ArrayList <PVector> cPointsList;
    cPointsList = contour.getPoints();
    for (int j=0; j<contour.numPoints(); j++) {
      cPoints[j] = new Point();
      cPoints[j].x = cPointsList.get(j).x;
      cPoints[j].y = cPointsList.get(j).y;
    }
    MatOfPoint2f mat = new MatOfPoint2f();
    mat.fromArray(cPoints);
    double cLen = Imgproc.arcLength(mat, true);
    double area = Imgproc.contourArea(mat);
    RotatedRect minRect = new RotatedRect();
    minRect = Imgproc.minAreaRect(mat);
    Point[] rectPoints = new Point[4];
    minRect.points(rectPoints);
    beginShape();
    vertex((float)rectPoints[0].x, (float)rectPoints[0].y);
    vertex((float)rectPoints[1].x, (float)rectPoints[1].y);
    vertex((float)rectPoints[2].x, (float)rectPoints[2].y);
    vertex((float)rectPoints[3].x, (float)rectPoints[3].y);
    endShape(CLOSE);
    double brHeight = dist((float)rectPoints[1].x, (float)rectPoints[1].y, (float)rectPoints[2].x, (float)rectPoints[2].y); 
    double brWidth = dist((float)rectPoints[2].x, (float)rectPoints[2].y, (float)rectPoints[3].x, (float)rectPoints[3].y); 
    if (brWidth > brHeight) {
      double temp = brHeight;
      brHeight = brWidth;
      brWidth = temp;
    }

    Parameters contourParameters = new Parameters();
    contourParameters.pLength = brHeight;//r.height;
    contourParameters.pDiameter = area/(cLen/2);
    contourParameters.pWidth = (brWidth-(contourParameters.pDiameter*2))/2;
    //    contourParameters.pDensity = area; //contourSat;
    parametersData.add(contourParameters);
  }
  if (parametersData.size()>0) {
    parametersAnalysis();
  }
}

void parametersAnalysis() {
  Parameters avgParams = new Parameters();

  for (int i=0; i<parametersData.size(); i++) {
    Parameters par = parametersData.get(i);
    avgParams.pLength += par.pLength;
    avgParams.pWidth += par.pWidth;
    avgParams.pDiameter += par.pDiameter;
    //    avgDensity += par.pDensity;
  }
  avgParams.pLength /= parametersData.size();
  avgParams.pWidth /= parametersData.size();
  avgParams.pDiameter /= parametersData.size();
  if (useROI) {
    avgParams.pDensity = (roiWidth*roiHeight)/densityPerFrame;
  } else {
    avgParams.pDensity =  (curImage.width*curImage.height)/densityPerFrame;
  }
  if (parametersToMusic) {
    saveAndSendData(avgParams);
    parametersToMusic = false;
  }
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
