# output a list of nodes associated with connectors labeled by hand

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle

header = ['neuron', 'neurite', 'areatreeId', 'nodeId', 'branch', 'layer', 'x', 'y', 'z', 'area', 'nInputs', 'nOutputs']
foundNeuriteNodes = [header]

project = Project.getProjects().get(1)
projectRoot = project.getRootProjectThing()

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

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if 'apla_' not in neurite.getTitle():
        continue
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

outfile = open('neuritesA.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeuriteNodes)
outfile.close()
            