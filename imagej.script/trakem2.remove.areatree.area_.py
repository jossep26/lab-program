# clear area of areatrees

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle
import re

project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    # if re.match(r"^apla_", neurite.getTitle()) is None:
    #     continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None:
            continue
        for nd in root.getSubtreeNodes():
            nd.setData(None)
         