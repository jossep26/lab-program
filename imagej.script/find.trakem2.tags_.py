# For output a list of tagged nodes in currently active TrakEM2 project
# Change output filename at the bottom

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
import csv

header = ['type', 'parentId', 'parentName', 'shortMeaningfulTitle', 'node', 'tag']
foundtags = [header]

areatrees = Display.getFront().getLayerSet().getZDisplayables(AreaTree)
for areatree in areatrees: 
    
    root = areatree.getRoot()
    if root is None:
        break

    for node in root.getSubtreeNodes():
        tags = node.getTags()
        if tags is None:
            continue
        for tag in tags:
            foundtags.append( ['areatrea', areatree.getId(), areatree.getTitle(), areatree.getProject().getShortMeaningfulTitle(areatree), str(node), str(tag)] )

connectors = Display.getFront().getLayerSet().getZDisplayables(Connector)
for connector in connectors:
    root = connector.getRoot()
    if root is None:
        break
    for node in root.getSubtreeNodes():
        tags = node.getTags()
        if tags is None:
            continue
        for tag in tags:
            foundtags.append( ['connector', connector.getId(), connector.getTitle(), connector.getProject().getShortMeaningfulTitle(connector), str(node), str(tag)] )

outfile = open('test.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundtags)
outfile.close()
