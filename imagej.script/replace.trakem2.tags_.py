# replace tags of one type to another in currently active TrakEM2 project
# tag used for replacement must exist

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
import csv
import itertools

def getTheTag(tagString):
    areatrees = Display.getFront().getLayerSet().getZDisplayables(AreaTree)
    connectors = Display.getFront().getLayerSet().getZDisplayables(Connector)
    tpTag = None
    for tree in itertools.chain(areatrees, connectors):
        root = tree.getRoot()
        if root is None:
            break
        for node in root.getSubtreeNodes():
            tags = node.getTags()
            if tags is None:
                continue
            for tag in tags:
                if tagString in tag.toString():
                    return tag

areatrees = Display.getFront().getLayerSet().getZDisplayables(AreaTree)
connectors = Display.getFront().getLayerSet().getZDisplayables(Connector)
tpTag = getTheTag('TODO-proofread')
if tpTag is None:
    print "tag not found"
    raise Exception("tag not found")
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
            if 'ET-new' in tag.toString():
                print "replacing tag", tag, "for node", node.getId()
                node.removeTag(tag)
                node.addTag(tpTag)
