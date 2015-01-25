from ij import IJ, ImagePlus, ImageStack
from java.awt.event import KeyEvent, KeyAdapter, MouseAdapter
from ij.gui import Overlay, Roi, Line, TextRoi
from java.lang import String
import os
import random
import math
import csv

imgPath = "d:\\tmp\\pointon\\2012-09-18 221x5905_Image011.tif"

def drawEnd(imp, keyEvent):
    if keyEvent.getKeyCode() == KeyEvent.VK_SPACE:
        print "space!"
        processPoints(imp)
    if keyEvent.getKeyCode() == KeyEvent.VK_PERIOD:
        print "next!"
        savePoints(imp)
        imp.close()
        prepareNewImage(imgPath)

class ListenToDrawEnd(KeyAdapter):
    def keyPressed(this, event):
        imp = event.getSource().getImage()
        drawEnd(imp, event)

class ListenToPointAdd(MouseAdapter):
    def mouseReleased(self, event):
        imp = event.getSource().getImage()
        drawLines(imp)
        
def drawLines(imp):
    roi = imp.getRoi()
    pp = roi.getFloatPolygon()
    print "Added", pp.npoints
    if pp.npoints <= 1:
        return
    xys = []
    for i in xrange(pp.npoints):
        xys.append([pp.xpoints[i], pp.ypoints[i]])
    ol = Overlay()
    x0 = xys[0][0]
    y0 = xys[0][1]
    cal = imp.getCalibration()
    for i in xrange(1, pp.npoints):
        xi = xys[i][0]
        yi = xys[i][1]
        d = math.sqrt((xi - x0)**2 + (yi - y0)**2) * cal.pixelWidth
        dText = String.format("%.2f ", d) + cal.getUnits()
        textOffset = 30
        xt = xi
        yt = yi
#        if xi > x0:
#            xt += textOffset
        if xi < x0:
            xt -= textOffset
#        if yi > y0:
#            yt += textOffset
        if yi < y0:
            yt -= textOffset
        lineRoi = Line(x0, y0, xi, yi)
        dTextRoi = TextRoi(xt, yt, dText)
        ol.add(lineRoi)
        ol.add(dTextRoi)
    imp.setOverlay(ol)
    imp.updateAndDraw()

def savePoints(imp):
    cal = imp.getCalibration()
    roi = imp.getRoi()
    pp = roi.getFloatPolygon()
    out = []
    out.append(imp.getTitle())
    for i in xrange(pp.npoints):
        out.append(pp.xpoints[i])
        out.append(pp.ypoints[i])
    out.append(cal.pixelWidth)
    out.append(cal.getUnit())

    outfile = open(outfn,'ab')
    writer = csv.writer(outfile)
    writer.writerows([out])
    outfile.close()


def prepareNewImage(imgPath):
    imp = IJ.openImage(imgPath)
    imp.show()

    lEnd = ListenToDrawEnd()
    lAdd = ListenToPointAdd()

    win = imp.getWindow()
    if win:
        canvas = win.getCanvas()
        canvas.addKeyListener(lEnd)
        canvas.addMouseListener(lAdd)
    print "ding!"

header = [['x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'pixel_width', 'unit', 'image_name']]
outfn = 'points.csv'

outfile = open(outfn,'wb')
writer = csv.writer(outfile)
writer.writerows(header)
outfile.close()

IJ.setTool("multipoint")

prepareNewImage(imgPath)