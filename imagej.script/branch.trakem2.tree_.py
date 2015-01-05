from ini.trakem2 import Project
from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Coordinate
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle
import csv
import re

THRESHOLD = 100

total_branches = 0
output = [['neurite', 'areatreeId', 'nodeId', 'size']]
project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")

for neurite in neurites:
    if re.match(r"^apla_", neurite.getTitle()) is None:
        continue
    this_branches = 0
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None:
            continue
        if root.getChildrenCount() > 2:
            branchNds = [nd for nd in root.getBranchNodes()]
        else:
            branchNds = [nd for nd in root.getBranchNodes() if nd is not root]
        for nd in branchNds:
            output.append([neurite.getTitle(), areatree.getId(), nd.getId(), len(nd.getSubtreeNodes())])
            if len(nd.getSubtreeNodes()) > THRESHOLD:
                this_branches += 1
    print 'Neurite', neurite.getTitle(), 'has', this_branches, 'branches.'
    total_branches += this_branches
print 'Total branches:', total_branches

outfile = open('branches.csv','wb')
writer = csv.writer(outfile)
writer.writerows(output)
outfile.close()
