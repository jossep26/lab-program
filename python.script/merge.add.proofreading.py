# merge objects

mainFile = r'zby.20140113.cleanup.xml.gz'

subFiles = (r'wsx.20140116.synapse.xml.gz', 
            r'zjj.20140116.synapse.xml.gz', 
            r'btt.20140116.syanpse.xml.gz',
            )

outFile = r'zby.20140116.merge.synapse.xml.gz'

# switch between adding new objects and only updating existing ones
onlyMergeExisting = True

## Tools ##
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.ops import cascaded_union
import gzip
import os
import re
import sys
sys.setrecursionlimit(1000000) 

objList = ['t2_node', 't2_areatree', 't2_connector', 't2_layer_set']
skipList = ['t2_display']

def parseProjectFileRoot(filename):
    if filename.endswith(".xml.gz"):
        f = gzip.open(filename, "rb")
    elif filename.endswith(".xml"):
        f = open(filename, "rb")
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

def isVoteTag(tagString):
    voteRe = re.compile(r"^VOTE-(yes|no)$")
    return bool(voteRe.match(tagString))

def getObjId(objX) : 
    objId = objX.get('noid')
    if not objId : 
        objId = objX.get('oid')
        if not objId : 
            objId = objX.get('id')
    return objId

def setNewCoor(objA, newCoor) : 
    if objA.tag == 't2_node' : 
        objA.set('x', str(float(objA.get('x')) - newCoor[0]))
        objA.set('y', str(float(objA.get('y')) - newCoor[1]))
    if objA.tag == 't2_path' : 
        dStr = objA.get('d').split()
        for i in range(1, len(dStr), 3) : 
            dStr[i] = str(int(float(dStr[i]) - newCoor[0]))
        for i in range(2, len(dStr), 3) : 
            dStr[i] = str(int(float(dStr[i]) - newCoor[1]))
        objA.set('d', ' '.join(dStr))
    for subObj in objA : 
        setNewCoor(subObj, newCoor)

def subObjectMerger(objA, objB, offsetA = [0.0, 0.0], offsetB = [0.0, 0.0]) : 
    subOffsetA = objA.get('transform', 'matrix(1.0,0.0,0.0,1.0,0.0,0.0)')
    subOffsetA = [float(x) for x in subOffsetA[subOffsetA.index('(') + 1 : subOffsetA.rindex(')')].split(',')[-2 :]]
    subOffsetA[0] += offsetA[0]
    subOffsetA[1] += offsetA[1]
    
    subOffsetB = objB.get('transform', 'matrix(1.0,0.0,0.0,1.0,0.0,0.0)')
    subOffsetB = [float(x) for x in subOffsetB[subOffsetB.index('(') + 1 : subOffsetB.rindex(')')].split(',')[-2 :]]
    subOffsetB[0] += offsetB[0]
    subOffsetB[1] += offsetB[1]

    for subObjB in objB : 
        if subObjB.tag in skipList :
            continue
        for subObjA in objA : 
            if subObjA.tag == subObjB.tag and getObjId(subObjA) == getObjId(subObjB) :                
                if subObjA.tag == 't2_node' : 
                    t2_tagsB = subObjB.findall('t2_tag')     
                    t2_tagsA = subObjA.findall('t2_tag')
                    tagsA_List = [x.get('name') for x in t2_tagsA];
                    subObjA.extend([x for x in t2_tagsB if x.get('name') not in tagsA_List])
                    for x in subObjB.findall('t2_area') : 
                        setNewCoor(x, [subOffsetA[0] - subOffsetB[0], subOffsetA[1] - subOffsetB[1]])
                        subObjA.append(x)
                subObjectMerger(subObjA, subObjB, subOffsetA, subOffsetB)
                break
        elif not onlyMergeExisting : 
            setNewCoor(subObjB, [subOffsetA[0] - subOffsetB[0], subOffsetA[1] - subOffsetB[1]])
            objA.append(subObjB)

def objBorder(objA, borderCoor = [sys.maxint, sys.maxint, -sys.maxint - 1, -sys.maxint - 1]) : 
    if objA.tag == 't2_node' : 
        radiusA = float(objA.get('r', '0'))
        xCoor = float(objA.get('x'))
        yCoor = float(objA.get('y'))
        minX = round(xCoor - radiusA)
        minY = round(yCoor - radiusA)
        maxX = round(xCoor + radiusA)
        maxY = round(yCoor + radiusA)
        if minX < borderCoor[0] : borderCoor[0] = minX
        if minY < borderCoor[1] : borderCoor[1] = minY
        if maxX > borderCoor[2] : borderCoor[2] = maxX
        if maxY > borderCoor[3] : borderCoor[3] = maxY
    if objA.tag == 't2_path' : 
        dStr = objA.get('d').split()
        for i in range(1, len(dStr), 3) : 
            xCoor = float(dStr[i])
            if xCoor < borderCoor[0] : borderCoor[0] = xCoor
            if xCoor > borderCoor[2] : borderCoor[2] = xCoor
        for i in range(2, len(dStr), 3) : 
            yCoor = float(dStr[i])
            if yCoor < borderCoor[1] : borderCoor[1] = yCoor
            if yCoor > borderCoor[3] : borderCoor[3] = yCoor
    for subObj in objA : 
        objBorder(subObj, borderCoor)

resetList = ['t2_areatree', 't2_connector']

def resetObj(objA) : 
    if objA.tag in resetList : 
        borderCoor = [sys.maxint, sys.maxint, -sys.maxint - 1, -sys.maxint - 1];
        objBorder(objA, borderCoor)
        objA.set('width', str(borderCoor[2] - borderCoor[0] + 1))
        objA.set('height', str(borderCoor[3] - borderCoor[1] + 1))
        offsetA = objA.get('transform', 'matrix(1.0,0.0,0.0,1.0,0.0,0.0)')
        offsetA = [float(x) for x in offsetA[offsetA.index('(') + 1 : offsetA.rindex(')')].split(',')[-2 :]]
        objA.set('transform', 'matrix(1.0,0.0,0.0,1.0,' + str(offsetA[0] + borderCoor[0]) + ',' + str(offsetA[1] + borderCoor[1]) + ')')
        setNewCoor(objA, [borderCoor[0], borderCoor[1]])
    for subObj in objA : 
        resetObj(subObj)

def areaUnion(objA) : 
    for subObj in objA : 
        if subObj.tag == 't2_node' : 
            allPolygons = [];
            for newArea in subObj.findall('t2_area') : 
                for newPath in newArea.findall('t2_path') : 
                    allCorStr = newPath.get('d').split()
                    allCors = [float(allCorStr[i]) for i in range(0, len(allCorStr)) if i % 3 != 0]
                    newPolygon = Polygon([(allCors[i], allCors[i + 1]) for i in range(0, len(allCors), 2)])
                    if newPolygon.contains(Point(float(subObj.get('x')), float(subObj.get('y')))) : 
                        allPolygons.append(newPolygon)
                subObj.remove(newArea)
            if len(allPolygons) != 0 : 
                finalPolygon = list(cascaded_union(allPolygons).exterior.coords)
                pathStr = 'M ' + ' '.join([str(int(x[0])) + ' ' + str(int(x[1])) + ' L' for x in finalPolygon])
                SubElement(SubElement(subObj, 't2_area'), 't2_path', {'d' : pathStr[: -1] + 'z'})
        areaUnion(subObj)

def objectMerger(objA, objB) : 
    subObjectMerger(objA, objB)
    resetObj(objA)
    areaUnion(objA)

## Tools end ##   

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
