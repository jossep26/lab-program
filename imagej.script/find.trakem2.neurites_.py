# For output a list of neurites(and their nodes) in currently active TrakEM2 project
# Change output filename at the bottom
# Set zoom at display window to proper value (50~70%)

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
import csv
from jarray import array


header = ['neuron', 'neurite', 'branch', 'layer', 'x', 'y', 'z', 'area', 'nInputs', 'nOutputs', 'connectors']
foundNeuriteNodes = [header]

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
        layerset = areatree.getLayerSet()
        calibration = layerset.getCalibration()
        affine = areatree.getAffineTransform()
        
        # nodes = root.getSlabNodes()
        # nodes = [nd for nd in nodes]
        # print neurite.getParent().getTitle(), neurite.getTitle(), len(nodes)
        # print areatree.getTitle()
#        print neurite.getParent()
#        print neurite.getTitle()
        # foundNeurites.append([neurite.getParent().getTitle(), neurite.getTitle()])

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

            # save a line of node profile data
            # ['neuron', 'neurite', 'branch', 'layer', 'x', 'y', 'z', 'area', 'nInputs', 'nOutputs', 'connectors']
            nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), 0, nd.getLayer(), x, y, z, nd.getArea(), nInputs, nOutputs, inAndOuts]
            foundNeuriteNodes.append(nodeData)


outfile = open('tt.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeuriteNodes)
outfile.close()

