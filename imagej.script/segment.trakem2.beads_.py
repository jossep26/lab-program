from ini.trakem2 import Project
from java.awt.event import KeyEvent
from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Node, Treeline, Tag
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle, Color
import re


def getCutNodes(tree):
    root = tree.getRoot()
    if root is None:
        return
    cs = findConnectorsInTree(tree)
    cutNodes = cs['outgoing'].keys()
    return set(cutNodes)

def markTreeSegment(tree, cutNodes=None):
    root = tree.getRoot()
    if root is None:
        return
    if cutNodes is None: 
        cutNodes = getCutNodes(tree)
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

def getOutAndInPt(areatreePt, connectorTable):
    if not isinstance(areatreePt, ProjectThing):
        return None
    projectRoot = areatreePt.getRootParent()
    areatree = areatreePt.getObject()
    outAndIn = findConnectorsInTree(areatree)
    outPt = []
    inPt = []
    for direction, ndVsC in outAndIn.iteritems():
        for nd, connectors in ndVsC.iteritems():
            for connector in connectors:
                if direction == 'outgoing':
                    outPt.append(connectorTable[connector])
                elif direction == 'incoming':
                    inPt.append(connectorTable[connector])
    return [outPt, inPt]

def getConnectorTable(project):
    # return a dict of connector vs. project thing
    t = {}
    projectRoot = project.getRootProjectThing()
    connectors = projectRoot.findChildrenOfTypeR("connector")
    for connector in connectors:
        t[connector.getObject()] = connector
    return t

def isTree(x):
    if isinstance(x, Connector):
        return False
    return isinstance(x, Treeline) or isinstance(x, AreaTree)

def findConnectorsInTree(tree):
    # returns a dict of two values, each contains a dict of node versus connectors
    if not isTree(tree):
        print "error: input is neither Treeline or AreaTree"
        return
    outgoing = {}
    incoming = {}
    las = tree.getLayerSet()
    cal = las.getCalibration()
    at = tree.getAffineTransform()
    root = tree.getRoot()
    if root is None:
        return
    for nd in root.getSubtreeNodes():
        # copied from TrakEM2_Scripting and Tree.java
        la = nd.getLayer()
        area = nd.getArea().clone()
        area.transform(at)
        cs = las.findZDisplayables(Connector, la, area, False, False)
        if cs.isEmpty():
            continue
        for connector in cs:
            # print 'found', connector
            if connector.intersectsOrigin(area, la):
                if nd in outgoing:
                    outgoing[nd].append(connector)
                else:
                    outgoing[nd] = [connector]
            else:
                if nd in incoming:
                    incoming[nd].append(connector)
                else:
                    incoming[nd] = [connector]
    return {'outgoing':outgoing, 'incoming':incoming}

nodes = [['neurite', 'areatreeId', 'nodeId', 'class']]

project = Project.getProjects().get(0)
projectTree = project.getProjectTree()
projectRoot = project.getRootProjectThing()
ct = getConnectorTable(project)
neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if re.match(r"^apla_d", neurite.getTitle()) is None:
        continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None: continue
        cuts = []
        beadMarks = set([])
        for nd in root.getSubtreeNodes():
            tags = nd.getTags()
            if tags is None:
                continue
            for tag in tags:
                if 'CUT' in tag.toString():
                    cuts.append(nd)
                if 'BEAD' in tag.toString():
                    beadMarks.add(nd)
        markings = markTreeSegment(areatree, set(cuts))
        for i, nds in markings.iteritems():
            if nds.intersection(beadMarks):
                tp = 'bead'
            else:
                tp = 'string'
            for nd in nds:
                nodes.append([neurite.getTitle(), areatree.getId(), nd.getId(), tp])

outfile = open('beads.csv','wb')
writer = csv.writer(outfile)
writer.writerows(nodes)
outfile.close()
