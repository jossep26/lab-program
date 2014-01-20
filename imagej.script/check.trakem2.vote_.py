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

def removeAllTagsWithString(tagName, project):
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
                tags = nd.getTags()
                if tags is None:
                    continue
                for tag in tags:
                    if tagName in tag.toString():
                        nd.removeTag(tag)

# get file names
# op = OpenDialog("Choose original project", None)
# opn = op.getFileName()

# if op is None:
#     print "User canceled the dialog!"
# else:
#     opd = op.getDirectory()
#     opffn = os.path.join(opd, opn)

fn = r"g:\data\zby\EM.dualbeam\test\merge.vote\candidate.xml.gz"



basicProjectThingTypes = ["area_list", "areatree", "ball", "connector", "dissector", "pipe", "polyline", "profile", "profile_list", "treeline"]
voteTypes = ["areatree", "connector"]

# get the first project
project = Project.getProjects().get(0)

# tt = getObjectVsProject(project)
voteRe = re.compile(r"^VOTE-(yes|no)$")
yesVoteRe = re.compile(r"^VOTE-yes$")
revoteRe = re.compile(r"^REVOTE-")
candidateRe = re.compile(r"^E[CT]-")

print "remove existing REVOTE tags ..."
removeAllTagsWithString("REVOTE-", project)
print "done. Checking votes ..."

candidateTable = getVoteNodeTable(project)
candidateIdVsNode = getIdVsNode(project)

for ndId, tagNames in candidateTable.iteritems():
    nd = candidateIdVsNode[ndId]
    isCandidate = False
    votes = []
    for tagName in tagNames:
        if candidateRe.match(tagName):
            isCandidate = True
        if voteRe.match(tagName):
            votes.append(tagName)
    if isCandidate:
        if 1 != len(votes):
            # one and only one vote should exist
            print "found missing vote"
            nd.addTag(Tag("REVOTE-this", KeyEvent.VK_R))

print "done."