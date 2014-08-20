from ini.trakem2 import Project
from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Coordinate
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle
import re

project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()

display = Display.getFront(project)

neurites = projectRoot.findChildrenOfTypeR("neurite")
notDrawnCo = []
notDrawn = [['layer', 'neurite', 'node']]

for neurite in neurites:
    if re.match(r"^apl", neurite.getTitle()) is None:
        continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None:
            continue

        nEmpty = 0
        nNodes = 0
        layerset = areatree.getLayerSet()
        calibration = layerset.getCalibration()
        affine = areatree.getAffineTransform()
        for nd in root.getSubtreeNodes():
            nNodes += 1
            ndArea = abs( AreaCalculations.area(nd.getData().getPathIterator(None)) )
            if ndArea < 1:
                nEmpty += 1
                fp = array([nd.getX(), nd.getY()], 'f')
                affine.transform(fp, 0, fp, 0, 1)
                x = fp[0]
                y = fp[1]
                notDrawnCo.append(Coordinate(x, y, nd.getLayer(), nd))
                notDrawn.append([nd.getLayer().getParent().indexOf(nd.getLayer()) + 1, neurite.getTitle(), nd.getId()])
        if nEmpty:
            print neurite.getTitle(), 'has ', nEmpty, '/', nNodes, 'nodes not drawn (area too small).'

outfile = open('notDrawn.csv','wb')
writer = csv.writer(outfile)
writer.writerows(notDrawn)
outfile.close()

display.centerAt(notDrawnCo[0])