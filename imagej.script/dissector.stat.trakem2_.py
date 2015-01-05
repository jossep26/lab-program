from ini.trakem2.display import Dissector
from ini.trakem2 import Project
import csv

# TODO: add arealist overlap

output = [['dissector_id', 'radius_pix', 'radius_um', 'intensity']]

project = Project.getProjects().get(0)
autoDissector = project.findById("autoDissector")
items = autoDissector.getAllItems()
layerset = autoDissector.getLayerSet()
calibration = layerset.getCalibration()

for item in items:
    itemPoint = item.getPoint()
    output.append(['', item.getRadius(), item.getRadius()*calibration.pixelWidth, item.getIntensity()])

outfile = open('dissector_stat.csv','wb')
writer = csv.writer(outfile)
writer.writerows(output)
outfile.close()
