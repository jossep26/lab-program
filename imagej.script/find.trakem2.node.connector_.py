# output a list of nodes associated with connectors

from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Tree, Treeline
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle
import re

##### tools #####
# recursive function to assign nodes with 'branch id' to mark different linear segments
branchId = 0
branchTable = {}
def markTreeBranch(node):
    global branchId
    global branchTable
    for nd in node.getSlabNodes():
        # print "branch degree", branchId, "at node", nd.getId()
        branchTable[nd] = branchId
    for childnd in nd.getChildren():
        branchId += 1
        markTreeBranch(childnd)

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

def findConnectedTree(tree):
    # returns a dict of two values, each contains a dict of node versus tree
    if isinstance(tree, AreaTree):
        fixAreatreeArea(tree)
    outputs = {}
    inputs = {}
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
                # outgoing connector
                t = filter(isTree, [t for ts in connector.getTargets() for t in ts])
                t = set(t)
                # print 'targets', t
                if nd in outputs:
                    outputs[nd] = outputs[nd].union(t)
                else:
                    outputs[nd] = t
            else:
                o = filter(isTree, connector.getOrigins())
                o = set(o)
                # print 'origin', o
                if nd in inputs:
                    inputs[nd] = inputs[nd].union(o)
                else:
                    inputs[nd] = o
    return {'outputs':outputs, 'inputs':inputs}

def fixAreatreeArea(areatree):
    # Append a 1-pixel square area for nodes without any area
    # this will fix using findZDisplayables for finding areatree, 
    #     including connector.getTargets(), connector.getOrigins() etc.
    if not isinstance(areatree, AreaTree):
        print "Error: input must be an AreaTree"
        return
    root = areatree.getRoot()
    if root is None:
        return
    for nd in root.getSubtreeNodes():
        a = nd.getArea()
        a.add(Area(Rectangle(int(nd.getX()), int(nd.getY()), 1, 1)))
        nd.setData(a)

##### tools end #####

header = ['neuron', 'neurite', 'areatreeId', 'nodeId', 'branch', 'layer', 'x', 'y', 'z', 'area', 'nInputs', 'nOutputs']
foundNeuriteNodes = [header]

project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if 'test_' not in neurite.getTitle():
        continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None:
            break

        cTable = findConnectorsInTree(areatree) # auto find connectors
        print findConnectedTree(areatree)
        branchId = 1
        branchTable = {}
        markTreeBranch(root)

        layerset = areatree.getLayerSet()
        calibration = layerset.getCalibration()
        affine = areatree.getAffineTransform()
        for nd in root.getSubtreeNodes():
            # manually labeled synapse
            tags = nd.getTags()
            nOutputs = 0
            nInputs = 0
            if tags is None:
                continue
            for tag in tags:
                if 'output_' in tag.toString():
                    nOutputs = 1
                if 'input_' in tag.toString():
                    posN = tag.toString().find('_')
                    nInputs = int(tag.toString()[posN+1 :])
            if 0 == (nOutputs + nInputs):
                continue
                    
            # auto find synapse
            nAutoOut = 0
            nAutoIn = 0
            outputs = cTable['outgoing']
            inputs = cTable['incoming']
            if nd in outputs:
                nAutoOut = len(outputs[nd])
            if nd in inputs:
                nAutoIn = len(inputs[nd])
            if nOutputs != nAutoOut or nInputs != nAutoIn:
                print nd, 'MAN', nOutputs, 'outputs', nInputs, 'inputs'
                print nd, 'AUTO', nAutoOut, 'outputs', nAutoIn, 'inputs'
            # get node coordinates, from tut on web
            fp = array([nd.getX(), nd.getY()], 'f')
            affine.transform(fp, 0, fp, 0, 1)
            x = fp[0] * calibration.pixelWidth
            y = fp[1] * calibration.pixelHeight
            z = nd.getLayer().getZ() * calibration.pixelWidth  # a TrakEM2 oddity

            # get branch id
            if branchTable.has_key(nd):
                branch = branchTable[nd]
            else:
                branch = 0

            # get area
            ndArea = abs( AreaCalculations.area( nd.getData().getPathIterator(None) ) * calibration.pixelWidth * calibration.pixelHeight )

            ndLayerIndex = nd.getLayer().getParent().indexOf(nd.getLayer()) + 1
            # save a line of node profile data
            # ['neuron', 'neurite', 'areatreeId', 'nodeId', 'branch', 'layer', 'x', 'y', 'z', 'area', 'nInputs', 'nOutputs', 'input', 'output']
            nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), branch, ndLayerIndex, x, y, z, ndArea, nInputs, nOutputs]
            foundNeuriteNodes.append(nodeData)

# outfile = open('neuritesConnectors01.csv','wb')
# writer = csv.writer(outfile)
# writer.writerows(foundNeuriteNodes)
# outfile.close()
