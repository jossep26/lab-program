from ini.trakem2.display import AreaList, Display, AreaTree, Connector
from ini.trakem2.tree import ProjectThing

areatreeId = "22436"

def getOutAndInPt(areatreePt):
    if not isinstance(areatreePt, ProjectThing):
        return None
    projectRoot = areatreePt.getRootParent()
    areatree = areatreePt.getObject()
    outAndIn = areatree.findConnectors()
    outPt = []
    inPt = []
    for connectorPt in projectRoot.findChildrenOfTypeR("connector"):
        connector = connectorPt.getObject()
        if connector in outAndIn[0] :
            outPt.append(connectorPt)
        elif connector in outAndIn[1] :
            inPt.append(connectorPt)
    return [outPt, inPt]


# get the first open project
project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()
nNeurites = 0
nOuts = 0
nIns = 0
neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if 'apla_' in neurite.getTitle():
        areatrees = neurite.findChildrenOfTypeR("areatree")
        for areatree in areatrees:
            nNeurites += 1
            Display3D.show(areatree, 1, 8)
            oiPt = getOutAndInPt(areatree)
            nOuts += len(oiPt[0])
            nIns += len(oiPt[1])
            oiPt = [x for y in oiPt for x in y]
            print oiPt
            if oiPt is None:
                continue
            for c in oiPt:
                Display3D.show(c, 1, 8)
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