from ini.trakem2.display import Tag
from java.awt.event import KeyEvent
from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Node
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle
import re


def mean(xs):
    if 0 == len(xs):
        return
    return sum(xs)/len(xs)

def var(xs):
    if 1 >= len(xs):
        return
    mean = sum(xs)/len(xs)
    v = (reduce(lambda s, e: s + pow(e - mean, 2),
                          xs, 0)) / (len(xs) - 1)
    return v

def std(xs):
    return var(xs) ** 0.5

def stderr(xs):
    return std(xs)/ len(xs) ** 0.5

def getNodeXYZ(nd, cal, at):
    # get node coordinates, from tut on web
    fp = array([nd.getX(), nd.getY()], 'f')
    at.transform(fp, 0, fp, 0, 1)
    x = fp[0] * cal.pixelWidth
    y = fp[1] * cal.pixelHeight
    z = nd.getLayer().getZ() * cal.pixelWidth  # a TrakEM2 oddity
    return [x, y, z]

def getTreeDistanceTable(tree):
    # calculate and store each node's distance to its parent node
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

def getInputs(nodes):
    inTable = {}
    nInputs = 0
    for nd in nodes:
        tags = nd.getTags()
        if tags is None:
            continue
        for tag in tags:
            if 'input_' in tag.toString():
                posN = tag.toString().find('_')
                nIn = int(tag.toString()[posN+1 :])
                inTable[nd] = nIn
    return inTable

def getLongestPathNodes(areatree):
    # requires ini.trakem2.display.Tree.MeasurePathDistance
    root = areatree.getRoot()
    endNodes = set([nd for nd in areatree.getEndNodes()])
    branchNodes = set([nd for nd in areatree.getBranchNodes()])
    if 2 == root.getChildrenCount():
        branchNodes.discard(root)

    # case 0. root is the only node
    if 0 == root.getChildrenCount():
        print 'root singleton'
        return
    # case 1. else
    else:
        # get longest path from each lobe
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
    return [ndtop, ndbottom]

def getCutNodes(root):
    cutNodes = []
    for nd in root.getSubtreeNodes():
        tags = nd.getTags()
        if tags is None:
            continue
        for tag in tags:
            if 'output_' in tag.toString():
                cutNodes.append(nd)
                break
    return set(cutNodes)

def markTreeSegment(root):
    cutNodes = getCutNodes(root)
    branchNodes = set([nd for nd in root.getBranchNodes()])
    branchCutNodes = branchNodes.intersection(cutNodes)
    markings = {}
    segId = 0
    for nd in root.getSubtreeNodes():
        markings[nd] = set([segId])
    segId += 1
    for cnd in cutNodes:
        if cnd in branchNodes:
            markings[cnd].add(segId)
            for chnd in cnd.getChildrenNodes():
                segId += 1
                for nd in chnd.getSubtreeNodes():
                    markings[nd].add(segId)
        else:
            for nd in cnd.getSubtreeNodes():
                markings[nd].add(segId)
            segId += 1

    markings.update((k, frozenset(v)) for k, v in markings.iteritems())

    # substitute set of ids to unique single id
    segIdSets = frozenset([v for k, v in markings.iteritems()])
    setToIdTable = {}
    for i, segIdSet in enumerate(segIdSets):
        setToIdTable[segIdSet] = i
    markings2 = {}
    for nd, idSet in markings.iteritems():
        i = setToIdTable[idSet]
        markings2[nd] = set([i])
    for nd in cutNodes:
        if nd in branchNodes:
            for chnd in nd.getChildrenNodes():
                if chnd in cutNodes:
                    continue
                markings2[nd] = markings2[nd].union(markings2[chnd])
        pnd = nd.getParent()
        if pnd is None or pnd in cutNodes:
            continue
        pidSet = markings2[pnd]
        markings2[nd] = markings2[nd].union(pidSet)

    markingsRev = {}
    for nd, iSet in markings2.iteritems():
        for i in iSet:
            if i in markingsRev:
                markingsRev[i] = markingsRev[i].union(set([nd]))
            else:
                markingsRev[i] = set([nd])

    uniqueMarkingsRev = {}
    for i, nds in markingsRev.iteritems():
        if 1 == len(nds):
            continue
        uniqueMarkingsRev[i] = nds

    return uniqueMarkingsRev

header = ['neuron','neurite','areatreeId','segmentId','length','nBranches','z','nInputs','meanInputDistance','varInputDistance']
outputdata = [header]

project = Project.getProjects().get(2)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if re.match(r"^(test|apla_|in_|out_)", neurite.getTitle()) is None:
        continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        layerset = areatree.getLayerSet()
        calibration = layerset.getCalibration()
        affine = areatree.getAffineTransform()
        print areatree

        root = areatree.getRoot()
        endNodes = set([nd for nd in areatree.getEndNodes()])
        branchNodes = set([nd for nd in areatree.getBranchNodes()])
        if 2 == root.getChildrenCount():
            branchNodes.discard(root)
        cutNodes = getCutNodes(root)
        dt = getTreeDistanceTable(areatree)
        topnd, bottomnd = getLongestPathNodes(areatree)
        mnds = set(MeasurePathDistance(areatree, topnd, bottomnd).getPath())

        markings = markTreeSegment(root)
        for i, nds in markings.iteritems():
            length = sum([d for nd, d in dt.iteritems() if nd in nds])
            mainSegNds = nds.intersection(mnds)
            subSegNds = nds.difference(mnds)
            segBranchNds = branchNodes.intersection(nds).difference(cutNodes)
            segCutNds = cutNodes.intersection(nds)

            ndXYZs = [getNodeXYZ(nd, calibration, affine) for nd in nds]
            zs = [z for x,y,z in ndXYZs]
            meanZ = sum(zs)/len(zs)
            inputs = getInputs(nds)
            inDistance = []
            for innd, n in inputs.iteritems():
                # nearest distance from input to ouput(cut points)
                ds = []
                for cnd in segCutNds:
                    ds.append(MeasurePathDistance(areatree, innd, cnd).getDistance())
                if 0 != len(ds):
                    d = min(ds)
                    inDistance.extend([d]*n)
            # print inDistance, len(inDistance)
            # print mainSegNds
            # print 'branch', bSegNds
            # for nd in nds:
            #     nd.addTag(Tag(str(i), KeyEvent.VK_K))
            # for nd in mainSegNds:
            #     nd.addTag(Tag(str(i)+'main', KeyEvent.VK_K))
            # for nd in bSegNds:
            #     nd.addTag(Tag(str(i)+'b', KeyEvent.VK_K))
            #['neuron','neurite','areatreeId','segmentId','length','nBranches','z','nInputs','meanInputDistance','varInputDistance']
            outputdata.append([neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), i, length, len(segBranchNds), meanZ, len(inDistance), mean(inDistance), var(inDistance)])

# print outputdata
print 'writing ...'
outfile = open('segments.csv','wb')
writer = csv.writer(outfile)
writer.writerows(outputdata)
outfile.close()
print 'done.'