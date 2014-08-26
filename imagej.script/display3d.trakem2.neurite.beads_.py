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
from javax.swing.tree import DefaultMutableTreeNode

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

def getConnectorTable(project):
    # return a dict of connector vs. project thing
    t = {}
    projectRoot = project.getRootProjectThing()
    connectors = projectRoot.findChildrenOfTypeR("connector")
    for connector in connectors:
        t[connector.getObject()] = connector
    return t

project = Project.getProjects().get(0)
projectTree = project.getProjectTree()
projectRoot = project.getRootProjectThing()
ct = getConnectorTable(project)
neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if re.match(r"^apla_d", neurite.getTitle()) is None:
        continue

    # prepare a new 'color_**' neurite for areatree segments
    for sibl in neurite.getParent().findChildrenOfType("neurite"):
        if "color_" + neurite.getTitle() in sibl.getTitle():
            projectTree.remove(False, sibl, None)
    colorPt = neurite.getParent().createChild("neurite")
    colorPt.setTitle("color_" + neurite.getTitle())
    nn = projectTree.findNode(neurite, projectTree)
    cn = DefaultMutableTreeNode(colorPt)
    projectTree.getModel().insertNodeInto(cn, nn.getParent(), nn.getParent().getChildCount())

    areatreePts = neurite.findChildrenOfTypeR("areatree")
    for areatreePt in areatreePts:

        # display connectors first
        oiPt = getOutAndInPt(areatreePt, ct)
        oiPt = [x for y in oiPt for x in y]
        if oiPt is None: continue
        for c in oiPt:
            Display3D.show(c, False, 5)

        areatree = areatreePt.getObject()
        las = areatree.getLayerSet()

        # add a clone of areatree to 'color_***' neurite
        colortree = areatree.clone(project, False)
        colortreePt = ProjectThing(areatreePt.getTemplate(), project, colortree)
        las.add(colortree)
        colorPt.addChild(colortreePt)
        catn = DefaultMutableTreeNode(colortreePt)
        projectTree.getModel().insertNodeInto(catn, cn, 0)
        print colorPt, colortreePt

        # prepare cut and bead nodes 
        root = colortree.getRoot()
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
        # markings = markTreeSegment(colortree, set(cuts))
        subtrees = set([colortree])
        for cut in cuts:
            ctree = None
            for subtree in subtrees:
                if cut in subtree.getRoot().getSubtreeNodes():
                    ctree = subtree
                    break
            if not ctree: continue
            cutted = ctree.splitAt(cut)
            subtrees.update(set(cutted))
        print 'cut into', len(subtrees), 'segments:', subtrees
        for subtree in subtrees:
            # change color and show in 3D
            las.add(subtree)
            if subtree != colortree:
                spt = project.getProjectTree().addSibling(colortree, subtree).getUserObject()
            else:
                spt = colortreePt
            for bead in beadMarks:
                if bead in subtree.getRoot().getSubtreeNodes():
                    subtree.setColor(Color(255, 53, 0))
                    for nd in subtree.getRoot().getSubtreeNodes():
                        nd.setColor(Color(255, 53, 0))
            subtree.setAlpha(0.6)
            Display3D.show(spt, False, 5)

        # for i, nds in markings.iteritems():
        #     if beadMarks.intersection(nds):
        #         beads.append(nds)
        #     else:
        #         strings.append(nds)
        
        # bc = Color(255,153,0)
        # for bead in beads:
        #     tmpat = areatree.clone(project, False)
        #     for nd in tmpat.getRoot().getSubtreeNodes():
        #         if nd not in bead:
        #             tmpat.removeNode(nd)
        #     tmpat.setColor(bc)
        #     Display3D.show(tmpat, False, 5)
