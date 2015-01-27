from ij import IJ, ImagePlus, ImageStack
from ij.gui import Overlay, Roi, PointRoi, Line, TextRoi
from ij.gui import ImageWindow, ImageCanvas, MessageDialog
from ij.io import DirectoryChooser, OpenDialog
from java.awt.event import KeyEvent, KeyAdapter, MouseAdapter
from java.lang import String
from java.awt import Color, Dimension, Component
from javax.swing import JFrame, JPanel, JLabel, JProgressBar, JDialog, JTextField
from javax.swing import BoxLayout, Box, BorderFactory

from datetime import datetime
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
        pmWin.update()

def drawEnd(imp, imgData, keyEvent):
    if keyEvent.getKeyCode() == KeyEvent.VK_BACK_QUOTE:
        # print "save table!"
        stashPoints(imp, imgData)
        saveToFile(imgData)
    if keyEvent.getKeyCode() == KeyEvent.VK_S:
        # print "save table!"
        stashPoints(imp, imgData)
        saveToFile(imgData)
        keyEvent.consume()
    if keyEvent.getKeyCode() == KeyEvent.VK_PERIOD:
        # print "next!"
        stashPoints(imp, imgData)
        imp.close()
        prepareNewImage(imgData)
    if keyEvent.getKeyCode() == KeyEvent.VK_COMMA:
        # print "prev!"
        stashPoints(imp, imgData)
        imp.close()
        prepareNewImage(imgData, 'prev')
    if keyEvent.getKeyCode() == KeyEvent.VK_TAB:
        # print "tab! next unmarked"
        stashPoints(imp, imgData)
        imp.close()
        prepareNewImage(imgData, 'unmarked')

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
    # print "Added", pp.npoints
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

def angle(xs, ys):
    # helper function to calculate angle between the 3 points
    if len(xs) != 3 or len(xs) != len(ys):
        return 0
    # calculate vectors
    x1 = xs[1] - xs[0]
    y1 = ys[1] - ys[0]
    x2 = xs[2] - xs[0]
    y2 = ys[2] - ys[0]

    inner_product = x1 * x2 + y1 * y2
    len1 = math.hypot(x1, y1)
    len2 = math.hypot(x2, y2)
    return math.acos(inner_product / (len1 * len2))

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
    ag = angle(pp.xpoints, pp.ypoints)
    points.append(ag)
    points.append(ag * 180 / math.pi)

    imgData.table[imp.getTitle()] = points

def saveToFile(imgData):
    pointsTable = imgData.table
    outfile = open(imgData.fn,'wb')
    writer = csv.writer(outfile)
    headerRow = ['image_name', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', \
                 'pixel_width', 'unit', 'angle_radian', 'angle_degree']
    writer.writerow(headerRow)
    for title, points in pointsTable.iteritems():
        entry = [title]
        entry.extend(points)
        # print entry
        writer.writerow(entry)
    outfile.close()
    # print 'saved!'
    pmWin.flashSaveMessage()

def prepareNewImage(imgData, direction=None):
    if direction == 'prev':
        # if not imgData.hasPrev():
            # print 'end! back to first'
        imgPath = imgData.prev()
    elif direction == 'unmarked':
        imgPath = imgData.nextUnmarked()
    else:
        # if not imgData.hasNext():
            # print 'end! to end'
        imgPath = imgData.next()

    imp = IJ.openImage(imgPath)

    try:
        newUnit = pmWin.unitText.getText()
        newPixelSize = float(pmWin.pixelSizeText.getText())
    except ValueError:
        pass
    else:
        cal = imp.getCalibration()
        cal.setUnit(newUnit)
        cal.pixelWidth = newPixelSize
        cal.pixelHeight = cal.pixelWidth

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
    #       key: image title, 1st column
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
    def __init__(self, imgPaths, pointFilePath, pointTable = dict()):
        # iterator of image paths
        self.l = imgPaths
        self.n = len(self.l)
        self.i = -1

        # table for storing marked points
        self.table = pointTable

        # file path for points
        self.fn = pointFilePath
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
    def nextUnmarked(self):
        path = self.l[self.i]
        while(self.hasNext()):
            if os.path.basename(path) not in self.table:
                break
            path = self.next()
        return path

## status window
class PointMarkerWin(object):
    def __init__(self, imgData):
        n = imgData.size()
        win = JFrame("Point Marker Panel")
        win.setSize(Dimension(350, 510))
        pan = JPanel()
        pan.setLayout(BoxLayout(pan, BoxLayout.Y_AXIS))
        win.getContentPane().add(pan)

        progressPanel = JPanel()
        progressPanel.setLayout(BoxLayout(progressPanel, BoxLayout.Y_AXIS))
        positionBar = JProgressBar()
        positionBar.setMinimum(0)
        positionBar.setMaximum(n)
        positionBar.setStringPainted(True)
        progressPanel.add(Box.createGlue())
        progressPanel.add(positionBar)

        progressBar = JProgressBar()
        progressBar.setMinimum(0)
        progressBar.setMaximum(n)
        progressBar.setStringPainted(True)
        progressPanel.add(progressBar)
        progressPanel.setBorder(BorderFactory.createEmptyBorder(0,10,0,10))
        pan.add(progressPanel)

        calPanel = JPanel()
        calPanel.setLayout(BoxLayout(calPanel, BoxLayout.X_AXIS))
        pixelSizeText = JTextField(12)
        pixelSizeText.setHorizontalAlignment(JTextField.RIGHT)
        pixelSizeText.setMaximumSize(pixelSizeText.getPreferredSize())
        unitText = JTextField(10)
        unitText.setMaximumSize(unitText.getPreferredSize())
        calPanel.add(JLabel("Pixel Size:"))
        calPanel.add(pixelSizeText)
        calPanel.add(JLabel("Unit:"))
        calPanel.add(unitText)
        calPanel.setAlignmentX(Component.CENTER_ALIGNMENT)
        calPanel.setBorder(BorderFactory.createEmptyBorder(0,10,0,10))
        pan.add(calPanel)

        savePanel = JPanel()
        savePanel.setLayout(BoxLayout(savePanel, BoxLayout.Y_AXIS))
        saveMessageLabel = JLabel("<html><u>Save Often</u></html>")
        savePanel.add(saveMessageLabel)
        savePanel.setAlignmentX(Component.CENTER_ALIGNMENT)
        savePanel.setBorder(BorderFactory.createEmptyBorder(0,10,0,10))
        pan.add(savePanel)
        # pan.add(saveMessageLabel)

        helpPanel = JPanel()
        helpPanel.setLayout(BoxLayout(helpPanel, BoxLayout.Y_AXIS))
        helpLable = JLabel("<html><ul>\
                            <li>Focus on Image Window</li>\
                            <li>Select multi-point Tool</li>\
                            <li>Click to Draw Points</li>\
                            <li>Drag to Move Points</li>\
                            <li>\"Alt\" + Click to Erase Points\
                            </html>")
        helpLable.setBorder(BorderFactory.createTitledBorder("Usage"))
        keyTagOpen = "<span style=\"background-color: #FFFFFF\"><b><kbd>"
        keyTagClose = "</kbd></b></span>"
        keyLable = JLabel("<html><ul>\
                            <li>Next Image --- " + keyTagOpen + "&lt" + \
                                keyTagClose + "</li>\
                            <li>Previous Image --- " + keyTagOpen + ">" + \
                                keyTagClose + "</li>\
                            <li>Save --- " + keyTagOpen + "`" + keyTagClose + \
                                " (upper-left to TAB key)</li>\
                            <li>Next Unmarked Image --- " + keyTagOpen + \
                                "TAB" + keyTagClose + "</li></ul>\
                            </html>")
        keyLable.setBorder(BorderFactory.createTitledBorder("Keyboard Shortcuts"))
        helpPanel.add(helpLable)
        helpPanel.add(keyLable)
        helpPanel.setAlignmentX(Component.CENTER_ALIGNMENT)
        helpPanel.setBorder(BorderFactory.createEmptyBorder(0,10,0,10))
        pan.add(helpPanel)

        # pan.add(Box.createRigidArea(Dimension(0, 10)))
        infoPanel = JPanel()
        infoPanel.setLayout(BoxLayout(infoPanel, BoxLayout.Y_AXIS))
        infoLabel = JLabel()
        infoLabel.setBorder(BorderFactory.createTitledBorder("Project Info"))
        infoPanel.add(infoLabel)
        infoPanel.setAlignmentX(Component.CENTER_ALIGNMENT)
        infoPanel.setBorder(BorderFactory.createEmptyBorder(0,10,0,10))
        pan.add(infoPanel)

        win.setVisible(True)

        self.imgData = imgData
        self.win = win
        # self.progressPanel = progressPanel
        self.positionBar = positionBar
        self.progressBar = progressBar
        self.saveMessageLabel = saveMessageLabel
        self.infoLabel = infoLabel
        self.pixelSizeText = pixelSizeText
        self.unitText = unitText
        self.update()

    def updatePositionAndProgress(self):
        positionBar = self.positionBar
        progressBar = self.progressBar
        _imgData = self.imgData
        n = _imgData.size()
        pos = _imgData.position()
        pro = _imgData.progress()
        positionBar.setValue(pos)
        positionBar.setString("Position: " + str(pos) + " / " + str(n))
        progressBar.setValue(pro)
        progressBar.setString("Progress: " + str(pro) + " / " + str(n))

    def updateInfoLabel(self):
        _imgData = self.imgData
        imgPath = _imgData.l[_imgData.i]
        dirn = os.path.dirname(_imgData.fn)
        fn = os.path.basename(_imgData.fn)
        self.infoLabel.setText("<html><ul style=\"list-style-type: none\">" +\
                          "<li>Working Dir: <samp>" + dirn + "</samp></li>" +\
                          "<li>Points file: <samp>" + fn + "</samp></li>" + \
                          "<li>Current image:<br><samp>" + \
                              os.path.basename(imgPath) + "</samp></li></html>")
    def update(self):
        self.updateInfoLabel()
        self.updatePositionAndProgress()
    def flashSaveMessage(self):
        sl = self.saveMessageLabel
        sl.setText("<html><u>Save Often</u>: \
                    Saved " + str(datetime.now()) + "</html>")

#######################
def run():
    global pmWin
    global imgData
    helpText = "This is Point Marker, " + \
               "a program for marking points in images.\n\n" + \
               ">> Select a file for storing points infomation.\n" + \
               ">> TIF-Images within the same directory will be auto-loaded."
    MessageDialog(IJ.getInstance(),"Point Marker Guide", helpText)

    fileChooser = OpenDialog("Point Marker: Choose working directory and file")
    outfilePath = fileChooser.getPath()
    imgDir = fileChooser.getDirectory()
    if not imgDir:  return
    imgPaths = []
    if imgDir:
        for root, directories, filenames in os.walk(imgDir):
            for filename in filenames:
                if not filename.endswith(".tif"):
                    continue
                imgPaths.append(os.path.join(root, filename))

    pointsTable1 = readPoints(outfilePath)

    imgData = PointMarkerData(imgPaths, outfilePath, pointsTable1)

    IJ.setTool("multipoint")
    PointRoi.setDefaultSize(3)

    pmWin = PointMarkerWin(imgData)
    pmWin.win.setLocation(IJ.getInstance().getLocation())
    prepareNewImage(imgData)

##
run()
