# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 14:01:19 2013

@author: shenlj, byzhou
"""

mainFile = r'merger2.20131210.p.merge.xml'

votingFiles = (
            r'voter1.20131211.vote.xml',  
            r'voter2.20131211.vote.xml',  
            r'voter3.20131211.vote.xml',  
            )

outFile = r'vmerger.20131212.v.merge3.xml'


# tool functions
from xml.etree.ElementTree import SubElement
import os
import re
import itertools

objList = ['t2_node', 't2_areatree', 't2_connector', 't2_layer_set']

def getVoter(votingFile) :
    fn = os.path.basename(votingFile)
    find = re.compile(r"^[^.]*")
    return re.search(find, fn).group(0)

def getObjId(objX) : 
    objId = objX.get('noid')
    if not objId : 
        objId = objX.get('oid')
        if not objId : 
            objId = objX.get('id')
    return objId

def voteStatistician(rootA, rootB, voter, tagError = 1) : 
    if not isinstance(voter, basestring) :
        print "wrong voter."
        return

    # iterate areatree and connector
    for objA in itertools.chain(rootA.iter('t2_areatree'), rootA.iter('t2_connector')):
        # prepare corresponding element in B
        for objB in itertools.chain(rootB.iter('t2_areatree'), rootB.iter('t2_connector')):
            if getObjId(objB) == getObjId(objA):
                matchedObjB = objB
                break
        if matchedObjB is None:
            # error, certainly, and skip to next areatree or connector
            print "error: cannot find corresponding element for", getObjId(objA)
            continue

        # iterate node
        for nodeA in objA.iter('t2_node'):
            # determine whether this node is a candidate
            candidate = [x.get('name') for x in nodeA.findall('t2_tag') if 'ET-' in x.get('name') or 'EC-' in x.get('name')]
            nCandidates = len(candidate)
            if nCandidates <= 0:
                # examine next node A
                continue
            elif nCandidates > 1:
                # error, and examine next node A
                print "error: multiple candidate tags on one node."
                if tagError:
                    e = SubElement(nodeA, 't2_tag', {'name' : "ERROR-multiple-tag", 'key' : "E"})
                continue

            # the nodeA is a candidate
            # get pre-existing vote results
            votedTagA = [x for x in nodeA.findall('t2_tag') if 'voted-' in x.get('name')]
            if len(votedTagA) > 1 :
                # error, and skip this node
                print "get voted tag error."
                if tagError:
                    e = SubElement(nodeA, 't2_tag', {'name' : "ERROR-votetag-" + voter, 'key' : "E"})
                continue
            elif len(votedTagA) <= 0 :
                # create new
                votedTagA = SubElement(nodeA, 't2_tag', {'name' : "voted-0/0", 'key' : "M"})
                allVote = 0
                voteYes = 0;
            else :
                votedTagA = votedTagA[0]
                posLine = votedTagA.get('name').find('-')
                posBias = votedTagA.get('name').find('/')
                voteYes = int(votedTagA.get('name')[posLine + 1 : posBias])
                allVote = int(votedTagA.get('name')[posBias + 1 :])

            # get corrisponding node in B
            matchedNodeB = None
            for nodeB in matchedObjB.iter('t2_node'):
                if getObjId(nodeB) == getObjId(nodeA):
                    matchedNodeB = nodeB
                    break
            if matchedNodeB is None:
                # error, and skip to next node in A
                print "error: cannot find vote node for", getObjId(nodeA)
                if tagError:
                    e = SubElement(nodeA, 't2_tag', {'name' : "ERROR-no-match-node-" + voter, 'key' : "E"})
                continue

            # get vote in B
            votingTagB = [x for x in matchedNodeB.findall('t2_tag') if 'VOTE-yes' in x.get('name') or 'VOTE-no' in x.get('name')]
            if len(votingTagB) is not 1:
                # voting wrong, probably missing
                r = SubElement(nodeA, 't2_tag', {'name' : "REVOTE-" + voter, 'key' : "R"})
                print getObjId(matchedNodeB), "vote tag wrong."
                continue
            else :
                # print getObjId(matchedNodeB) , "vote accepted."
                allVote += 1
                # voteAcceptTagA = SubElement(nodeA, 't2_tag', {'name' : "VALID-" + voter, 'key' : "O"})
                if 'VOTE-yes' in votingTagB[0].get('name') : 
                    voteYes += 1
                votedTagA.set('name', 'voted-' + str(voteYes) + '/' + str(allVote))


def voteStatistician2(objA, objB, voter, tagError = 1) : 
    # TODO: make the function function
    for subObjA in objA : 
        if subObjA.tag not in objList : 
            continue
        nCandidate = len([x for x in subObjA.findall('t2_tag') if 'ET-' in x.get('name') or 'EC-' in x.get('name')])
        foundMatchedObjB = 0
        for subObjB in objB : 
            if subObjA.tag == subObjB.tag and getObjId(subObjA) == getObjId(subObjB) :
                foundMatchedObjB = 1
                if subObjA.tag == 't2_node' : 
                    if nCandidate is 0 :
                        continue
                    elif nCandidate is not 1 :
                        print "error: too many candidate error tags. (", nCandidate, ")"
                        if tagError:
                            e = SubElement(subObjA, 't2_tag', {'name' : "ERROR-multiple-tag", 'key' : "E"})
                        continue

                    votedTagA = [x for x in subObjA.findall('t2_tag') if 'voted-' in x.get('name')]
                    if not votedTagA : 
                        votedTagA = SubElement(subObjA, 't2_tag', {'name' : "voted-0/0", 'key' : "M"})
                        allVote = 0
                        voteYes = 0;
                    elif len(votedTagA) is not 1 :
                        print "error: too many voted tags."
                        if tagError :
                            e = SubElement(subObjA, 't2_tag', {'name' : "ERROR-multiple-vote-" + voter, 'key' : "E"})
                        continue
                    else : 
                        votedTagA = votedTagA[0]
                        posLine = votedTagA.get('name').find('-')
                        posBias = votedTagA.get('name').find('/')
                        voteYes = int(votedTagA.get('name')[posLine + 1 : posBias])
                        allVote = int(votedTagA.get('name')[posBias + 1 :])

                    # voting tags, list of votes, as string
                    votingTagB = [x.get('name') for x in subObjB.findall('t2_tag') if 'VOTE-yes' in x.get('name') or 'VOTE-no' in x.get('name')]
                    if len(votingTagB) is not 1 :
                        # voting wrong, probably missing
                        r = SubElement(subObjA, 't2_tag', {'name' : "REVOTE-" + voter, 'key' : "R"})
                        print getObjId(subObjB), "vote tag wrong, needs revisit."
                        continue
                    else :
                        allVote += 1
                        if 'VOTE-yes' in votingTagB : 
                            voteYes += 1
                        votedTagA.set('name', 'voted-' + str(voteYes) + '/' + str(allVote))

                voteStatistician2(subObjA, subObjB, voter, tagError)
                break
        if not foundMatchedObjB : 
            if subObjA.tag == 't2_node' and nCandidate is 1:
                # error on finding the same node in B
                print "error: cannot find vote node, len(node) =", str(len(subObjB)), getObjId(subObjA)
                if tagError:
                    e = SubElement(subObjA, 't2_tag', {'name' : "ERROR-" + str(len(subObjB)) + "-node-" + voter, 'key' : "E"})
            else :
                print "error: cannot find the same", subObjA.tag

# tool funcions end


import xml.etree.ElementTree as ET
import sys

sys.setrecursionlimit(1000000) 

print "parsing main file"
mainRoot = ET.parse(mainFile).getroot()
project = mainRoot.find('project')
project.set('title', outFile)

if mainRoot.tag != 'trakem2' : 
    print mainFile, ' has invalid trakem2 format!'
else : 
    headerStr = ''
    mainFileHandle = open(mainFile)
    for newLine in mainFileHandle : 
        if newLine == '<trakem2>\n' : 
            break
        headerStr += newLine
    mainFileHandle.close()
    
    for votingFile in votingFiles : 
        subRoot = ET.parse(votingFile).getroot()
        if subRoot.tag != 'trakem2' : 
            print mainFile, ' has invalid trakem2 format!'
        else : 
            print "processing", votingFile
            voteStatistician(mainRoot, subRoot, getVoter(votingFile))

    print "writing to file", outFile
    treeStr = ET.tostring(mainRoot, 'ISO-8859-1')
    outFileHandle = open(outFile, 'w')
    outFileHandle.write(headerStr)
    outFileHandle.write(treeStr[treeStr.index('\n') + 1 : ])
    outFileHandle.close()
            
