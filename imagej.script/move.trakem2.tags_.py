# move tags from connector root to target

from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Tag
from java.awt.event import KeyEvent
import csv
import itertools

def containsTag(node, string):
    tags = node.getTags()
    if tags is None:
        return False
    for tag in tags:
        if string in tag.toString():
            return True
    return False

def unsetTagWithString(node, string):
    tags = node.getTags()
    if tags is None:
        return
    for tag in tags:
        if string in tag.toString():
            node.removeTag(tag)

theTag = Tag('EC-link', KeyEvent.VK_C)

connectors = Display.getFront().getLayerSet().getZDisplayables(Connector)
for connector in connectors:
    root = connector.getRoot()
    if root is None:
        continue
    if not containsTag(root, 'EC-link'):
        continue
    # wrong tag position, move to child node
    for childnode in root.getChildrenNodes():
        if not containsTag(childnode, 'EC-link'):
            childnode.addTag(theTag)
            print 'set new tag on', connector.getId()
    unsetTagWithString(root, 'EC-link')
