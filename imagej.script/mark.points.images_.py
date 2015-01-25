from ij import IJ, ImagePlus, ImageStack
from ij.gui import Overlay, Roi, PointRoi, Line, TextRoi
from ij.io import DirectoryChooser
from java.awt.event import KeyEvent, KeyAdapter, MouseAdapter
from java.lang import String
from java.awt import Color
import os
import random
import math
import csv

def drawEnd(imp, keyEvent):
    if keyEvent.getKeyCode() == KeyEvent.VK_S:
        print "save!"
        keyEvent.consume()
        print keyEvent.isConsumed()
    if keyEvent.getKeyCode() == KeyEvent.VK_SPACE:
        print "space!"
        
    if keyEvent.getKeyCode() == KeyEvent.VK_PERIOD:
        print "next!"
        savePoints(imp)
        imp.close()
        prepareNewImage(imgIt)

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
        lineRoi.setStrokeWidth(1)
        lineRoi.setStrokeColor(Color(255,255,0))
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

def prepareNewImage(imgIt, direction=None):
    if direction == 'prev':
        imgPath = imgIt.prev()
    else:
        imgPath = imgIt.next()
    imp = IJ.openImage(imgPath)
    imp.show()

    lEnd = ListenToDrawEnd()
    lAdd = ListenToPointAdd()

    win = imp.getWindow()
    if win:
        canvas = win.getCanvas()
        # override key listeners
        kls = canvas.getKeyListeners()
        print len(kls)
        map(canvas.removeKeyListener, kls)
        canvas.addKeyListener(lEnd)
        map(canvas.addKeyListener, kls)
        canvas.addMouseListener(lAdd)
    print "ding!"

class twoWayCircularIterator(object):
    def __init__(self, l):
        # l should be a list
        self.l = l
        self.n = len(l)
        self.i = 0
    def next(self):
        cur = self.l[self.i]
        self.i += 1
        if self.i >= self.n:
            self.i = 0
        return cur
    def prev(self):
        cur = self.l[self.i]
        self.i -= 1
        if self.i < 0:
            self.i = self.n - 1
        return cur


#######################
imgPath = "d:\\tmp\\pointon\\2012-09-18 221x5905_Image011.tif"
imgDir = DirectoryChooser("Chose Directory of Images").getDirectory()
imgPaths = []
if imgDir:
    for root, directories, filenames in os.walk(imgDir):
        for filename in filenames:
            # Skip non-TIF files
            if not filename.endswith(".tif"):
                continue
            imgPaths.append(os.path.join(root, filename))
imgIt = twoWayCircularIterator(imgPaths)

header = [['x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'pixel_width', 'unit', 'image_name']]
outfn = 'points.csv'

outfile = open(outfn,'wb')
writer = csv.writer(outfile)
writer.writerows(header)
outfile.close()

IJ.setTool("multipoint")
PointRoi.setDefaultSize(3)

prepareNewImage(imgIt)
