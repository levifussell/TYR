var VIEW_SIZE;

window.onload = function()
{
    InitialiseDevice();

    var canvas = document.getElementById('myCanvas');
    paper.setup(canvas);

    var numOfPoints = 10;
    var start = new paper.Point(0, VIEW_SIZE.y / 2);
    var end = new paper.Point(VIEW_SIZE.x, VIEW_SIZE.y / 2);
    var rateX = VIEW_SIZE.x / numOfPoints;

    var path = new paper.Path();
    path.semgents = [];
    path.add(start);

    for(var i = 1; i < numOfPoints; ++i)
    {
        var p = new paper.Point(rateX * i, VIEW_SIZE.y / 2 + 10 * Math.random() - 5);
        path.add(p);
    }
    path.add(end);

    path.strokeColor = 'black';

    var count = 0;
    path.onFrame = function(event)
    {
        count += 0.01;
        console.log("hello");
        for(var i = 1; i < numOfPoints; ++i)
        {
            console.log(path.segments[i].point.y);
            path.segments[i].point.y += Math.sin(count * i) * 5;
        }
    }


    paper.view.draw();
}

function InitialiseDevice()
{
    //VIEW_SIZE = view.size;
    VIEW_SIZE = new paper.Point(700, 400);
}

function OnWindowResize()
{
    IntialiseDevice();
}

window.addEventListener('resize', OnWindowResize);
