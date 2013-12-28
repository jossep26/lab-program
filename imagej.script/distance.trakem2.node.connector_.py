# output a list of shortest distance between connectors labeled by hand

from ini.trakem2.display import AreaList, Display, AreaTree, Connector
from ini.trakem2.display.Tree import MeasurePathDistance
from fiji.geom import AreaCalculations
import csv
from jarray import array
from java.awt.geom import Area
from java.awt import Rectangle
import re

neuriteList_zjj = ['in_a_005', 'in_b_012', 'in_i_006', 'in_b_001', 'in_b_005', 'in_a_006', 'in_e_002', 'out_g_003', 'out_g_002', 'in_h_008', 'in_b_006']
neuriteList_wsx = ['in_h_009', 'out_d_001', 'in_b_006', 'out_b_002', 'in_h_010', 'in_j_001', 'in_c_003', 'in_h_011', 'in_h_005', 'in_a_003_out']
neuriteList = neuriteList_wsx + neuriteList_zjj

header = ['neuron', 'neurite', 'areatreeId', 'nodeId', 'synapseDirection', 'layer', 'x', 'y', 'z', 'area', 'distance']
foundNeuriteNodes = [header]

project = Project.getProjects().get(3)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if re.match(r"^apla_", neurite.getTitle()) is None:
        continue
    areatrees = neurite.findChildrenOfTypeR("areatree")
    for areatree in areatrees:
        areatree = areatree.getObject()
        root = areatree.getRoot()
        if root is None:
            break

#        branchId = 1
#        branchTable = {}
##        markTreeBranch(root)
#
        layerset = areatree.getLayerSet()
        calibration = layerset.getCalibration()
        affine = areatree.getAffineTransform()
        ndIn = []
        ndOut = []
        for nd in root.getSubtreeNodes():
            # manually labeled synapse
            tags = nd.getTags()
            if tags is None:
                continue
            for tag in tags:
                if 'output_' in tag.toString():
                    nOutputs = 1
                    ndOut.append(nd)
                if 'input_' in tag.toString():
                    posN = tag.toString().find('_')
                    nInputs = int(tag.toString()[posN+1 :])
                    ndIn.append(nd)
        ndIn = set(ndIn)
        ndOut = set(ndOut)

        if 0 == len(ndIn) or 0 == len(ndOut) :
            continue

        # calculate shortest distance for each input
        ndInDistance = {}
        for nd in ndIn:
            d = []
            for tnd in ndOut:
                d.append(MeasurePathDistance(areatree, nd, tnd).getDistance())
            ndInDistance[nd] = min(d)

        # calculate shortest distance for each out
        ndOutDistance = {}
        for nd in ndOut:
            d = []
            for tnd in ndIn:
                d.append(MeasurePathDistance(areatree, nd, tnd).getDistance())
            ndOutDistance[nd] = min(d)

        # input synapses
        for nd, d in ndInDistance.iteritems():
            # get node coordinates, from tut on web
            fp = array([nd.getX(), nd.getY()], 'f')
            affine.transform(fp, 0, fp, 0, 1)
            x = fp[0] * calibration.pixelWidth
            y = fp[1] * calibration.pixelHeight
            z = nd.getLayer().getZ() * calibration.pixelWidth  # a TrakEM2 oddity

            # get area
            ndArea = abs( AreaCalculations.area( nd.getData().getPathIterator(None) ) * calibration.pixelWidth * calibration.pixelHeight )

            ndLayerIndex = nd.getLayer().getParent().indexOf(nd.getLayer()) + 1
            # save a line of node profile data
            # ['neuron', 'neurite', 'areatreeId', 'nodeId', 'synapseDirection', 'layer', 'x', 'y', 'z', 'area', 'distance']
            nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'incoming', ndLayerIndex, x, y, z, ndArea, d]
            foundNeuriteNodes.append(nodeData)

        # output synapses
        for nd, d in ndOutDistance.iteritems():
            # get node coordinates, from tut on web
            fp = array([nd.getX(), nd.getY()], 'f')
            affine.transform(fp, 0, fp, 0, 1)
            x = fp[0] * calibration.pixelWidth
            y = fp[1] * calibration.pixelHeight
            z = nd.getLayer().getZ() * calibration.pixelWidth  # a TrakEM2 oddity

            # get area
            ndArea = abs( AreaCalculations.area( nd.getData().getPathIterator(None) ) * calibration.pixelWidth * calibration.pixelHeight )

            ndLayerIndex = nd.getLayer().getParent().indexOf(nd.getLayer()) + 1
            # save a line of node profile data
            # ['neuron', 'neurite', 'areatreeId', 'nodeId', 'synapseDirection', 'layer', 'x', 'y', 'z', 'area', 'distance']
            nodeData = [neurite.getParent().getTitle(), neurite.getTitle(), areatree.getId(), nd.getId(), 'outgoing', ndLayerIndex, x, y, z, ndArea, d]
            foundNeuriteNodes.append(nodeData)

outfile = open('synapse-distances-zby.csv','wb')
writer = csv.writer(outfile)
writer.writerows(foundNeuriteNodes)
outfile.close()
            