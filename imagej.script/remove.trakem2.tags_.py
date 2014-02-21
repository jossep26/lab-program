# For removing certain tags in currently active TrakEM2 project

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
import csv
import itertools

import re

def onlyDigits(s):
    od = re.compile('^\d+$')
    return bool(od.search(s))
    
def startWithDigits(s):
    od = re.compile('^\d+')
    return bool(od.search(s))
    
areatrees = Display.getFront().getLayerSet().getZDisplayables(AreaTree)
connectors = Display.getFront().getLayerSet().getZDisplayables(Connector)

for tree in itertools.chain(areatrees, connectors):
#    print "processing", type(tree), ":", tree.getId()
    root = tree.getRoot()
    if root is None:
        continue
    for node in root.getSubtreeNodes():
        tags = node.getTags()
        if tags is None:
            continue
        for tag in tags:
            if re.match(r"^voted-3/4$", tag.toString()):
                print "removing tag", tag, "for node:", node.getId()
                node.removeTag(tag)
