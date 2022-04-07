
boolean midi = false; // change this to false for mouseX/mouseY/mouseScroll


int x;
int y;
int w;
int h;
PShape u;
int[] xList = {2, 3, 4};
int[] x2List = {8, 9, 10};
int[] hList = {0, 0, 1, 2, 3, 4, 8, 9, 10, 11, 12};
//int[] hList = {};

float mw;
void setup() {
  size(512, 512);
  u = loadShape("uuu.svg");
}

void draw() {
  translate(width/2, height/2);
  //shape(u,10,10);
  //for (int i = 0 ; i< u.get)
  background(255);
  u.disableStyle();
  PShape c = u.getChild(0);
  PShape d = u.getChild(1);
  int total = c.getVertexCount();
  for (int j = 0; j < total; j++) {
    PVector v = c.getVertex(j);
    //fill(255,0,255);
    text(j, v.x, v.y);
  }
  c.setStroke(true);
  strokeWeight(abs(w));
  stroke(225, 0, 0);
  noFill();
  c.beginShape();
  c.stroke(255, 0, 0);
  c.strokeCap(3);
  c.strokeWeight(w);
  c.noFill();
  c.endShape();
  //c.get
  for (int i = 0; i<xList.length; i++) {
    PVector a14 = d.getVertex(xList[i]);
    PVector b14 = d.getVertex(x2List[i]);
    b14.x=(-1*(x-60))*0.590551181;
    a14.x=(x-60)*0.590551181;
    c.setVertex(xList[i], a14);
    c.setVertex(x2List[i], b14);
    //println(a14);
  }
  for (int i = 1; i<hList.length; i++) {
    PVector a14 = d.getVertex(hList[i]);
    PVector c14 = c.getVertex(hList[i]);

    a14.y+=y;
    a14.x=c14.x;
    c.setVertex(hList[i], a14);
    //println(a14);
  }
  //c.strokeCap(2);

  shape(c, 10, 10);

  //println(x,y,w,h);
  if (!midi){
  x = mouseX/5;
  y = mouseY/5;
  w = (int)mw;
  
  }
}

void mouseWheel(MouseEvent event) {
  float e = event.getCount();
  mw += e;
  //println(e);
}
