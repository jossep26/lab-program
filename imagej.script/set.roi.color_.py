from ij import IJ, ImagePlus, ImageStack
from ij.plugin.frame import RoiManager
from java.awt import Color
import re

# requires an opened RoiManager
roim = RoiManager.getInstance()
rois = roim.getRoisAsArray()

for roi in rois:
    if re.match(r"^hrp", roi.getName()):
        roi.setStrokeColor(Color.yellow)
    else:
        roi.setStrokeColor(Color.cyan)
