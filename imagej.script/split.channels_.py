from ij import IJ, ImagePlus, ImageStack
from ij.plugin import ChannelSplitter
from ij.io import DirectoryChooser
import os

srcDir = DirectoryChooser("Batch Splitter: Chose Source Dir").getDirectory()
if srcDir is None:
    print "Canceled"
    exit(1)

outDir = DirectoryChooser("Batch Splitter: Chose >Output< Dir").getDirectory()
if outDir is None:
    print "Output to same dir as source."
    ourtDir = srcDir

for root, directories, filenames in os.walk(srcDir):
    for filename in filenames:
        # Skip non-TIF files
        if not filename.endswith(".tif"):
            continue
        inpath = os.path.join(root, filename)

        print "Reading ", filename
        imp = IJ.openImage(inpath)
        if imp is None:
            print "Skipped, wrong with reading: ", filename
            continue
        else:
            splittedimps = ChannelSplitter.split(imp)
            for i, simp in enumerate(splittedimps):
                outfn = os.path.splitext(filename)[0] + "_C_" + str(i) + ".tif"
                outpath = os.path.join(outDir, outfn)
                if os.path.exists(outpath):
                    print "Skipped, already exists: ", outfn
                    continue
                IJ.saveAsTiff(simp, outpath)
                print "Splitted and saved to ", outfn

print "done."
