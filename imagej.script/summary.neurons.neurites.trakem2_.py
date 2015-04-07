# For output a list of neurons/neurites in currently active TrakEM2 project
#   with the same sequence as seen in project tab
# Change output filename at the bottom
# 
# author Bangyu Zhou, 2015 Apr 4

from ini.trakem2 import Project
from ini.trakem2.display import AreaList, Display, AreaTree, Treeline, Connector
from jarray import array
import csv

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

header = ['neurite', 'neuron', 'areatreeIds', 'nNodes', 'length', 'nInputs', 'nOutputs']
foundNeurons = [header]

# get the first open project, project root, and 'drosophila_brain'
project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()
brain = projectRoot.findChildrenOfType("drosophila_brain")[0]

neurons = brain.findChildrenOfType("neuron")
for neuron in neurons:
    neurites = neuron.findChildrenOfType("neurite")
    for neurite in neurites:
        nNodes = 0
        length = 0
        nInputs = 0
        nOutputs = 0
        areatrees = neurite.findChildrenOfType("areatree")
        areatreeIds = []
        for areatree in areatrees:
            areatree = areatree.getObject()

            areatreeIds.append(areatree.getId())

            dt = getTreeDistanceTable(areatree)
            length += sum([d for nd, d in dt.iteritems()])

            synapses = findConnectorsInTree(areatree)
            nInputs = len(synapses['incoming'])
            nOutputs = len(synapses['outgoing'])

            root = areatree.getRoot()
            if root is None:
                continue
            nNodes += len(root.getSubtreeNodes())
        foundNeurons.append([neurite.getTitle(), neuron.getTitle(), areatreeIds, nNodes, length, nInputs, nOutputs])

outfile = open('sum.neurons.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeurons)
outfile.close()
