from ij import IJ, ImagePlus, ImageStack
from ij.gui import Overlay, Roi, PointRoi, Line, TextRoi
from ij.gui import ImageWindow, ImageCanvas
from ij.io import DirectoryChooser, OpenDialog
from java.awt.event import KeyEvent, KeyAdapter, MouseAdapter
from java.lang import String
from java.awt import Color
from javax.swing import JFrame, JPanel, JLabel, JProgressBar
import os.path
import random
import math
import csv

class ListenToDrawEnd(KeyAdapter):
    # def __init__(self, imgData):
    #     self.imgData = imgData
    def keyPressed(this, event):
        source = event.getSource()
        if isinstance(source, ImageCanvas):
            imp = event.getSource().getImage()
        elif isinstance(source, ImageWindow):
            imp = event.getSource().getImagePlus()
        else:
            return
        # reads global imgData
        drawEnd(imp, imgData, event)

def drawEnd(imp, imgData, keyEvent):
    if keyEvent.getKeyCode() == KeyEvent.VK_SPACE:
        print "space!"
    if keyEvent.getKeyCode() == KeyEvent.VK_BACK_QUOTE:
        print "save table!"
        stashPoints(imp, imgData)
        saveToFile(imgData)
    if keyEvent.getKeyCode() == KeyEvent.VK_S:
        print "save table!"
        stashPoints(imp, imgData)
        saveToFile(imgData)
        keyEvent.consume()
    if keyEvent.getKeyCode() == KeyEvent.VK_PERIOD:
        print "next!"
        stashPoints(imp, imgData)
        imp.close()
        prepareNewImage(imgData)
    if keyEvent.getKeyCode() == KeyEvent.VK_COMMA:
        print "prev!"
        stashPoints(imp, imgData)
        imp.close()
        prepareNewImage(imgData, 'prev')

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

def stashPoints(imp, imgData):
    # store/update points in imgData
    # only 3 points
    MAXPOINTS = 3
    cal = imp.getCalibration()
    roi = imp.getRoi()
    if not roi:  return
    pp = roi.getFloatPolygon()
    if pp.npoints < MAXPOINTS:  return
    points = []
    for i in xrange(pp.npoints):
        if i < MAXPOINTS:
            points.append(pp.xpoints[i])
            points.append(pp.ypoints[i])
    points.append(cal.pixelWidth)
    points.append(cal.getUnit())

    imgData.table[imp.getTitle()] = points

def saveToFile(imgData):
    pointsTable = imgData.table
    outfile = open(imgData.fn,'wb')
    writer = csv.writer(outfile)
    headerRow = ['image_name', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'pixel_width', 'unit']
    writer.writerow(headerRow)
    for title, points in pointsTable.iteritems():
        entry = [title]
        entry.extend(points)
        print entry
        writer.writerow(entry)
    outfile.close()
    print 'saved!'

def prepareNewImage(imgData, direction=None):
    if direction == 'prev':
        if not imgData.hasPrev():
            print 'end! back to first'
        imgPath = imgData.prev()
    else:
        if not imgData.hasNext():
            print 'end! to end'
        imgPath = imgData.next()

    imp = IJ.openImage(imgPath)
    imp.show()
    pointsTable = imgData.table
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
        # override key listeners
        wkls = win.getKeyListeners()
        map(win.removeKeyListener, wkls)
        win.addKeyListener(lEnd)
        map(win.addKeyListener, wkls)

        canvas = win.getCanvas()
        ckls = canvas.getKeyListeners()
        map(canvas.removeKeyListener, ckls)
        canvas.addKeyListener(lEnd)
        map(canvas.addKeyListener, ckls)
        canvas.addMouseListener(lAdd)

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

# data holder, contains a two way iterator of image paths,
# and a table for marked points
class PointMarkerData(object):
    def __init__(self, imgPaths, pointTable = dict(), pointFile = "points.csv"):
        # iterator of image paths
        self.l = imgPaths
        self.n = len(self.l)
        self.i = -1

        # table for storing marked points
        self.table = pointTable

        # file path for points
        self.fn = pointFile
    def size(self):
        return self.n
    def position(self):
        return self.i + 1
    def progress(self):
        return len(self.table)

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


#######################

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

pointsTable1 = readPoints(OUTFN)

imgData = PointMarkerData(imgPaths, pointsTable1, OUTFN)

IJ.setTool("multipoint")
PointRoi.setDefaultSize(3)

prepareNewImage(imgData)
