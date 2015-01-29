import re
import os
from tracing import PathAndFillManager
from ij.measure import Calibration
from ij.io import DirectoryChooser
from ij.gui import MessageDialog
from ij import IJ

def toSvgPathDString(path):
    pathDString = "M" + str(path.getXUnscaledDouble(0)) + " " + \
                  str(path.getYUnscaledDouble(0)) + " "
    for i in xrange(1, path.size()):
        pathDString = pathDString + "L" + \
                      str(path.getXUnscaledDouble(i)) + " " + \
                      str(path.getYUnscaledDouble(i)) + " "
    return pathDString

def toSvgPolylineString(path):
    s = "<polyline style=\"fill:none;stroke:blue;stroke-width:5\" points=\""
    for i in xrange(path.size()):
        x = int(path.getXUnscaledDouble(i)*100)
        y = int(path.getYUnscaledDouble(i)*100)
        x = path.getXUnscaled(i)
        y = path.getYUnscaled(i)
        s = s + str(x) + "," + str(y) + " "
    s = s + "\" />"
    return s

def toSvgString_path(path):
    s = "<svg>\n"
    s = s + "    " + "<path style=\"fill:none;stroke:blue;stroke-width:5\" "
    s = s + "d=\"" + toSvgPathDString(path) + "\" />\""
    s = s + "</svg>\n"
    return s

def toSvgString_polyline(path):
    s = "<svg>\n"
    s = s + "    " + toSvgPolylineString(path) + "\n"
    s = s + "</svg>\n"
    return s

##
def run():
    helpText = "This program will batch convert .swc files to " + \
               "SVG vector graphs.\n\n" + \
               ">> Press OK to Select a directory of .swc traces."
    MessageDialog(IJ.getInstance(),"Batch SWC to SVG Guide", helpText)


    d = DirectoryChooser("Chose Traces Dir").getDirectory()
    if d is None:
        IJ.log("Choose Dir Canceled!")
        return

    swc_files = [ os.path.join(d,x) for x in os.listdir(d) if re.search('(?i)\.swc$',x) ]
     
    pafm = PathAndFillManager(10240, # width
                              10240, # height
                              1, # depth
                              1, # x spacing
                              1, # y spacing
                              1, # z spacing
                              "pixel")

    for swc_file in swc_files:
        out_file = swc_file + ".svg"
     
        if not pafm.importSWC(swc_file,False): # second parameter is ignoreCalibration
            IJ.error("Failed to load: "+swc_file)
     
        for i in range(pafm.size()):
            path = pafm.getPath(i)
            
            f = open(out_file, "wb")
            f.write(toSvgString_polyline(path))
            f.close()

            f = open(swc_file + "-path.svg", "wb")
            f.write(toSvgString_path(path))
            f.close()

##############
run()
MessageDialog(IJ.getInstance(),"Batch SWC to SVG Guide", "Done")
