# For output a list of neurons in currently active TrakEM2 project
#   with the same sequence as seen in project tab
# Change output filename at the bottom
# 
# author Bangyu Zhou, 2013 Dec 10

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
import csv
from jarray import array

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

header = ['neurite', 'neuron', 'areatreeIds', 'nNodes', 'length']
foundNeurons = [header]

# get the first open project, project root, and 'drosophila_brain'
project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()
brain = projectRoot.findChildrenOfType("drosophila_brain")[0]

neurons = brain.findChildrenOfType("neuron")
for neuron in neurons:
    neurites = neuron.findChildrenOfType("neurite")
    for neurite in neurites:
        areatrees = neurite.findChildrenOfType("areatree")
        nNodes = 0
        areatreeIds = []
        length = 0
        for areatree in areatrees:
            areatree = areatree.getObject()
            areatreeIds.append(areatree.getId())
            dt = getTreeDistanceTable(areatree)
            length += sum([d for nd, d in dt.iteritems()])
            root = areatree.getRoot()
            if root is None:
                continue
            nNodes += len(root.getSubtreeNodes())
        foundNeurons.append([neurite.getTitle(), neuron.getTitle(), areatreeIds, nNodes, length])

outfile = open('neurons.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeurons)
outfile.close()
