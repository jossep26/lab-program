# For output a list of neurons in currently active TrakEM2 project
#   with the same sequence as seen in project tab
# Change output filename at the bottom
# 
# author Bangyu Zhou, 2013 Dec 10

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
import csv

header = ['neurite', 'neuron', 'areatreeIds', 'nNodes']
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
        for areatree in areatrees:
            areatree = areatree.getObject()
            areatreeIds.append(areatree.getId())
            root = areatree.getRoot()
            if root is None:
                continue
            nNodes += len(root.getSubtreeNodes())
        foundNeurons.append([neurite.getTitle(), neuron.getTitle(), areatreeIds, nNodes])

outfile = open('neurons.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeurons)
outfile.close()
