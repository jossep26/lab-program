from ini.trakem2.display import AreaList, Display, AreaTree, Connector, Tree, Tag
from jarray import array
from java.awt.geom import Area
from java.awt.event import KeyEvent
from java.awt import Rectangle
import re
import os
import csv


def getObjectVsProject(project):
# return a object vs project dict
    table = {}
    basicProjectThingTypes = ["area_list", "areatree", "ball", "connector", "dissector", "pipe", "polyline", "profile", "profile_list", "treeline"]
    for projectThingString in basicProjectThingTypes:
        for pt in project.getRootProjectThing().findChildrenOfTypeR(projectThingString):
            if pt.getObject() in table:
                print 'Wrong in get dict for object vs project: should be one to one relationship.'
                return None
            table[pt.getObject()] = pt
    return table

def getIdVsNode(project):
    table = {}
    treeTypes = ["areatree", "connector", "treeline"]
    for treeType in treeTypes:
        for tpt in project.getRootProjectThing().findChildrenOfTypeR(treeType):
            treeObject = tpt.getObject()
            if not isinstance(treeObject, Tree):
                continue
            root = treeObject.getRoot()
            if root is None:
                continue
            for nd in root.getSubtreeNodes():
                table[nd.getId()] = nd
    return table

def getVoteNodeTable(project):
    # return a table of tree node ids vs candidate and/or vote tag names
    table = {}
    voteProjectThingTypes = ["areatree", "connector", "treeline"]    # these are trees
    candidateRe = re.compile(r"^E[CT]-")
    voteRe = re.compile(r"^VOTE-(yes|no)$")
    for voteType in voteProjectThingTypes:
        for vpt in project.getRootProjectThing().findChildrenOfTypeR(voteType):
            voteObject = vpt.getObject()
            if isinstance(voteObject, Tree):
                root = voteObject.getRoot()
                if root is None:
                    continue
                for nd in root.getSubtreeNodes():
                    tags = nd.getTags()
                    if tags is None:
                        continue
                    relevantTags = []
                    for tag in tags:
                        tagName = tag.toString()
                        if candidateRe.match(tagName) or voteRe.match(tagName):
                            relevantTags.append(tagName)
                    if not relevantTags:
                        continue
                    table[nd.getId()] = relevantTags
    return table

def getVoter(project):
    find = re.compile(r"^[^.]*")
    return re.search(find, project.getTitle()).group(0)

# get file names
# op = OpenDialog("Choose original project", None)
# opn = op.getFileName()

# if op is None:
#     print "User canceled the dialog!"
# else:
#     opd = op.getDirectory()
#     opffn = os.path.join(opd, opn)

opffn = r"g:\data\zby\EM.dualbeam\test\merge.vote\candidate.xml.gz"
vpffns = (r"g:\data\zby\EM.dualbeam\test\merge.vote\voter1.votes.xml.gz",
          r"g:\data\zby\EM.dualbeam\test\merge.vote\voter2.votes.xml.gz",
        )

outfn = r"g:\data\zby\EM.dualbeam\test\merge.vote\merged.xml.gz"

basicProjectThingTypes = ["area_list", "areatree", "ball", "connector", "dissector", "pipe", "polyline", "profile", "profile_list", "treeline"]
voteTypes = ["areatree", "connector"]

# Load the projects
originProject = Project.openFSProject(opffn, False) # don't open display
voteProjects = []
for vpffn in vpffns:
    voteProjects.append(Project.openFSProject(vpffn, False))

# tt = getObjectVsProject(originProject)
voteRe = re.compile(r"^VOTE-(yes|no)$")
yesVoteRe = re.compile(r"^VOTE-yes$")

candidateTable = getVoteNodeTable(originProject)
candidateIdVsNode = getIdVsNode(originProject)
sumTable = dict.fromkeys(candidateTable.keys(), [0, 0])
for voteProject in voteProjects:
    print "processing project", voteProject.getTitle()
    voter = getVoter(voteProject)
    voteTable = getVoteNodeTable(voteProject)
    for ndId, candidateTags in candidateTable.iteritems():
        nd = candidateIdVsNode[ndId]
        nYesVotes = sumTable[ndId][0]
        nAllVotes = sumTable[ndId][1]
        if ndId in voteTable:
            voteTagNames = voteTable[ndId]
            voteTags = [tagName for tagName in voteTagNames if voteRe.match(tagName)]
            if 1 == len(voteTags):
                # valid votes
                nAllVotes = nAllVotes + 1
                if yesVoteRe.match(voteTags[0]):
                    nYesVotes = nYesVotes + 1
            else:
                # vote not found
                print "missing vote at node", ndId
                nd.addTag(Tag("REVOTE-"+voter, KeyEvent.VK_R))
        else:
            # vote not found
            print "missing vote at node", ndId
            nd.addTag(Tag("REVOTE-"+voter, KeyEvent.VK_R))
        sumTable[ndId] = [nYesVotes, nAllVotes]
        voteProject.getLoader().setChanged(False) # avoid dialog at closing
        voteProject.destroy()

for ndId, votes in sumTable.iteritems():
    nd = candidateIdVsNode[ndId]
    nYesVotes = sumTable[ndId][0]
    nAllVotes = sumTable[ndId][1]
    votedString = 'voted-' + str(nYesVotes) + '/' + str(nAllVotes)
    nd.addTag(Tag(votedString, KeyEvent.VK_M))

originProject.setTitle(os.path.basename(outfn))
originProject.getLoader().setChanged(False) # avoid dialog at closing
originProject.saveAs(outfn)
