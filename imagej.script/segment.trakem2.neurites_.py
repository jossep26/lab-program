from ini.trakem2.display import Tag
from  java.awt.event import KeyEvent

def getInputs(nodeSet):
    nInputs = 0
    for nd in nodeSet:
        tags = nd.getTags()
        if tags is None:
            continue
        for tag in tags:
            if 'input_' in tag.toString():
                posN = tag.toString().find('_')
                nIn = int(tag.toString()[posN+1 :])
                nInputs += nIn
    return nInputs



def markTreeSegment(root):
    cutNodes = []
    for nd in root.getSubtreeNodes():
        tags = nd.getTags()
        if tags is None:
            continue
        for tag in tags:
            if 'output_' in tag.toString():
                cutNodes.append(nd)
                break
    cutNodes = set(cutNodes)
    branchNodes = set([nd for nd in root.getBranchNodes()])
    branchCutNodes = branchNodes.intersection(cutNodes)
    markings = {}
    segId = 0
    for nd in root.getSubtreeNodes():
        markings[nd] = set([segId])
    segId += 1
    for cnd in cutNodes:
        if cnd in branchNodes:
            markings[cnd].add(segId)
            for chnd in cnd.getChildrenNodes():
                segId += 1
                for nd in chnd.getSubtreeNodes():
                    markings[nd].add(segId)
        else:
            for nd in cnd.getSubtreeNodes():
                markings[nd].add(segId)
            segId += 1

    markings.update((k, frozenset(v)) for k, v in markings.iteritems())

    # substitute set of ids to unique single id
    segIdSets = frozenset([v for k, v in markings.iteritems()])
    setToIdTable = {}
    for i, segIdSet in enumerate(segIdSets):
        setToIdTable[segIdSet] = i
    markings2 = {}
    for nd, idSet in markings.iteritems():
        i = setToIdTable[idSet]
        markings2[nd] = set([i])
    for nd in cutNodes:
        if nd in branchNodes:
            for chnd in nd.getChildrenNodes():
                if chnd in cutNodes:
                    continue
                markings2[nd] = markings2[nd].union(markings2[chnd])
        pnd = nd.getParent()
        if pnd is None or pnd in cutNodes:
            continue
        pidSet = markings2[pnd]
        markings2[nd] = markings2[nd].union(pidSet)

        markingsRev = {}
        for nd, iSet in markings2.iteritems():
            for i in iSet:
                if i in markingsRev:
                    markingsRev[i] = markingsRev[i].union(set([nd]))
                else:
                    markingsRev[i] = set([nd])

        uniqueMarkingsRev = {}
        for i, nds in markingsRev.iteritems():
            if 1 == len(nds):
                continue
            uniqueMarkingsRev[i] = nds

    return uniqueMarkingsRev


project = Project.getProjects().get(2)
projectRoot = project.getRootProjectThing()

neurites = projectRoot.findChildrenOfTypeR("neurite")
for neurite in neurites:
    if 'apla_a' in neurite.getTitle():
        areatrees = neurite.findChildrenOfTypeR("areatree")
        for areatree in areatrees:
            root = areatree.getObject().getRoot()
            markings = markTreeSegment(root)

            print markings
            for i, nds in markings.iteritems():
                for nd in nds:
                    nd.addTag(Tag(str(i), KeyEvent.VK_K))

