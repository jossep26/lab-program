from ij import IJ, ImagePlus, ImageStack
from ij.gui import Overlay, Roi, PointRoi, Line, TextRoi
from ij.io import DirectoryChooser, OpenDialog
from java.awt.event import KeyEvent, KeyAdapter, MouseAdapter
from java.lang import String
from java.awt import Color
import os.path
import random
import math
import csv

def drawEnd(imp, pointsTable, keyEvent):
    if keyEvent.getKeyCode() == KeyEvent.VK_SPACE:
        print "space!"
    if keyEvent.getKeyCode() == KeyEvent.VK_BACK_QUOTE:
        print "save table!"
        savePointsToTable(imp, pointsTable)
        saveTableToFile(pointsTable, OUTFN)
    if keyEvent.getKeyCode() == KeyEvent.VK_PERIOD:
        print "next!"
        savePointsToTable(imp, pointsTable)
        imp.close()
        prepareNewImage(imgIt, pointsTable)
    if keyEvent.getKeyCode() == KeyEvent.VK_COMMA:
        print "prev!"
        savePointsToTable(imp, pointsTable)
        imp.close()
        prepareNewImage(imgIt, pointsTable, 'prev')

class ListenToDrawEnd(KeyAdapter):
    def keyPressed(this, event):
        imp = event.getSource().getImage()
        # reads global pointsTable
        drawEnd(imp, pointsTable, event)

class ListenToPointAdd(MouseAdapter):
    def mouseReleased(self, event):
        imp = event.getSource().getImage()
        drawLines(imp)
        
def drawLines(imp, points=None):
    if points and (len(points)%2 == 0):
        # points is numeric list of even length
        pRoi = PointRoi(points[0::2], points[1::2], len(points)/2)
        pRoi.setShowLabels(True)
        pRoi.setSize(3)
        imp.setRoi(pRoi)
    roi = imp.getRoi()
    pp = roi.getFloatPolygon()
    print "Added", pp.npoints
    if pp.npoints <= 1:
        # don't draw if only one point
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
        # prepare text label
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
        dTextRoi = TextRoi(xt, yt, dText)
        ol.add(dTextRoi)

        lineRoi = Line(x0, y0, xi, yi)
        lineRoi.setStrokeWidth(1)
        lineRoi.setStrokeColor(Color(255,255,0))
        ol.add(lineRoi)
    imp.setOverlay(ol)
    imp.updateAndDraw()

def savePoints(imp):
    # append points to existing file
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

    outfile = open(OUTFN,'ab')
    writer = csv.writer(outfile)
    writer.writerows([out])
    outfile.close()

def savePointsToTable(imp, pointsTable):
    # pointsTable should be a dict
    cal = imp.getCalibration()
    roi = imp.getRoi()
    pp = roi.getFloatPolygon()
    points = []
    for i in xrange(pp.npoints):
        if i < NPOINTS:
            # only record 3 points
            points.append(pp.xpoints[i])
            points.append(pp.ypoints[i])
    points.append(cal.pixelWidth)
    points.append(cal.getUnit())

    pointsTable[imp.getTitle()] = points

def saveTableToFile(pointsTable, fn):
    outfile = open(fn,'wb')
    writer = csv.writer(outfile)
    writer.writerows(HEADER)
    print "header"
    print pointsTable
    for title, points in pointsTable.iteritems():
        entry = [title]
        entry.extend(points)
        print entry
        writer.writerow(entry)
    outfile.close()
    print 'saved!'

def prepareNewImage(imgIt, pointsTable, direction=None):
    if direction == 'prev':
        if not imgIt.hasPrev():
            print 'end! back to first'
        imgPath = imgIt.prev()
    else:
        if not imgIt.hasNext():
            print 'end! to end'
        imgPath = imgIt.next()

    imp = IJ.openImage(imgPath)
    imp.show()

    if os.path.basename(imgPath) in pointsTable:
        pts = pointsTable[os.path.basename(imgPath)]
        if len(pts) >= 6:
            # at least 3 points (i.e. 6 coords)
            imgPoints = map(float, pts[:6])
            drawLines(imp, imgPoints)

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
    imp.show()
    print "ding!"

class twoWayCircularIterator(object):
    def __init__(self, l):
        # l should be a list
        self.l = l
        self.n = len(l)
        self.i = -1
    def hasNext(self):
        return self.i < self.n - 1
    def next(self):
        self.i += 1
        if self.i >= self.n:
            self.i = 0
        return self.l[self.i]
    def hasPrev(self):
        return self.i > 0
    def prev(self):
        self.i -= 1
        if self.i < 0:
            self.i = self.n - 1
        return self.l[self.i]

def readPoints(fn):
    # reads and create a table for storing points
    #       key: image title
    #       value: points and pixel width
    # note: no validation on file input, 
    #       ok only if no direct file modification
    table = dict()
    if not os.path.isfile(fn):
        return table
    f = open(fn,'rb')
    reader = csv.reader(f)
    try:
        reader.next()
    except StopIteration:
        return table
    for row in reader:
        table[row[0]] = row[1:]
    f.close()
    return table

#######################
HEADER = [['image_name', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'pixel_width', 'unit']]
NPOINTS = 3

fileChooser = OpenDialog("Point Marker: Choose working directory and file")
OUTFN = fileChooser.getPath()

imgDir = fileChooser.getDirectory()
imgPaths = []
if imgDir:
    for root, directories, filenames in os.walk(imgDir):
        for filename in filenames:
            if not filename.endswith(".tif"):
                continue
            imgPaths.append(os.path.join(root, filename))
imgIt = twoWayCircularIterator(imgPaths)

pointsTable = readPoints(OUTFN)

IJ.setTool("multipoint")
PointRoi.setDefaultSize(3)

prepareNewImage(imgIt, pointsTable)
