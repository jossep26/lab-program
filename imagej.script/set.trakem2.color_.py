from jarray import array
from java.awt import Rectangle
from java.awt.geom import Area
from java.awt.event import KeyEvent
from java.awt import Color
from ini.trakem2 import Project
from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Node, Treeline, Tag
import re

apcolor = Color(255,153,0)

project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if re.match(r"^.*aplap_", neurite.getTitle()) is None:
        continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None:
            break
        print neurite.getTitle(), ': ', areatree.getColor(), 'set to -->', apcolor
        areatree.setColor(apcolor)
        print 'alpha', areatree.getAlpha(), 'set to --> 0.6'
        areatree.setAlpha(0.6)
