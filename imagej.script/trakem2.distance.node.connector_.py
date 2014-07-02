# output a list of shortest distance between connectors labeled by hand

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle
import re

## tools
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

def getTreeNeuriteTable(project):
    # return a dict of areatree/treeline vs. project neurite
    t = {}
    projectRoot = project.getRootProjectThing()
    neurites = projectRoot.findChildrenOfTypeR("neurite")
    for neurite in neurites:
        trees = neurite.findChildrenOfTypeR("areatree")
        # trees.addAll(neurite.findChildrenOfTypeR("treeline"))
        for tree in trees:
            t[tree.getObject()] = neurite
    return t

#####
header = ['neuron', 'neurite', 'areatreeId', 'nodeId', 'to', 'from', 'distance']
foundNeuriteNodes = [header]
minDistances = [header]
dConnectorsId = [['neuron', 'neurite', 'areatreeId', 'nodeId', 'to', 'from', 'toId', 'fromId', 'distance']]
connectorProfile = [['connectorId', 'neuron', 'neurite', 'areatreeId', 'nodeId', 'direction']]

project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if re.match(r"^apla_", neurite.getTitle()) is None:
        continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None:
            break
        
        layerset = areatree.getLayerSet()
        calibration = layerset.getCalibration()
        affine = areatree.getAffineTransform()

        cTable = findConnectorsInTree(areatree)
        outputs = cTable['outgoing']
        inputs = cTable['incoming']
        ndIn = inputs.keys()
        ndOut = outputs.keys()
        if 0 == len(ndIn) or 0 == len(ndOut) :
            continue

        # connector reference table
        for nd, connectors in outputs.iteritems():
            for c in connectors:
                p = [c.getId(), neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing']
                connectorProfile.append(p)
        for nd, connectors in inputs.iteritems():
            for c in connectors:
                p = [c.getId(), neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming']
                connectorProfile.append(p)
        # calculate distance for each input
        for nd in ndIn:
            ds = []
            for tnd in ndOut:
                # from output
                d = MeasurePathDistance(areatree, nd, tnd).getDistance()
                nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming', 'outgoing', d]
                foundNeuriteNodes.append(nodeData)
                # for min
                ds.append(d)
                # for connectors with id
                for toCt in inputs[nd]:
                    for fromCt in outputs[tnd]:
                        connectorData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming', 'outgoing', toCt.getId(), fromCt.getId(), d]
                        dConnectorsId.append(connectorData)
            if not ds:  # empty
                text = 'NA'
            else:
                text = min(ds)
            minData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming', 'outgoing', text]
            minDistances.append(minData)

            ds = []
            for tnd in ndIn:
                # from input
                if tnd == nd:
                    continue
                d = MeasurePathDistance(areatree, nd, tnd).getDistance()
                nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming', 'incoming', d]
                foundNeuriteNodes.append(nodeData)
                # for min
                ds.append(d)
                # for connectors with id
                for toCt in inputs[nd]:
                    for fromCt in inputs[tnd]:
                        connectorData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming', 'incoming', toCt.getId(), fromCt.getId(), d]
                        dConnectorsId.append(connectorData)
            if not ds:  # empty
                text = 'NA'
            else:
                text = min(ds)
            minData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming', 'incoming', text]
            minDistances.append(minData)

        # calculate distance for each out
        for nd in ndOut:
            ds = []
            for tnd in ndOut:
                # from output
                if tnd == nd:
                    continue
                d = MeasurePathDistance(areatree, nd, tnd).getDistance()
                nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing', 'outgoing', d]
                foundNeuriteNodes.append(nodeData)
                # for min
                ds.append(d)
                # for connectors with id
                for toCt in outputs[nd]:
                    for fromCt in outputs[tnd]:
                        connectorData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing', 'outgoing', toCt.getId(), fromCt.getId(), d]
                        dConnectorsId.append(connectorData)
            if not ds:  # empty
                text = 'NA'
            else:
                text = min(ds)
            minData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing', 'outgoing', text]
            minDistances.append(minData)

            ds = []
            for tnd in ndIn:
                # from input
                d = MeasurePathDistance(areatree, nd, tnd).getDistance()
                nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing', 'incoming', d]
                foundNeuriteNodes.append(nodeData)
                # for min
                ds.append(d)
                # for connectors with id
                for toCt in outputs[nd]:
                    for fromCt in inputs[tnd]:
                        connectorData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing', 'incoming', toCt.getId(), fromCt.getId(), d]
                        dConnectorsId.append(connectorData)
            if not ds:  # empty
                text = 'NA'
            else:
                text = min(ds)
            minData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing', 'incoming', text]
            minDistances.append(minData)

        # # input synapses
        # for nd, d in ndInDistance.iteritems():
        #     # get node coordinates, from tut on web
        #     fp = array([nd.getX(), nd.getY()], 'f')
        #     affine.transform(fp, 0, fp, 0, 1)
        #     x = fp[0] * calibration.pixelWidth
        #     y = fp[1] * calibration.pixelHeight
        #     z = nd.getLayer().getZ() * calibration.pixelWidth  # a TrakEM2 oddity

        #     # get area
        #     ndArea = abs( AreaCalculations.area( nd.getData().getPathIterator(None) ) * calibration.pixelWidth * calibration.pixelHeight )

        #     ndLayerIndex = nd.getLayer().getParent().indexOf(nd.getLayer()) + 1
        #     # save a line of node profile data
        #     # ['neuron', 'neurite', 'areatreeId', 'nodeId', 'synapseDirection', 'layer', 'x', 'y', 'z', 'area', 'distance']
        #     nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming', ndLayerIndex, x, y, z, ndArea, d]
        #     foundNeuriteNodes.append(nodeData)

        # # output synapses
        # for nd, d in ndOutDistance.iteritems():
        #     # get node coordinates, from tut on web
        #     fp = array([nd.getX(), nd.getY()], 'f')
        #     affine.transform(fp, 0, fp, 0, 1)
        #     x = fp[0] * calibration.pixelWidth
        #     y = fp[1] * calibration.pixelHeight
        #     z = nd.getLayer().getZ() * calibration.pixelWidth  # a TrakEM2 oddity

        #     # get area
        #     ndArea = abs( AreaCalculations.area( nd.getData().getPathIterator(None) ) * calibration.pixelWidth * calibration.pixelHeight )

        #     ndLayerIndex = nd.getLayer().getParent().indexOf(nd.getLayer()) + 1
        #     # save a line of node profile data
        #     # ['neuron', 'neurite', 'areatreeId', 'nodeId', 'synapseDirection', 'layer', 'x', 'y', 'z', 'area', 'distance']
        #     nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing', ndLayerIndex, x, y, z, ndArea, d]
        #     foundNeuriteNodes.append(nodeData)

outfile = open('synapse-distances.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeuriteNodes)
outfile.close()

# min
outfile = open('synapse-min-distances.csv','wb')
writer = csv.writer(outfile)
writer.writerows(minDistances)
outfile.close()

# connector with id
outfile = open('synapse-id-distances.csv','wb')
writer = csv.writer(outfile)
writer.writerows(dConnectorsId)
outfile.close()

# connector profiles
outfile = open('synapse-profiles.csv','wb')
writer = csv.writer(outfile)
writer.writerows(connectorProfile)
outfile.close()
