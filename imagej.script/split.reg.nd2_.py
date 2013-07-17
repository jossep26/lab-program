from ij import IJ, ImagePlus, ImageStack
from ij.process import ImageProcessor
from ij.process import FloatProcessor  
from ij.io import OpenDialog
from ij.plugin import ChannelSplitter
from ij.gui import ImageWindow
from ij.io import FileSaver
import os

from loci.plugins import BF

import TurboReg_


def regBf(fn=None, imp=None, refId=None):
    """ 
        Register a time series stack to a specified reference slice, 
            from a file (imported by BioFormat) or a stack ImagePlus.
        Returns a registered ImagePlus.
        The stack must have only 1 z layer.
        refId is in the format of [int channel, int slice, int frame]
            If no refId is supplied, will use the first slice [1,1,1]

        Note: since TurboReg is used for registeration, there will be 
            temporary opened image windows.

    """

    ## Prepare the right ImagePlus
    if imp is None:
        if fn is None:
            od = OpenDialog("Choose a file", None)
            filename = od.getFileName()

            if filename is None:
                print "User canceled the dialog!"
                return
            else:
                directory = od.getDirectory()
                filepath = directory + filename
                print "Selected file path:", filepath
        else:
            if os.path.exists(fn) and os.path.isfile(fn):
                filepath = fn
            else:
                print "File does not exist!"
                return

        imps = BF.openImagePlus(filepath)
        imp = imps[0]
        if imp is None:
            print "Cannot load file!"
            return

    else:
        if fn is not None:
            print "File or ImagePlus? Cannot load both."
            return

    width = imp.getWidth()
    height = imp.getHeight()
    # C
    nChannels = imp.getNChannels()
    # Z
    nSlices = imp.getNSlices()
    # T
    nFrames = imp.getNFrames()
    # pixel size
    calibration = imp.getCalibration()

    # Only supoort one z layer
    if nSlices != 1:
        print "Only support 1 slice at Z dimension."
        return

    # set registration reference slice
    if refId is None:
        refC = 1
        refZ = 1
        refT = 1
    else:
        refC = refId[0]
        refZ = refId[1]
        refT = refId[2]
        if (refC not in range(1, nChannels+1) or
            refZ not in range(1, nSlices+1) or
            refT not in range(1, nFrames+1) ):
            print "Invalid reference image!"
            return

    stack = imp.getImageStack()
    registeredStack = ImageStack(width, height, nChannels*nFrames*nSlices)

    # setup windows, these are needed by TurboReg
    tmpip = FloatProcessor(width, height)
    refWin = ImageWindow(ImagePlus("ref", tmpip))
    bounds = refWin.getBounds()
    # refWin.setVisible(False)
    toRegWin = ImageWindow(ImagePlus("toReg", tmpip))
    toRegWin.setLocation(bounds.width + bounds.x, bounds.y)
    # toRegWin.setVisible(False)
    toTransformWin = ImageWindow(ImagePlus("toTransform", tmpip))
    toTransformWin.setLocation(2 * bounds.width + bounds.x, bounds.y)
    # toTransformWin.setVisible(False)

    # get reference image
    refImp = ImagePlus("ref", stack.getProcessor(imp.getStackIndex(refC, refZ, refT)))
    refWin.setImage(refImp)

    tr = TurboReg_()

    for t in xrange(1, nFrames+1):
        IJ.showProgress(t-1, nFrames)

        # print "t ", t
        # do TurboReg on reference channel
        toRegId = imp.getStackIndex(refC, refZ, t)
        toRegImp = ImagePlus("toReg", stack.getProcessor(toRegId))
        toRegWin.setImage(toRegImp)

        regArg =  "-align " +\
                  "-window " + toRegImp.getTitle() + " " +\
                  "0 0 " + str(width - 1) + " " + str(height - 1) + " " +\
                  "-window " + refImp.getTitle() + " " +\
                  "0 0 " + str(width - 1) + " " + str(height - 1) + " " +\
                  "-rigidBody " +\
                  str(width / 2) + " " + str(height / 2) + " " +\
                  str(width / 2) + " " + str(height / 2) + " " +\
                  "0 " + str(height / 2) + " " +\
                  "0 " + str(height / 2) + " " +\
                  str(width - 1) + " " + str(height / 2) + " " +\
                  str(width - 1) + " " + str(height / 2) + " " +\
                  "-hideOutput"
                
        tr = TurboReg_()
        tr.run(regArg)
        registeredImp = tr.getTransformedImage()
        sourcePoints = tr.getSourcePoints()
        targetPoints = tr.getTargetPoints()

        registeredStack.setProcessor(registeredImp.getProcessor(), toRegId)

        # toRegImp.flush()

        # apply transformation on other channels
        for c in xrange(1, nChannels+1):
            # print "c ", c
            if c == refC:
                continue

            toTransformId = imp.getStackIndex(c, 1, t)
            toTransformImp = ImagePlus("toTransform", stack.getProcessor(toTransformId))
            toTransformWin.setImage(toTransformImp)

            transformArg = "-transform " +\
                           "-window " + toTransformImp.getTitle() + " " +\
                           str(width) + " " + str(height) + " " +\
                           "-rigidBody " +\
                           str(sourcePoints[0][0]) + " " +\
                           str(sourcePoints[0][1]) + " " +\
                           str(targetPoints[0][0]) + " " +\
                           str(targetPoints[0][1]) + " " +\
                           str(sourcePoints[1][0]) + " " +\
                           str(sourcePoints[1][1]) + " " +\
                           str(targetPoints[1][0]) + " " +\
                           str(targetPoints[1][1]) + " " +\
                           str(sourcePoints[2][0]) + " " +\
                           str(sourcePoints[2][1]) + " " +\
                           str(targetPoints[2][0]) + " " +\
                           str(targetPoints[2][1]) + " " +\
                           "-hideOutput"

            tr = TurboReg_()
            tr.run(transformArg)
            registeredStack.setProcessor(tr.getTransformedImage().getProcessor(), toTransformId)

            # toTransformImp.flush()
            sourcePoints = None
            targetPoints = None

        IJ.showProgress(t, nFrames)
        IJ.showStatus("Frames registered: " + str(t) + "/" + str(nFrames))

    refWin.close()
    toRegWin.close()
    toTransformWin.close()

    imp2 = ImagePlus("reg_"+imp.getTitle(), registeredStack)
    imp2.setCalibration(imp.getCalibration().copy())
    imp2.setDimensions(nChannels, nSlices, nFrames)
    # print "type ", imp.getType()
    # print "type ", imp2.getType()
    # print nChannels, " ", nSlices, " ", nFrames
    # print registeredStack.getSize()

    for key in imp.getProperties().stringPropertyNames():
        imp2.setProperty(key, imp.getProperty(key))
    # comp = CompositeImage(imp2, CompositeImage.COLOR)  
    # comp.show()
    # imp2 = imp.clone()
    # imp2.setStack(registeredStack)
    # imp2.setTitle("reg"+imp.getTitle())
    # imp2.show()
    # imp.show()

    return imp2


# batch reg nd2 in dir

srcDir = DirectoryChooser("Chose Source Dir").getDirectory()
if srcDir is None:
    print "Canceled"
    exit(1)

outDir = DirectoryChooser("Chose >Output< Dir").getDirectory()
if outDir is None:
    print "Output to same dir as source."
    ourtDir = srcDir

for root, directories, filenames in os.walk(srcDir):
    for filename in filenames:
        # Skip non-ND2 files
        if not filename.endswith(".nd2"):
            continue
        inpath = os.path.join(root, filename)

        # outfn = "reg_" + os.path.splitext(filename)[0] + ".tif"
        # outpath = os.path.join(outDir, outfn)
        # if os.path.exists(outpath):
        #     print "Skipped, already exists: ", outfn
        #     continue

        print "Registering ", filename
        imp = regBf(fn=inpath, refId=[2,1,1])
        if imp is None:
            print "Skipped, wrong with registration: ", filename
            continue
        else:
            # fs = FileSaver(imp)
            # fs.saveAsTiffStack(outpath)
            # IJ.saveAsTiff(imp, outpath)
            # print "Registered and saved to ", outfn
            splittedimps = ChannelSplitter.split(imp)
            for i, simp in enumerate(splittedimps):
                outfn = "reg_" + os.path.splitext(filename)[0] + "_C_" + i + ".tif"
                outpath = os.path.join(outDir, outfn)
                if os.path.exists(outpath):
                    print "Skipped, already exists: ", outfn
                    continue
                IJ.saveAsTiff(simp, outpath)
                print "Registered and saved to ", outfn

print "done."
