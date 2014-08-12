from jarray import array
from java.awt import Rectangle
from java.awt.geom import Area
from java.awt.event import KeyEvent
from ini.trakem2 import Project
from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Node, Treeline, Tag
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
import re
import csv

project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()
output = [['lobe', 'Z','area']]

arealists = projectRoot.findChildrenOfTypeR("area_list")
for arealist in arealists:
    if re.match(r".*lobe", arealist.getTitle()) is None:
        continue
    arealist = arealist.getObject()
    layerset = arealist.getLayerSet()
    calibration = layerset.getCalibration()
    layers = arealist.getLayerRange()
    for layer in layers:
        area = arealist.getArea(layer)
        if area is None:
            A = 0
        else:
            A = abs( AreaCalculations.area(area.getPathIterator(None) ) * calibration.pixelWidth * calibration.pixelHeight )
        
        output.append([arealist.getTitle(), layer.getZ()*calibration.pixelWidth, A])

print 'writing ...'
outfile = open('area.lobes.csv','wb')
writer = csv.writer(outfile)
writer.writerows(output)
outfile.close()
print 'done.'
