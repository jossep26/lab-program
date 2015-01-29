import os
import re
from ij import IJ, ImagePlus, ImageStack
from ij.io import DirectoryChooser
from ij.measure import Calibration
from ij.process import ImageConverter
from ij.gui import MessageDialog

def run():
    helpText = "This program will batch convert any tif image to 8-bit greyscale, " + \
               "and empty calibration infomation.\n\n" + \
               ">> Press OK to Select a directory of TIFF images."
    MessageDialog(IJ.getInstance(),"Empty Calibration Guide", helpText)

    srcDir = DirectoryChooser("Chose Source Dir").getDirectory()
    if srcDir is None:
        IJ.log("Choose Dir Canceled!")
        return

    for root, directories, filenames in os.walk(srcDir):
        for filename in filenames:
            if not filename.endswith(".tif"):
                continue
            imgPath = os.path.join(root, filename)
            outPath = os.path.join(root, "decal-" + filename)

            imp = IJ.openImage(imgPath)
            imp.setCalibration(Calibration())
            ic = ImageConverter(imp)
            ic.convertToGray8()
            IJ.saveAsTiff(imp, outPath)
            print "removed calibration and saved to ", os.path.basename(outPath)

run()