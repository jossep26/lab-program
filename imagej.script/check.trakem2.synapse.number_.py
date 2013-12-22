project = Project.getProjects().get(0)
projectRoot = project.getRootProjectThing()

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

neurites = projectRoot.findChildrenOfTypeR("neurite")
nNeurites = 0
nManAllOuts = 0
nManAllIns = 0
nAutoAllOuts = 0
nAutoAllIns = 0
for neurite in neurites:
    if 'apla_' in neurite.getTitle():
        areatrees = neurite.findChildrenOfTypeR("areatree")
        for areatree in areatrees:
            nNeurites += 1

            # manually labeled
            nManOutputs = 0
            nManInputs = 0
            root = areatree.getObject().getRoot()
            if root is None:
                break
            for nd in root.getSubtreeNodes():
                tags = nd.getTags()
                if tags is None:
                    continue
                for tag in tags:
                    if 'output_' in tag.toString():
                        # print nd.getId(), 'out'
                        nManOutputs += 1
                    if 'input_' in tag.toString():
                        # print nd.getId(), 'in'
                        posN = tag.toString().find('_')
                        nIn = int(tag.toString()[posN+1 :])
                        nManInputs += nIn

            # auto recognized
            oiPt = getOutAndInPt(areatree)
            nAutoOutputs = len(oiPt[0])
            nAutoInputs = len(oiPt[1])
            print 'auto', nAutoOutputs, nAutoInputs
            print 'mann', nManOutputs, nManInputs
            # print neurite.getTitle(), nManOutputs, 'outs,', nManInputs, 'ins.'
            nManAllOuts += nManOutputs
            nManAllIns += nManInputs
            nAutoAllOuts += nAutoOutputs
            nAutoAllIns += nAutoInputs

synapses = projectRoot.findChildrenOfTypeR("synapse")
nNameAllOuts = 0
nNameAllIns = 0
for synapse in synapses:
    if 'out_apla_' in synapse.getTitle():
        nNameAllOuts += 1
    if 'in_apla_' in synapse.getTitle():
        nNameAllIns +=1

print 'summary-----\nneurites:', nNeurites
print 'manually:', 'all outs', nManAllOuts, ', all ins', nManAllIns
print 'names:', 'all outs', nNameAllOuts, ', all ins', nNameAllIns
print 'auto:', 'all outs', nAutoAllOuts, ', all ins', nAutoAllIns
