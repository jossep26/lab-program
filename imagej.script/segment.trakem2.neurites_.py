from ini.trakem2.display import Tag
from  java.awt.event import KeyEvent


def markTreeSegment(node):
    global segmentId
    global segmentList

    segmentId = 0
    segmentList = []

    print 'node', node.getId(), 'segment', segmentId
    node.addTag(Tag(str(segmentId), KeyEvent.VK_K))
    segmentList.append([node, segmentId])

    canBeCut = 0
    tags = node.getTags()
    if tags is not None:
        for tag in tags:
            if 'output_' in tag.toString():
                canBeCut = 1
                break
    if canBeCut:
        segmentId += 1
        print 'node', node.getId(), 'segment', segmentId
        node.addTag(Tag(str(segmentId), KeyEvent.VK_K))
        segmentList.append([node, segmentId])

    # go to next node
    count = node.getChildrenCount()
    if 0 == count:
        print 'this node is end'
        return
    elif 1 == count:
        nextNode = node.getChildrenNodes()[0]
        # print 'next', nextNode.getId()
        markTreeSegment(nextNode)
    else:
        print 'this is branch'
        for nextNode in node.getChildrenNodes():
            segmentId += 1
            print 'node', node.getId(), 'segment', segmentId
            node.addTag(Tag(str(segmentId), KeyEvent.VK_K))
            segmentList.append([node, segmentId])
            markTreeSegment(nextNode)


def markTreeSegmentClean(node):
    global segmentId
    global segmentList

    segmentId = 0
    segmentList = []
    markTreeSegment(node)
    cpList = segmentList

    keyNodes = []
    for bnd in node.getBranchNodes(node):
        tags = bnd.getTags()
        if tags is None:
            keyNodes.append(bnd)
            continue
        for tag in tags:
            if 'output_' not in tag.toString():
                keyNodes.append(bnd)

    markings = dict()
    for nd, sid in cpList:
        if nd in markings:
            markings[nd].append(sid)
        else:
            markings[nd] = [sid]

    return cpList

def markTreeSegment2(root):
    cutNodes = [root]
    branchNodes = set([nd for nd in root.getBranchNodes()])
    isRootCut = bool(0)
    for nd in root.getSubtreeNodes():
        tags = nd.getTags()
        if tags is None:
            continue
        for tag in tags:
            if 'output_' in tag.toString():
                if root.getId() == nd.getId():
                    isRootCut = bool(1)
                else:
                    cutNodes.append(nd)
                break
    cutNodes = set(cutNodes)
    branchCutNodes = branchNodes.intersection(cutNodes)
    markings = {}
    segId = 0

    for cnd in cutNodes:
        if cnd in branchNodes:
            if cnd in markings:
                markings[cnd].add(segId)
            else:
                markings[cnd] = set([segId])
            for chnd in cnd.getChildrenNodes():
                segId += 1
                for nd in chnd.getSubtreeNodes():
                    if nd in markings:
                        markings[nd].add(segId)
                    else:
                        markings[nd] = set([segId])
        else:
            for nd in cnd.getSubtreeNodes():
                if nd in markings:
                    markings[nd].add(segId)
                else:
                    markings[nd] = set([segId])
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
            markings = markTreeSegment2(root)

            print markings
            for i, nds in markings.iteritems():
                for nd in nds:
                    nd.addTag(Tag(str(i), KeyEvent.VK_K))

