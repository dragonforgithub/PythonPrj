# Sheldon : 2019-04-25
import sys,getopt
from xml.etree import cElementTree as et
from graphviz import Digraph as gh
import random
import os

# cluster_
PREFIX_TOPTO_ID_NODE = "cluster_node_"
PREFIX_TOPTO_ID_PIPELINE = "cluster_pipe_"


class PortDesc:
    PORT_NAME = "PortName"
    PORT_ID = "PortId"
    NODE_NAME = "NodeName"
    NODE_ID = "NodeId"
    NODE_INSTANCE = "NodeInstance"
    NODE_INSTANCE_ID = "NodeInstanceId"


def makeNodeTopoId(pipelineName, nodeId, nodeInsId):
    return PREFIX_TOPTO_ID_NODE+pipelineName+'_'+str(nodeId)+"_"+str(nodeInsId)


def makePipelineTopoId(pipelineName):
    return PREFIX_TOPTO_ID_PIPELINE+str(pipelineName)


def makeNodePortTopoId(pipelineName, nodeId, nodeInsId, nodePortId):
    return makeNodeTopoId(pipelineName, nodeId, nodeInsId)+'_'+nodePortId


def findUsercase(root, usercaseName):
    for usercaseRoot in root.findall('.//Usecase'):
        name = usercaseRoot.find('UsecaseName').text.strip()
       # print(name,'####')
        if name == usercaseName:
            return usercaseRoot
    return None


def findPipeline(root, pipelineName):
    for pipelineRoot in root.findall('.//Pipeline'):
        name = pipelineRoot.find('PipelineName').text.strip()
        print(name)
        if name == pipelineName:
            return pipelineRoot
    return None


def getElemText(linkPort, tagName):
    return linkPort.find(tagName).text.strip()


def parseLinkPort(linkPort):
    portName = getElemText(linkPort, PortDesc.PORT_NAME)
    portId = getElemText(linkPort, PortDesc.PORT_ID)
    nodeName = getElemText(linkPort, PortDesc.NODE_NAME)
    nodeId = getElemText(linkPort, PortDesc.NODE_ID)
    nodeIns = getElemText(linkPort, PortDesc.NODE_INSTANCE)
    nodeInsId = getElemText(linkPort, PortDesc.NODE_INSTANCE_ID)

    port = LinkPort(nodeName, nodeId, nodeInsId, portId, portName)
    return port

def updateNodes(node,nodes,portId):
    tempNode = nodes.get(node.topoId,None)
    if tempNode:
        tempNode.appendPortId(portId)
    else:
        nodes[node.topoId]=node
        node.appendPortId(portId)


class Drawable:
    def draw(self, graph=None):
        pass


class Node(Drawable):
    def __init__(self, pipelineName, nodeName, nodeId, nodeInsId, portCount=0):
        self.pipelineName = pipelineName
        self.nodeName = nodeName
        self.nodeId = nodeId
        self.nodeInsId = nodeInsId
        self.portCount = portCount
        self.portIds = set()
        self.setTopoId(pipelineName, nodeId, nodeInsId)
        self.nodeGraph = gh(self.topoId, graph_attr={
                            'label': self.nodeName+'('+self.nodeId+'/'+self.nodeInsId+')', 'height': '4'})

    def setPortCount(self, portCount):
        self.portCount = portCount

    def setTopoId(self, pipelineName, nodeId, nodeInsId):
        self.topoId = makeNodeTopoId(pipelineName, nodeId, nodeInsId)

    def appendPortId(self, portId):
        self.portIds.add(portId)

    def draw(self, graph):
        portIds = list(self.portIds)
        for portId in portIds:
            self.nodeGraph.node(makeNodePortTopoId(
                self.pipelineName, self.nodeId, self.nodeInsId, portId), str(portId), fontsize='10')
        graph.subgraph(self.nodeGraph)

    def __eq__(self, other):
        return self.topoId == other.topoId

    def __ne__(self, other):
        return self.topoId != other.topoId


class LinkPort:
    def __init__(self, nodeName, nodeId, nodeInsId, portId, portName):
        self.nodeName = nodeName
        self.nodeId = nodeId
        self.nodeInsId = nodeInsId
        self.portId = portId
        self.portName = portName


class Link(Drawable):
    def __init__(self, pipelineName, srcLinkPort=None, dstLinkPorts=None):
        self.pipelineName = pipelineName
        self.srcLinkPort = srcLinkPort
        self.dstLinkPorts = dstLinkPorts

    def draw(self, graph=None):
        srcNodePortId = makeNodePortTopoId(
            self.pipelineName, self.srcLinkPort.nodeId, self.srcLinkPort.nodeInsId, self.srcLinkPort.portId)
        for dstPort in self.dstLinkPorts:
            dstNodePortId = makeNodePortTopoId(
                self.pipelineName, dstPort.nodeId, dstPort.nodeInsId, dstPort.portId)
            # graph.edge(srcNodePortId,dstNodePortId,arrowsize='0.5')
            # graph.edge(srcNodePortId,dstNodePortId,arrowsize='0.5',label=self.srcLinkPort.portName+"->"+dstPort.portName,fontsize='9')
            graph.edge(srcNodePortId, dstNodePortId, arrowsize='0.5', headlabel=dstPort.portName, taillabel=self.srcLinkPort.portName,
                       labelfontsize='11', labeldistance='5', labelangle='0', labelfontcolor='blue', labelloc='b', pendWidth='0.1')


class Pipeline(Drawable):
    def __init__(self, pipelineName, nodes, links,rankDir='LR'):
        self.pipelineName = pipelineName
        self.nodes = nodes
        self.links = links
        self.rankDir=rankDir
        self.pipelineTopoId = makePipelineTopoId(self.pipelineName)
        self.pipelineGraph = gh(self.pipelineTopoId, node_attr={
                                'shape': 'circle'}, graph_attr={'label': self.pipelineName})
        self.pipelineGraph.attr(rankdir=self.rankDir)
        self.configGraph()

    def configGraph(self):
        #self.pipelineGraph.engine = 'dot'
        #self.pipelineGraph.attr(rankdir='TB')
        # self.pipelineGraph.attr(splines='curved')
       # self.pipelineGraph.attr(splines='true')
        self.pipelineGraph.attr(overlap='false')
        self.pipelineGraph.attr(size="9.0,5.0")
        # self.pipelineGraph.attr(pad="30")
        self.pipelineGraph.attr(page="40")
        # self.pipelineGraph.attr(ratio='expand')
        self.pipelineGraph.attr('node', width='0.5')
       # self.pipelineGraph.attr(concentrate='true')
        #self.pipelineGraph.attr(pack='true')
       # self.pipelineGraph.attr(defaultdist='100')
       # self.pipelineGraph.attr(mode='spring')
        self.pipelineGraph.attr(ratio='fill')
        self.pipelineGraph.attr(nodesep='0.3')
        self.pipelineGraph.attr(ranksep='1.8')

    def setFormat(self,format='pdf'):
        self.pipelineGraph.format=format

    def setRankDir(self,rankDir='LR'):
        self.rankDir = rankDir
        self.pipelineGraph.attr(rankdir=self.rankDir)

    def draw(self, graph=None):
        for topoId in self.nodes:
            self.nodes[topoId].draw(self.pipelineGraph)
        for link in self.links:
            link.draw(self.pipelineGraph)

        if graph == None:
            #self.pipelineGraph.view()
            self.pipelineGraph.render(cleanup=True,view=True)
        else:
            graph.subgraph(self.pipelineGraph)


class UseCase(Drawable):
    def __init__(self, root, sourceFileName=None, usecaseName=None, prefPipelineName=None,format='pdf',rankdir='LR'):
        self.root = root
        self.usercaseName = usecaseName
        self.prefPipelineName = prefPipelineName
        self.usercaseGraph = None
        self.prefPipeline = None
        self.rankdir = rankdir
        self.format=format
        self.pipelines = []
    
        if(self.prefPipelineName == None):
            self.usercaseGraph = gh(sourceFileName+"_"+self.usercaseName, node_attr={'shape': 'circle'},format=self.format, graph_attr={'label': self.usercaseName})
            self.configGraph()
        else:
            self.prefPipeline = findPipeline(root, self.prefPipelineName)

    def configGraph(self):
         self.usercaseGraph.engine = 'dot'
         self.usercaseGraph.attr(rankdir=self.rankdir)
         self.usercaseGraph.attr(overlap='false')
         #self.usercaseGraph.attr(size="99.0,96.0")
        #  self.usercaseGraph.attr(size="ideal")
         self.usercaseGraph.attr('node', width='0.4')
         self.usercaseGraph.attr(nodesep='0.3')
         self.usercaseGraph.attr(ranksep='1.9')
        #  self.usercaseGraph.attr(ratio='compress')
        #  self.usercaseGraph.attr(page='10')


    def parseUserCase(self):
        pass

    def parsePipeline(self, pipelineRoot):
        pipelineName = pipelineRoot.find('PipelineName').text.strip()
        print(pipelineName)
        links=[]
        nodes={}
        for link in pipelineRoot.findall('.//Link'):
            srcLinkPort = parseLinkPort(link.find('SrcPort'))
            tempNode = Node(pipelineName,srcLinkPort.nodeName,srcLinkPort.nodeId,srcLinkPort.nodeInsId)
            updateNodes(tempNode,nodes,srcLinkPort.portId)
            dstLinkPorts=[]
            for dst in link.findall('DstPort'):
                dstLinkPort = parseLinkPort(dst)
                dstLinkPorts.append(dstLinkPort)
                tempNode = Node(pipelineName,dstLinkPort.nodeName,dstLinkPort.nodeId,dstLinkPort.nodeInsId)
                updateNodes(tempNode,nodes,dstLinkPort.portId)
            linkBundle=Link(pipelineName,srcLinkPort,dstLinkPorts)
            links.append(linkBundle)

        pipeline = Pipeline(pipelineName,nodes,links)
        return pipeline


    def draw(self,graph=None):
        if self.prefPipelineName:
            pipeline = self.parsePipeline(self.prefPipeline)
            pipeline.setFormat(self.format)
            pipeline.setRankDir(self.rankdir)
            pipeline.draw()
            print("Generate:" + pipeline.pipelineName, pipeline.pipelineTopoId)
        else:
            usecaseRoot = findUsercase(self.root,self.usercaseName)
            print(self.usercaseName,usecaseRoot)
            for pipelineRoot in usecaseRoot.findall('.//Pipeline'):
                pipeline = self.parsePipeline(pipelineRoot)
                self.pipelines.append(pipeline)
            for pipeline in self.pipelines:
                pipeline.draw(self.usercaseGraph)
                print ("Generate:" + pipeline.pipelineName, pipeline.pipelineTopoId)
            #self.usercaseGraph.view()
            self.usercaseGraph.render(cleanup=True,view=True)

####################################################################

def parseCommand(command):
    pass


def help():
    starCount=100
    print('*'*starCount)
    print('Usage : python topologyParse.py -options')
    print('\noptions :\n')
    print('''-t:topology XML. 
             e.g.
             python topologyParse.py -t:titan17x_usecases.xml
    ''')
    print('''-u:usecaseName  ,draw an usecase. 
             e.g.
             python topologyParse.py -u:UsecaseRaw8 
             will draw usecase topology of UsecaseRaw8
    ''')
    print('''-p:pipelineName ,draw a pipeline.
             e.g. 
             python topologyParse.py -p:Realtime0 
             will draw pipeline topology of Realtime0
    ''')
    print('''-f:format , format of output
             e.g. 
             python topologyParse.py -p:Realtime0 -f:png
             will output pipeline topology of Realtime0 as png
    ''')
    print('*'*starCount)

OPTS=['-h','-t','-u','-p','-f']
FORMATS=['png','pdf','svg','jpg','gif']
ORIENTATIONS=['LR','TB']

def checkParameter(arg_len, arg_val):
    for i in range(0, arg_len):
        optKV=arg_val[i].split(':')
        print ("arg"+ str(i) +"  :", optKV)
        res = optKV[0] in OPTS
        if res==False:
            return (False, optKV[0] + " not in OPTS")
    return (True, "Parameter is OK")

def clearTemp():
    for file in os.listdir('.'):
        absFile='.'+os.path.sep+file
        if os.path.isfile(absFile) and file.endswith('.gv'):
            print(absFile)
            os.remove(absFile)

def main(argv):
    argc = len(argv)
    sourceFileName='titan17x_usecases.xml' #default topology
    format = 'pdf'
    queryUsecase=None
    queryPipeline=None
    queryOrientation='LR'

    print("Script name ：", argv[0])
    result=checkParameter(argc-1, argv[1:])
    if (result[0]==False):
        print("Error : " + result[1])
        help()
        exit(0)

    opts, args = getopt.getopt(argv[1:], "ht:u:p:f:")
    for op, value in opts:
        if op == "-h":
            help()
            exit(0)
        elif op == "-t":
            sourceFileName = value.strip(':')
            print("->sourceFileName：", sourceFileName)
        elif op == "-u":
            queryUsecase = value.strip(':')
            print("->queryUsecase：", queryUsecase)
        elif op == "-p":
            queryPipeline = value.strip(':')
            print("->queryPipeline：", queryPipeline)
        elif op == "-f":
            format = value.strip(':')
            print("->format：", format)

    tree = et.parse(sourceFileName)
    root = tree.getroot()

    try:
        usercase = UseCase(root,sourceFileName,queryUsecase,queryPipeline,format,queryOrientation)
        usercase.draw()
        
    except:
        print('ERROR : Could not find usecase = '+ str(queryUsecase) +' or pipeline = ' + str(queryPipeline))
        exit(1)
    finally:
        #clearTemp()
        pass


if __name__ == '__main__':
    main(sys.argv)
