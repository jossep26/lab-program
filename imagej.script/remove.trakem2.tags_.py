# For removing certain tags in currently active TrakEM2 project

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
import csv
import itertools

areatrees = Display.getFront().getLayerSet().getZDisplayables(AreaTree)
connectors = Display.getFront().getLayerSet().getZDisplayables(Connector)

for tree in itertools.chain(areatrees, connectors):
    print "processing", type(tree), ":", tree.getId()
    root = tree.getRoot()
    if root is None:
        break
    for node in root.getSubtreeNodes():
        tags = node.getTags()
        if tags is None:
            continue
        for tag in tags:
            if 'voted-' in tag.toString():
                print "removing tag", tag, "for node:", node.getId()
                node.removeTag(tag)
