from ij import IJ, ImagePlus, ImageStack
from ij.process import FloatProcessor  
from array import zeros  
from ij.io import OpenDialog 
from ij.plugin.frame import RoiManager
import os

# this script requires that Roi Manager be closed !

odroi = OpenDialog("Choose a ROI file", None)
roifn = odroi.getFileName()

if roifn is None:
    print "User canceled the dialog!"
else:
    roidir = odroi.getDirectory()
    roipath = os.path.join(roidir, roifn)

odref = OpenDialog("Choose a reference image file", None)
reffn = odref.getFileName()

if reffn is None:
    print "User canceled the dialog!"
else:
    refdir = odref.getDirectory()
    refpath = os.path.join(refdir, reffn)

refImp = IJ.openImage(refpath)
width = refImp.width  
height = refImp.height  

roim = RoiManager()
roim.runCommand("open", roipath)

roiArray = roim.getRoisAsArray()
nRoi = len(roiArray)
roim.close()

bwStack = ImageStack(width, height, nRoi)
for i in xrange(1, nRoi+1):
    bwStack.setProcessor(FloatProcessor(width, height, zeros('f', width * height), None), i)

for i in xrange(1, nRoi+1):
    roi = roiArray[i-1]
    fp = bwStack.getProcessor(i)
    fp.setValue(1.0)
    fp.fill(roi)

roiImp = ImagePlus("roi", bwStack)

outfn = "roi_" + os.path.splitext(roifn)[0] + ".tif"
outpath = os.path.join(roidir, outfn)
if os.path.exists(outpath):
    print "Skipped, already exists: ", outfn
else:
    IJ.saveAsTiff(roiImp, outpath)
