# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 12:56:56 2015

@author: Jason
"""
import pico
import numpy

#input = name start, type start, name end, type end; given in multiples of 4 delimited by commas
#3 types: house, source, junction 
#names are unique
 
#hello = pydata 
def hello(pydata="hello"): 
    class node:
        def __init__(self, name, kind):
            self.name = name
            self.type = kind

    class edge:
        def __init__(self, startNode, endNode):
            self.start = startNode
            self.end = endNode
    firstDollar = pydata.find("$")
    secondDollar = pydata.rfind("$")
    graphData = pydata[0:firstDollar]
    flowData = pydata[firstDollar + 1: secondDollar]
    leakData = pydata[secondDollar + 1:]
    
    #input = "reservoir,s,meter1,m,meter1,m,junction1,j,junction1,j,meter2,m,meter2,m,jason,h,junction1,j,sreyas,h"
    #input2 = "reservoir1,s,junction1,j,reservoir2,s,junction1,j,junction1,j,jason,h"
    input3 = "R1 s J1 j R2 s J1 j J1 j H1 h"
    #input3 = graphData
    inputList = input3.strip().split(" ")
    #print inputList
    
    nodes = []
    edges = []
    #generate set of nodes and edges
    for i in xrange(0,len(inputList),4):
        #print i
        startName = inputList[i]
        startType = inputList[i+1]
        endName = inputList[i+2]
        endType = inputList[i+3]
        
        startNode = node(startName, startType)
        endNode = node(endName, endType)
    
        #build edges list
        edgeTemp = edge(startNode, endNode)
        if edgeTemp not in edges:
            edges.append(edgeTemp)    
        
        #build nodes list
        startPresentAlready = False
        endPresentAlready = False
        for currentNode in nodes:
            if startNode.name == currentNode.name:
               startPresentAlready = True
            if endNode.name == currentNode.name:
                endPresentAlready = True
        if (startPresentAlready == False):
            nodes.append(startNode)
        if (endPresentAlready == False):
            nodes.append(endNode)
        
    #generate paths
    for node in nodes:
        if node.type == "h":
            currentPath = []
            paths = []
            findPath(node, currentPath, edges, paths)
            #return len(paths)
    #------------------
    #calculate average & standard deviation flow percentage loss per edge
    #input data is essentially a table in string form
    #number of objects as 'columns'; number of days as 'rows'
    #measurement at each object node
    
    #   R1 R2 J1 H1
    #D1  1000 1000 1800 1600
    #D2 900 900 1750 1600
    #D3 800 800 1600 1500
    
    initialData = "R1 R2 J1 H1 1000 900 800 1000 900 800 1800 1750 1600 1600 1600 1500"
    #initialData = flowData
    initialData = initialData.split(" ")    
    numNodes = len(nodes)
    numDataPoints = len(initialData)
    numDays = (numDataPoints - numNodes)/numNodes
    reformat = ""
    for i in xrange(0, numNodes):
        reformat = reformat + initialData[i] + " "  

    for i in xrange(0, numDays):
        string = ""
        for j in xrange(numNodes + i, len(initialData), numDays):
            string = string + initialData[j] + " "
        reformat += string
    print reformat
    empiricalData = reformat
    #empiricalData = "R1 R2 J1 H1 1000 1000 1800 1600 900 900 1750 1600 800 800 1600 1500"
    dataList = empiricalData.strip().split(" ")
     
    nodeOrder = []
    for i in xrange(0, numNodes):
        nodeOrder.append(dataList[i])
    
    dictMeterValues = {} #keeps track of datapoints relevant to each object; sums to get total flow
    for node in nodeOrder:
        #print node
        dictMeterValues[node] = []
    
    #calculate raw sums    
    counter = 0
    for i in xrange(numNodes, len(dataList)):
        print counter
        print dataList[i]
        currentNode = nodeOrder[counter]
        print currentNode
        dictMeterValues[currentNode].append(int(dataList[i]))
        if counter == numNodes - 1:
            counter = 0
        else:
            counter += 1
    
    print dictMeterValues
    
    dictPercentLoss = {}
    for edge in edges:
        initialEdge = edge
        dictPercentLoss[initialEdge] = []
        startName = edge.start.name
        endName = edge.end.name
        #calculate number of connections for both start and end nodes
        #for startNode
        startConnections = 0
        for edge in edges:
            if edge.start.name == startName:
                startConnections += 1
        #for endNode
        endConnections = 0
        for edge in edges:
            if edge.end.name == endName:
                endConnections += 1
        
        #total flow/# of connections
        for i in xrange(0, numDays):
            startMeterValue = dictMeterValues[startName][i]
            endMeterValue = dictMeterValues[endName][i]
            loss = abs(float(endMeterValue/endConnections) - float(startMeterValue/startConnections))
            fractionLoss = loss/float(startMeterValue/startConnections)
            dictPercentLoss[initialEdge].append(fractionLoss)
        
    print dictPercentLoss
    
    #calculate average percent loss for each edge and standard deviation
    dictOutput = {}
    for edge in edges:
        initialEdge = edge
        dictOutput[initialEdge] = []
        losses = dictPercentLoss[edge]
        
        sum = 0
        for i in xrange(0, numDays):
            sum += losses[i]
        
        average = sum/float(numDays)
        standardDeviation =  numpy.std(losses)
        dictOutput[initialEdge] = [average, standardDeviation]
    
    print dictOutput
   
   #------------------
    #pinpoint edges that are leaky
    
    #   R1 R2 J1 H1
    #D1  1200 1200 2200 1600 --> one day's worth of meter data  
    testData = "1200 1200 2200 1600"
    #testData = leakData
    testData = testData.strip().split(" ")
    dictMeterValues = {} #keeps track of datapoints relevant to each object; sums to get total flow
    for i in xrange(0, len(nodeOrder)): #nodeOrder is list of node names as string
        dictMeterValues[nodeOrder[i]] = testData[i]
    
    dictPercentLoss = {}
    for edge in edges:
        initialEdge = edge
        dictPercentLoss[initialEdge] = 0
        startName = edge.start.name
        endName = edge.end.name
        print startName, endName
        #calculate number of connections for both start and end nodes
        #for startNode
        startConnections = 0
        for edge in edges:
            if edge.start.name == startName:
                startConnections += 1
        #for endNode
        endConnections = 0
        for edge in edges:
            if edge.end.name == endName:
                endConnections += 1
        
        #total flow/# of connections
        startMeterValue = float(dictMeterValues[startName])
        endMeterValue = float(dictMeterValues[endName])
        loss = abs(float(endMeterValue/endConnections) - float(startMeterValue/startConnections))
        fractionLoss = loss/float(startMeterValue/startConnections)
        dictPercentLoss[initialEdge] = fractionLoss
    #print dictPercentLoss
    
    #compare differences; flag edges that are >1.5 stdev from mean
    leaks = []    
    for edge in edges:
        output = dictOutput[edge]
        loss = dictPercentLoss[edge]
        average = output[0]
        stdev = output[1]
        print average, stdev, loss
        print loss - average, 2*stdev
        if abs(loss - average) > (2*stdev):
            print edge.start.name, edge.end.name
            leaks.append(edge.start.name + "-->" + edge.end.name)
   
   #RETURN SECTION
    returnString = ""
    #return edge labels
    for edge in edges:
        returnString += edge.start.name + "-->" + edge.end.name + " "
    returnString += "$ "
   
    #return average edge losses
    for edge in edges:
        returnString += str(dictOutput[edge][0]) + " "
    returnString += "% "
    
    #return today's edge losses
    for edge in edges:
        returnString += str(dictPercentLoss[edge]) + " "
    returnString += "# "
    
    #return potential leakages
    for leak in leaks:
        returnString += "leak + " "
    
    return returnString
    
#edits paths = set of all paths; works recursively
def findPath(currentNode, currentPath, edges, paths):
    currentPath.insert(0, currentNode)
    #print currentNode.name
    if currentNode.type == "s":
        paths.append(currentPath)
        print "CURRENT PATH: "
        for node in currentPath:
            print node.name
        return
    #look at connections
    for edge in edges:
        if edge.end.name == currentNode.name:
            findPath(edge.start, currentPath, edges, paths)
            currentPath.remove(currentPath[0])  
             
hello()             

#next steps:
#standard deviation for all
#comparing test data with averages: look for ones that have high difference from mean ~2 stdev
#highlight in red by sending pack to html doc --> potentially identify origin of leak  

                 
        
    

    
    
