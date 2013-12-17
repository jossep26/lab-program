# For output a list of neurites(and their nodes) in currently active TrakEM2 project
# Note: Change output filename at the bottom
#       Set zoom at display window to proper value (50~70%)
#       node.getId() only available in mod; if used in original, omit node id field

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
from fiji.geom import AreaCalculations
import csv
from jarray import array

header = ['neuron', 'neurite', 'areatreeId', 'nodeId', 'branch', 'layer', 'x', 'y', 'z', 'area', 'nInputs', 'nOutputs', 'connectors']
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
        for nd in root.getSubtreeNodes():
            # get node coordinates, from tut on web
            fp = array([nd.getX(), nd.getY()], 'f')
            affine.transform(fp, 0, fp, 0, 1)
            x = fp[0] * calibration.pixelWidth
            y = fp[1] * calibration.pixelHeight
            z = nd.getLayer().getZ() * calibration.pixelWidth  # a TrakEM2 oddity

            # get node connections, in/out synapse number, synapse id
            # NOTE: this method seems to be affected by display zoom value
            inAndOuts = layerset.findZDisplayables(Connector, nd.getLayer(), int(fp[0]), int(fp[1]), False)
            nInputs = 0
            nOutputs = 0
            for connector in inAndOuts:
                if connector is None:
                    break
                originTrees = []
                for t in connector.getOrigins(Tree):
                    originTrees.append(t)
                targetTrees = []
                for tSet in connector.getTargets(Tree):
                    for t in tSet:
                        targetTrees.append(t)
                if areatree in originTrees:
                    nOutputs += 1
                if areatree in targetTrees:
                    nInputs += 1

            # get branch id
            if branchTable.has_key(nd):
                branch = branchTable[nd]
            else:
                branch = 0

            # get area
            ndArea = abs( AreaCalculations.area( nd.getData().getPathIterator(None) ) * calibration.pixelWidth * calibration.pixelHeight )

            ndLayerIndex = nd.getLayer().getParent().indexOf(nd.getLayer()) + 1
            # save a line of node profile data
            # ['neuron', 'neurite', 'areatreeId', 'nodeId', 'branch', 'layer', 'x', 'y', 'z', 'area', 'nInputs', 'nOutputs', 'connectors']
            nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), branch, ndLayerIndex, x, y, z, ndArea, nInputs, nOutputs, inAndOuts]
            foundNeuriteNodes.append(nodeData)

outfile = open('neurites.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeuriteNodes)
outfile.close()

