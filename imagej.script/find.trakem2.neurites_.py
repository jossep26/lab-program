# For output a list of neurites(and their nodes) in currently active TrakEM2 project
# Note: Change output filename at the bottom
#       Set zoom at display window to proper value (50~70%)
#       node.getId() only available in mod; if used in original, omit node id field

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle

header = ['neuron', 'neurite', 'areatreeId', 'nodeId', 'branch', 'layer', 'x', 'y', 'z', 'area', 'nInputs', 'nOutputs', 'input', 'output']
foundNeuriteNodes = [header]

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
            break

        branchId = 1
        branchTable = {}
        markTreeBranch(root)

        layerset = areatree.getLayerSet()
        calibration = layerset.getCalibration()
        affine = areatree.getAffineTransform()
        # outAndInArray = areatree.findConnectors()
        for nd in root.getSubtreeNodes():
            # get node coordinates, from tut on web
            fp = array([nd.getX(), nd.getY()], 'f')
            affine.transform(fp, 0, fp, 0, 1)
            x = fp[0] * calibration.pixelWidth
            y = fp[1] * calibration.pixelHeight
            z = nd.getLayer().getZ() * calibration.pixelWidth  # a TrakEM2 oddity

            # get node connections, in/out synapse number, synapse id
            # NOTE: this method seems to be affected by display zoom value
            area = Area(Rectangle(int(fp[0]), int(fp[1]), 1, 1))
            # area.transform(affine)
            inAndOuts = layerset.findZDisplayables(Connector, nd.getLayer(), area, False, False)
            outgoing = []
            incoming = []
            for connector in inAndOuts:
                if connector is None:
                    break
                if connector.intersectsOrigin(area, nd.getLayer()):
                    outgoing.append(connector)
                else:
                    incoming.append(connector)
            nInputs = len(incoming)
            nOutputs = len(outgoing)
            outgoingIds = [x.getId() for x in outgoing]
            incomingIds = [x.getId() for x in incoming]

            # get node connections, out/in synapse number, synapse id

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
            nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), branch, ndLayerIndex, x, y, z, ndArea, nInputs, nOutputs, incomingIds, outgoingIds]
            foundNeuriteNodes.append(nodeData)

outfile = open('neurites.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeuriteNodes)
outfile.close()

