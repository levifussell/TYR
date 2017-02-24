int Y_AXIS = 1;
int X_AXIS = 2;
color b1, b2, c1, c2;

void setup()
{
    /*colorT = [56, 175, 199];*/
    colorT = [47, 152, 137];
    size(window.innerWidth / 2.05, window.innerHeight * 0.8);
    stroke(200, 200);
    strokeWeight(0.3);
    /*noLoop();*/
    smooth();
    /*noStroke();*/
    PFont fontA = loadFont("courier");
    textFont(fontA, 14);
    max_distance = dist(0, 0, width, height);

    b1 = color(47, 152, 137);
    b2 = color(56, 175, 199);
    c1 = color(204, 102, 0);
    c2 = color(0, 102, 153);

    elipseSize = 5;
    numElipses = 200;
    randElipses = [];
    randElipseSize = [];
    randElipseFill = [];
    randElipseDir = [];
    /*randCount = [];*/
    randCount = 0;
    variance = 100;

    /*pg = createGraphics(800, 800, P3D);*/
    /*makebackground();*/

    randElipses[0] = [Math.random() * width / 3, Math.random() * height / 3];
    randElipses[1] = [Math.random() * width, Math.random() * height * 2 / 3];
    randElipses[2] = [Math.random() * width * 2 / 3, Math.random() * height * 2 / 3];
    randElipseSize[0] = Math.random() * 10 - 5;
    randElipseFill[0] = Math.random() * 255 + 140;
    randElipseSize[1] = Math.random() * 10 - 5;
    randElipseFill[1] = Math.random() * 255 + 140;
    randElipseSize[2] = Math.random() * 10 - 5;
    randElipseFill[2] = Math.random() * 255 + 140;
    randElipseDir[0] = [1, -1];
    randElipseDir[1] = [-1, 1];
    randElipseDir[2] = [1, 1];
    for(var i = 3; i < numElipses; ++i)
    {
        /*if(i == 0)*/
            /*randElipses[i] = [Math.random() * width, Math.random() * height];*/
        /*else*/
        randElipses[i] = [Math.random() * width, Math.random() * height];

        randElipseSize[i] = Math.random() * 10 - 5;
        randElipseFill[i] = Math.random() * 255;
        randElipseDir[i] = [Math.round(Math.random() * 2 - 0.1), Math.round(Math.random() * 2 - 1)];
    }

}

void draw()
{
    /*background(colorT[0], colorT[1], colorT[2]);*/
    /*background(pg);*/
    setGradient(0, 0, width, height, b1, b2, X_AXIS);
    /*setGradient(width/2, 0, width/2, height, b2, b1, X_AXIS);*/

    /*setGradient(50, 90, 540, 80, c1, c2, Y_AXIS);*/
    /*setGradient(50, 190, 540, 80, c2, c1, X_AXIS);*/

    //background gradient
    /*for(int i = 0; i < 3; ++i)*/
    /*{*/
        /*for(int j = 0; j < 3; ++j)*/
        /*{*/
            /*fill(colorT[0] / 2, colorT[1], colorT[2], 2 * i);*/
            /*strokeWeight(0);*/
            /*stroke(200, 0);*/
            /*ellipse(100 + i * 100, 100 + j * 100, 600, 600);*/
        /*}*/
    /*}*/

    ambientLight(51, 102, 126);

    stroke(200, 200);
    strokeWeight(0.8);

    /*text("Hello", 20, 20);*/
    /*println("Hello ErrorLog!");*/
    randCount += 0.0004;

    for(int i = 0; i < numElipses - 1; i++)
    {
        fill(200, randElipseFill[i]);
        /*float size = dist(mouseX, mouseY, i, j);*/
        /*size = size / max_distance * 66;*/
        randElipseSize[i] = Math.sin(randCount * i) * 5;
        offsetPosX = (Math.sin(randCount * i) * 2 - 1) * randElipseDir[i][0];
        offsetPosY = (Math.sin(randCount * i) * 2 - 1) * randElipseDir[i][1];
        randElipses[i][0] = (randElipses[i][0] + offsetPosX) % width;
        randElipses[i][1] = (randElipses[i][1] + offsetPosY) % height;
        if(randElipses[i][0] < 0)
            randElipses[i][0] = width - 1;
        if(randElipses[i][1] < 0)
            randElipses[i][1] = height - 1;
        ellipse(randElipses[i][0] + offsetPosX, randElipses[i][1] + offsetPosY, randElipseSize[i], randElipseSize[i]);
        /*line(randElipses[i][0], randElipses[i][1], randElipses[i + 1][0], randElipses[i + 1][1]);*/

        if(i < 3)
        {
            offsetV = Math.sin(randCount * randCount) * 100 - 2.5;
            line(randElipses[i][0] + offsetV, randElipses[i][1] + offsetV, randElipses[(i + 1) % 3][0] + offsetPosX, randElipses[(i + 1) % 3][1] + offsetPosY);
        }
    }

}

void setGradient(int x, int y, float w, float h, color c1, color c2, int axis ) {

  noFill();

    if (axis == Y_AXIS) {  // Top to bottom gradient
        for (int i = y; i <= y+h; i++) {
      float inter = map(i, y, y+h, 0, 1);
            color c = lerpColor(c1, c2, inter);
                  stroke(c);
                        line(x, i, x+w, i);

        }
          }
            else if (axis == X_AXIS) {  // Left to right gradient
                for (int i = x; i <= x+w; i++) {
      float inter = map(i, x, x+w, 0, 1);
            color c = lerpColor(c1, c2, inter);
                  stroke(c);
                        line(i, y, i, y+h);

                }
                  }

}
