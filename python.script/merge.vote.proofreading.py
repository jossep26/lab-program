# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 14:01:19 2013

@author: shenlj, byzhou
"""

mainFile = r'merger2.20131210.p.merge.xml'

subFiles = (
            r'voter1.20131211.vote.xml',  
            r'voter2.20131211.vote.xml',  
            r'voter3.20131211.vote.xml',  
            )

outFile = r'vmerger.20131212.v.merge3.xml'


# tool functions
from xml.etree.ElementTree import SubElement
import xml.etree.ElementTree as ET
import os
import gzip
import re
# import itertools
import sys
sys.setrecursionlimit(1000000) 

def getVoter(votingFile) :
    fn = os.path.basename(votingFile)
    find = re.compile(r"^[^.]*")
    return re.search(find, fn).group(0)

def parseProjectFileRoot(filename):
    if filename.endswith(".xml.gz"):
        f = gzip.open(filename, "rb")
    elif filename.endswith(".xml", "rb"):
        f = open(filename)
    else:
        return None
    root = ET.parse(f).getroot()
    f.close()
    if root.tag != 'trakem2' : 
        print filename, ' has invalid trakem2 format!'
        return None
    return root

def getProjectHeaderString(filename):
    headerStr = ''
    if filename.endswith(".xml.gz"):
        f = gzip.open(filename, "rb")
    elif filename.endswith(".xml"):
        f = open(filename, "rb")
    else:
        return None
    for newLine in f : 
        if newLine == '<trakem2>\n' : 
            break
        headerStr += newLine
    f.close()
    return headerStr

def writeProject(filename, headerStr, treeRoot):
    treeStr = ET.tostring(treeRoot, 'ISO-8859-1')
    if filename.endswith(".xml.gz"):
        f = gzip.open(filename, "wb")
    elif filename.endswith(".xml"):
        f = open(filename, "wb")
    else:
        return False
    f.write(headerStr)
    f.write(treeStr[treeStr.index('\n') + 1 : ])
    f.close()
    return True   

def getObjId(objX) : 
    objId = objX.get('noid')
    if not objId : 
        objId = objX.get('oid')
        if not objId : 
            objId = objX.get('id')
    return objId

def objectMerger(objA, objB) : 
    objList = ['t2_node', 't2_areatree', 't2_connector', 't2_layer_set']
    skipList = ['t2_area', 't2_path', 't2_display']
    for subObjB in objB : 
        if subObjB.tag in skipList :
            continue
        for subObjA in objA : 
            if subObjA.tag == subObjB.tag and getObjId(subObjA) == getObjId(subObjB) : 
                if subObjA.tag == 't2_node' : 
                    t2_tagsB = subObjB.findall('t2_tag')
                    t2_tagsA = subObjA.findall('t2_tag')
                    tagsA_List = [x.get('name') for x in t2_tagsA]
                    subObjA.extend([x for x in t2_tagsB if not isVoteTag(x) and x.get('name') not in tagsA_List])
                objectMerger(subObjA, subObjB)
                break
        else : 
            objA.append(subObjB)

def isCandidateTag(nodeTag):
    if nodeTag.tag != "t2_tag":
        return False
    tagName = nodeTag.get('name')
    return bool(re.match(r"^E[CT]-", tagName))

def isVoteTag(nodeTag):
    if nodeTag.tag != "t2_tag":
        return False
    tagName = nodeTag.get('name')
    voteRe = re.compile(r"^VOTE-(yes|no)$")
    return bool(voteRe.match(tagName))

def isYesVoteTag(nodeTag):
    if nodeTag.tag != "t2_tag":
        return False
    tagName = nodeTag.get('name')
    yesVoteRe = re.compile(r"^VOTE-yes$")
    return bool(yesVoteRe.match(tagName))

def getNodeIdVsVote(projectRoot):
    # return a dict of t2_node object vs. relevant tag names for voting
    table = {}
    treeTypes = ["t2_areatree", "t2_connector", "t2_treeline"]
    for treeType in treeTypes:
        for obj in projectRoot.iter(treeType):
            for node in obj.iter("t2_node"):
                tag = [x for x in node.findall("t2_tag") if isVoteTag(x) or isCandidateTag(x)]
                if tag:
                    table[getObjId(node)] = tag
    return table

def getNodeIdVsNode(projectRoot):
    # return a dict of t2_node id vs. object
    table = {}
    treeTypes = ["t2_areatree", "t2_connector", "t2_treeline"]
    for treeType in treeTypes:
        for obj in projectRoot.iter(treeType):
            for node in obj.iter("t2_node"):
                table[getObjId(node)] = node
    return table

def addTagToNode(node, tagString, keyString):
    if node.tag != "t2_node":
        print "Error adding Tag to node, invalid node."
        return False
    if not isinstance(tagString, basestring) :
        print "Error adding Tag to node, invalid tag for", getObjId(node)
        return False
    if re.match(r"^([A-Z]|[0-9])$", keyString) is None:
        print "Error adding Tag to node, invalid key for", getObjId(node)
        return False
    SubElement(node, "t2_tag", {"name":tagString, "key":keyString})
    return True

# tool funcions end

## parsing projects
print "Parsing main file", os.path.basename(mainFile)
mainRoot = parseProjectFileRoot(mainFile)
if mainRoot is None : 
    print mainFile, ' has invalid trakem2 format!'
    raise Exception("Main File invalid!")
else:
    headerStr = getProjectHeaderString(mainFile)

project = mainRoot.find('project')
project.set('title', os.path.basename(outFile))

subRoots = {}
for f in subFiles:
    print "Parsing sub file", os.path.basename(f)
    r = parseProjectFileRoot(f)
    if r is None:
        print f, ' has invalid trakem2 format! skiped.'
        continue
    subRoots[f] = r

## merge voting results:
print "Merging votes ..."
candidateTable = getNodeIdVsVote(mainRoot)
candidateNodeTable = getNodeIdVsNode(mainRoot)
sumVoteTable = dict.fromkeys(candidateTable.keys(), [0, 0]) 
for subFile, subRoot in subRoots.iteritems():
    # check the sub files against main file
    print "processing votes in", subFile
    voter = getVoter(subFile)
    voteTable = getNodeIdVsVote(subRoot)
    for nodeId, candidateTagNames in candidateTable.iteritems():
        node = candidateTable[nodeId]
        nYesVotes = sumVoteTable[nodeId][0]
        nAllVotes = sumVoteTable[nodeId][1]
        if nodeId in voteTable:
            voteTags = [x for x in voteTable[nodeId] if isVoteTag(x)]
            if 1 == len(voteTags):
                # valid vote
                nAllVotes = nAllVotes + 1
                if isYesVoteTag(voteTags[0]):
                    nYesVotes = nYesVotes + 1
            else:
                # vote not found
                print "missing vote at node", nodeId
                addTagToNode(node, "REVOTE-"+voter, "R")
        else:
            # no corresponding node in voting project
            print "node missing", nodeId
            addTagToNode(node, "REVOTE-"+voter, "R")
        sumVoteTable[nodeId] = [nYesVotes, nAllVotes]

print "Votes merged, adding voted tags ..."
for nodeId, votes in sumVoteTable.iteritems():
    node = candidateNodeTable[nodeId]
    nYesVotes = votes[0]
    nAllVotes = votes[1]
    votedString = 'voted-' + str(nYesVotes) + '/' + str(nAllVotes)
    addTagToNode(node, votedString, "M")

## merging newly proofread objects
print "Merging newly proofread objects ..."
for subFile, subRoot in subRoots.iteritems():
    print "processing new objects in", subFile
    objectMerger(mainRoot, subRoot)

## writing file
print "writing to file", outFile
writeProject(outFile, headerStr, mainRoot)
