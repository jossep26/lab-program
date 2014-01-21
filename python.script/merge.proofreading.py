# merge objects

mainFile = r'zby.20140113.cleanup.xml.gz'

subFiles = (r'wsx.20140116.synapse.xml.gz', 
            r'zjj.20140116.synapse.xml.gz', 
            r'btt.20140116.syanpse.xml.gz',
            )

outFile = r'zby.20140116.merge.synapse.xml.gz'

import xml.etree.ElementTree as ET
# from xml.etree.ElementTree import SubElement
import gzip
import os
import re
import sys
sys.setrecursionlimit(1000000) 

objList = ['t2_node', 't2_areatree', 't2_connector', 't2_layer_set']
skipList = ['t2_area', 't2_path', 't2_display']

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

def isVoteTag(tagString):
    voteRe = re.compile(r"^VOTE-(yes|no)$")
    return bool(voteRe.match(tagString))

def objectMerger(objA, objB) : 
    for subObjB in objB : 
        if subObjB.tag in skipList :
            continue
        for subObjA in objA : 
            if subObjA.tag == subObjB.tag and getObjId(subObjA) == getObjId(subObjB) : 
                if subObjA.tag == 't2_node' : 
                    t2_tagsB = subObjB.findall('t2_tag')
                    t2_tagsA = subObjA.findall('t2_tag')
                    tagsA_List = [x.get('name') for x in t2_tagsA];
                    subObjA.extend([x for x in t2_tagsB if not (isVoteTag(x.get('name'))) and x.get('name') not in tagsA_List])
                objectMerger(subObjA, subObjB)
                break
        else : 
            objA.append(subObjB)

print "parsing main project..."
mainRoot = parseProjectFileRoot(mainFile)
project = mainRoot.find('project')
project.set('title', os.path.basename(outFile))

if mainRoot.tag is None : 
    print mainFile, ' has invalid trakem2 format!'
else : 
    headerStr = getProjectHeaderString(mainFile)
    
    for subFile in subFiles : 
        print "processing project", subFile
        subRoot = parseProjectFileRoot(subFile)
        if subRoot.tag is None : 
            print mainFile, ' has invalid trakem2 format!'
        else : 
            objectMerger(mainRoot, subRoot)
            
    print "writing merged project to", outFile
    writeProject(outFile, headerStr, mainRoot)
