from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Node
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle
import re

def getNodeXYZ(nd, cal, at):
    # get node coordinates, from tut on web
    fp = array([nd.getX(), nd.getY()], 'f')
    at.transform(fp, 0, fp, 0, 1)
    x = fp[0] * cal.pixelWidth
    y = fp[1] * cal.pixelHeight
    z = nd.getLayer().getZ() * cal.pixelWidth  # a TrakEM2 oddity
    return [x, y, z]

def getTreeDistanceTable(tree):
    dTable = {}
    layerset = tree.getLayerSet()
    calibration = layerset.getCalibration()
    affine = tree.getAffineTransform()
    root = tree.getRoot()
    if root is None:
        return
    for nd in root.getSubtreeNodes():
        x, y, z = getNodeXYZ(nd, calibration, affine)
        if nd.getParent() is None:
            # root
            xp, yp, zp = [x, y, z]
        else:
            xp, yp, zp = getNodeXYZ(nd.getParent(), calibration, affine)
        d = ((x-xp)**2 + (y-yp)**2 + (z-zp)**2) ** (0.5)
        dTable[nd] = d
    return dTable

def std(xs):
    mean = sum(xs)/len(xs)
    std = (reduce(lambda s, e: s + pow(e - mean, 2),
                          xs, 0)) ** 0.5 / len(xs)
    return std

def getXYScatterness(tree, nodes):
    nodes = set(nodes)
    layerset = tree.getLayerSet()
    calibration = layerset.getCalibration()
    affine = tree.getAffineTransform()
    root = tree.getRoot()
    if root is None:
        return
    coords = [getNodeXYZ(nd, calibration, affine) for nd in nodes]
    xs = []
    ys = []
    # zs = []
    for x, y, z in coords:
        xs.append(x)
        ys.append(y)
        # zs.append(z)

    return max(xs) - min(xs) + max(ys) - min(ys)

# prepare output
header = ['neuron','neurite','areatreeId','branchGroup','length','branchPos', 'nBranches','nodeScatterness']
outdata = [header]

project = Project.getProjects().get(1)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if re.match(r"^(test|apla_|in_|out_)", neurite.getTitle()) is None:
        continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        dTable = getTreeDistanceTable(areatree)
        root = areatree.getRoot()
        endNodes = set([nd for nd in areatree.getEndNodes()])
        branchNodes = set([nd for nd in areatree.getBranchNodes()])
        if 2 == root.getChildrenCount():
            branchNodes.discard(root)
        if root in branchNodes:
            print '-----root is branch------'
            print areatree
        else:
            print '---root is not branch---'
            print areatree

        # case 0. root is the only node
        if 0 == root.getChildrenCount():
            print 'root singleton'
        else:
            # get longest path from each half
            ndVsLen = {}
            ndVsLen[root] = 0.0    # compatibility when root children count is 1
            for loberoot in root.getChildrenNodes():
                lbEndNodes = [nd for nd in loberoot.getEndNodes()]
                lbBranchNodes = [nd for nd in loberoot.getBranchNodes()]
                lbMaxLen = 0.0
                lbMaxPM = None
                lbMaxNd = lbEndNodes[0]
                for nd in lbEndNodes:
                    pm = MeasurePathDistance(areatree, nd, root)
                    if lbMaxLen <= pm.getDistance():
                        lbMaxLen = pm.getDistance()
                        lbMaxPM = pm
                        lbMaxNd = nd
                ndVsLen[lbMaxNd] = lbMaxLen
                # print 'lobe max', nd, lbMaxLen
            longestNodes = sorted(ndVsLen, key=ndVsLen.get, reverse=True)
            nda = longestNodes[0]
            ndb = longestNodes[1]
            if nda.getLayer().getParent().indexOf(nd.getLayer()) >= ndb.getLayer().getParent().indexOf(nd.getLayer()):
                ndtop = nda
                ndbottom = ndb
            else:
                ndtop = ndb
                ndbottom =nda
            pm = MeasurePathDistance(areatree, ndtop, ndbottom)
            maintreeLength = pm.getDistance()

            mainTreeNodes = set(pm.getPath())
            # print 'scatterness', getXYScatterness(areatree, mainTreeNodes)
            # branch nodes on main tree
            mainBranchNodes = mainTreeNodes.intersection(branchNodes)
            # main tree data['neuron','neurite','areatreeId','branchGroup','length','branchPos','nBranches','nodeScatterness']
            outdata.append([neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), 'main_tree', maintreeLength, '', len(mainBranchNodes), getXYScatterness(areatree, mainTreeNodes)])
            for mbnd in mainBranchNodes:
                subtreeNodes = set(mbnd.getSubtreeNodes())
                subtreeNodes = subtreeNodes.difference(mainTreeNodes)
                subBranchNodes = set(mbnd.getBranchNodes())
                subBranchNodes.discard(mbnd)
                totalLength = sum([d for nd, d in dTable.iteritems() if nd in subtreeNodes])
                zpos = MeasurePathDistance(areatree, ndtop, mbnd).getDistance() / maintreeLength
                # each branch in total
                outdata.append([neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), 'major_branch', totalLength, zpos, len(subBranchNodes), getXYScatterness(areatree, subtreeNodes)])
                
print 'writing to file ...'
outfile = open('branches.csv','wb')
writer = csv.writer(outfile)
writer.writerows(outdata)
outfile.close()
print 'done.'