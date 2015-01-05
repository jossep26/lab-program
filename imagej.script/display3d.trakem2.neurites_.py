from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Display3D
from ini.trakem2.tree import ProjectThing
import re

## tools
def getOutAndInPt(areatreePt, connectorTable):
    if not isinstance(areatreePt, ProjectThing):
        return None
    projectRoot = areatreePt.getRootParent()
    areatree = areatreePt.getObject()
    # NOTE: buggy function? may transform area for nodes
    outAndIn = findConnectorsInTree(areatree)
    outPt = []
    inPt = []
    for direction, ndVsC in outAndIn.iteritems():
        for nd, connectors in ndVsC.iteritems():
            for connector in connectors:
                if direction == 'outgoing':
                    outPt.append(connectorTable[connector])
                elif direction == 'incoming':
                    inPt.append(connectorTable[connector])
    # for connectorPt in projectRoot.findChildrenOfTypeR("connector"):
    #     connector = connectorPt.getObject()
    #     if connector in outAndIn['outgoing'] :
    #         outPt.append(connectorPt)
    #     elif connector in outAndIn['incoming'] :
    #         inPt.append(connectorPt)
    return [outPt, inPt]

def isTree(x):
    if isinstance(x, Connector):
        return False
    return isinstance(x, Treeline) or isinstance(x, AreaTree)

def findConnectorsInTree(tree):
    # returns a dict of two values, each contains a dict of node versus connectors
    if not isTree(tree):
        print "error: input is neither Treeline or AreaTree"
        return
    outgoing = {}
    incoming = {}
    las = tree.getLayerSet()
    cal = las.getCalibration()
    at = tree.getAffineTransform()
    root = tree.getRoot()
    if root is None:
        return
    for nd in root.getSubtreeNodes():
        # copied from TrakEM2_Scripting and Tree.java
        la = nd.getLayer()
        area = nd.getArea().clone()
        area.transform(at)
        cs = las.findZDisplayables(Connector, la, area, False, False)
        if cs.isEmpty():
            continue
        for connector in cs:
            # print 'found', connector
            if connector.intersectsOrigin(area, la):
                if nd in outgoing:
                    outgoing[nd].append(connector)
                else:
                    outgoing[nd] = [connector]
            else:
                if nd in incoming:
                    incoming[nd].append(connector)
                else:
                    incoming[nd] = [connector]
    return {'outgoing':outgoing, 'incoming':incoming}

def fixAreatreeArea(areatree):
    # Append a 1-pixel square area for nodes without any area
    # this will fix using findZDisplayables for finding areatree, 
    #     including connector.getTargets(), connector.getOrigins() etc.
    if not isinstance(areatree, AreaTree):
        print "Error: input must be an AreaTree"
        return
    root = areatree.getRoot()
    if root is None:
        return
    for nd in root.getSubtreeNodes():
        a = nd.getArea()
        a.add(Area(Rectangle(int(nd.getX()), int(nd.getY()), 1, 1)))
        nd.setData(a)

def getConnectorTable(project):
    # return a dict of connector vs. project thing
    t = {}
    projectRoot = project.getRootProjectThing()
    connectors = projectRoot.findChildrenOfTypeR("connector")
    for connector in connectors:
        t[connector.getObject()] = connector
    return t

# get the first open project
project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()
ct = getConnectorTable(project)
nNeurites = 0
nOuts = 0
nIns = 0
neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if re.match(r"^(apla_|in_|out_)", neurite.getTitle()):
        areatrees = neurite.findChildrenOfTypeR("areatree")
        for areatree in areatrees:
            nNeurites += 1
            oiPt = getOutAndInPt(areatree, ct)
            nOuts += len(oiPt[0])
            nIns += len(oiPt[1])
            oiPt = [x for y in oiPt for x in y]
            # print oiPt
            if oiPt is None:
                continue
            for c in oiPt:
                Display3D.show(c, False, 4)
            Display3D.show(areatree, False, 4)
            # for iPt in oiPt[0]:
            #     Display3D.show(iPt, 1, 8)
    # if 'in_' in neurite.getTitle():
    #     connectors = neurite.findChildrenOfTypeR("connector")
    #     for connector in connectors:
    #         Display3D.show(connector, 1, 8)

print 'done.'
print nNeurites, 'neurites,', nOuts, 'outputs,', nIns, 'inputs'
# ps = Display.getFront().getLayerSet().getLayer(800).getAll(Patch)
# for p in ps:
    # print type(p), p
#    Display3D.show(p)