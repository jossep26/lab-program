# For output a list of synapses of neurites(and their nodes) in currently active TrakEM2 project
# Note: Change output filename at the bottom
#       Set zoom at display window to proper value (50~70%)
#       node.getId() only available in mod; if used in original, omit node id field

from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Treeline
from ini.trakem2 import Project
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle

header = ['neuron', 'neurite', 'areatreeId', 'nodeId', 'synapseId', 'direction', 'nTargets']
foundSynapses = [header]

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


# get the first open project
project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None:
            continue

        layerset = areatree.getLayerSet()
        calibration = layerset.getCalibration()
        affine = areatree.getAffineTransform()
        # outAndInArray = areatree.findConnectors()
        outAndIn = findConnectorsInTree(areatree)
        outs = outAndIn['outgoing']
        ins = outAndIn['incoming']

        for nd, synapses in outs.iteritems():
            for synapse in synapses:
                # save a line of synapse profile data
                # ['neuron', 'neurite', 'areatreeId', 'nodeId', 'synapseId', 'direction', 'nTargets']
                synapseData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), synapse.getId(), 'outgoing', synapse.getTargetCount()]
                foundSynapses.append(synapseData)
        for nd, synapses in ins.iteritems():
            for synapse in synapses:
                # save a line of synapse profile data
                # ['neuron', 'neurite', 'areatreeId', 'nodeId', 'synapseId', 'direction', 'nTargets']
                synapseData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), synapse.getId(), 'incoming', synapse.getTargetCount()]
                foundSynapses.append(synapseData)

outfile = open('synapses.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundSynapses)
outfile.close()

