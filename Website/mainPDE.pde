void setup()
{
    size(300, 500);
    background(125);
    fill(200);
    stroke(200)
    /*noLoop();*/
    smooth();
    /*noStroke();*/
    PFont fontA = loadFont("courier");
    textFont(fontA, 14);
    max_distance = dist(0, 0, width, height);

    elipseSize = 5;
    numElipses = 20;
    randElipses = [];
    randElipseSize = [];
    variance = 100;
    for(var i = 0; i < numElipses; ++i)
    {
        if(i == 0)
            randElipses[i] = [Math.random() * width, Math.random() * height];
        else
            randElipses[i] = [randElipses[i - 1][0] + Math.random() * variance - variance / 2, randElipses[i - 1][1] + Math.random() * variance - variance / 2];

        randElipseSize[i] = Math.random() * 10 - 5;
    }

}

void draw()
{
    background(51);
    /*text("Hello", 20, 20);*/
    /*println("Hello ErrorLog!");*/

    for(int i = 0; i < numElipses - 1; i++)
    {
        
        /*float size = dist(mouseX, mouseY, i, j);*/
        size = size / max_distance * 66;
        ellipse(randElipses[i][0], randElipses[i][1], randElipseSize[i], randElipseSize[i]);
        line(randElipses[i][0], randElipses[i][1], randElipses[i + 1][0], randElipses[i + 1][1]);
    }
}
