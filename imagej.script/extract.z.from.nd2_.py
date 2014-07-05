import re
import os
from ij.io import DirectoryChooser
from loci.plugins.in import ImportProcess, ImporterOptions


def run():
    srcDir = DirectoryChooser("Batch Splitter: Chose Source Dir").getDirectory()
    # print srcDir
    # print type(srcDir)
    if srcDir is None:
        return

    sumf = open(os.path.join(srcDir, 'summary.z.txt'), 'w')
    # fn = r'e:\Data\data\zby\imaging\20140627.imaging.alignment.z\526-4eGH146GC3-mCherry001.nd2'
    # # fn = r'e:\Data\data\zby\imaging\20140627.imaging.alignment.z\526-4eGH146GC3-mCherry011.nd2'
    # outfn = r'e:\Data\data\zby\imaging\20140627.imaging.alignment.z\526-4eGH146GC3-mCherry001.txt'

    zString = ["Z position for position, plane #01", "Z position for position, plane #001", "dZStep", "dZLow", "dZPos", "dZHigh"]

    for fn in os.listdir(srcDir):
        # Skip non-ND2 files
        if not fn.endswith(".nd2"):
            continue

        # get input and output filenames
        fullfn = os.path.join(srcDir, fn)
        outfn = os.path.splitext(fn)[0] + ".z.txt"
        fulloutfn = os.path.join(srcDir, outfn)
        # if os.path.exists(fulloutfn):
        #     print "Skipped, already exists: ", outfn
        #     continue

        print "Reading ", fn
        sumf.write(fn)
        sumf.write('\n')
        op = ImporterOptions()
        op.setId(fullfn)
        process = ImportProcess(op)
        process.execute()
        meta = process.getOriginalMetadata()

        print "Writing", fulloutfn
        f = open(fulloutfn, 'w')
        for k in meta.keySet():
            if k in zString:
                line = ''.join([k, '\t', str(meta[k])])
                f.write(line)
                f.write('\n')
                sumf.write(line)
                sumf.write('\n')                
        f.close()
        sumf.write('\n')
    sumf.close()
    print 'done.'

run()
