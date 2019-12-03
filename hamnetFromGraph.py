#!/usr/bin/python
# -*- coding: utf-8 -*-
# hamnetFromGraph.py
import networkx as nx
import matplotlib.pyplot as plt
import sys
import os
import stat
import socket
import struct
import subprocess
import settings as set #settings.py
import rewrite as rew
import check #check.py
import time
import numpy as np

from mininet.net import Containernet
from mininet.cli import CLI
from mako.template import Template
from mininet.link import Intf, Link, TCLink
from collections import deque
from scipy.optimize import minimize
from progress.bar import Bar, IncrementalBar
from datetime import datetime

nodeList = []

def graph2Network(G, net):

    nextip = 738197504  #44.0.0.0

    for (u,v,c) in G.edges.data():

        set.restartExited()

        left_ip = nextip
        nextip+=1
        right_ip = nextip
        nextip +=1

        left_ip_isset=False
        right_ip_isset=False


        if u not in net:
            net.addDocker(u, ip='%s/31' % socket.inet_ntoa(struct.pack('!I',left_ip)), dimage="kraken_dind", dcmd="dockerd-entrypoint.sh", prefixLen=31)
            left_ip_isset=True

            h=net.get(u)
            h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=0")
            h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=0")
            h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=0")
        if v not in net:
            net.addDocker(v, ip='%s/31' % socket.inet_ntoa(struct.pack('!I',right_ip)), dimage="kraken_dind",  dcmd="dockerd-entrypoint.sh", prefixLen=31)
            right_ip_isset=True

            h=net.get(v)
            h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=0")
            h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=0")
            h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=0")

        if1 = (u+'-'+v)[-15:]
        if2 = (v+'-'+u)[-15:]

        try:
            net.addLink(net.get(u), net.get(v), intfName1=if1, intfName2=if2)
        except:
            print("Unexpected error:", sys.exc_info()[0], u, v, c)

        if not left_ip_isset:
            print("set on host %s interface %s" % (u, if1))
            net.get(u).setIP(socket.inet_ntoa(struct.pack('!I',left_ip)), prefixLen=31, intf=if1)
        if not right_ip_isset:
            print("set on host %s interface %s" % (v, if2))
            net.get(v).setIP(socket.inet_ntoa(struct.pack('!I',right_ip)), prefixLen=31, intf=if2)
    #print (nodeList)
    #return


def limitLinks(G, net, routing):
    for (u, v, c) in G.edges.data():
        interfaceNameUV = (u+'-'+v)[-15:]
        interfaceNameVU = (v+'-'+u)[-15:]
        hostU = net.get(u)
        hostV = net.get(v)

        hostU.cmd('tc qdisc add dev %s root netem delay 1.940ms 8.515ms distribution pareto rate 4096kbit slot 0.683ms 0.683ms packets 1' % interfaceNameUV)
        hostV.cmd('tc qdisc add dev %s root netem delay 1.940ms 8.515ms distribution pareto rate 4096kbit slot 0.682ms 0.683ms packets 1' % interfaceNameVU)


def restartLinks(G, net):
    for (u, v, c) in G.edges.data():
        interfaceNameUV = (u+'-'+v)[-15:]
        interfaceNameVU = (v+'-'+u)[-15:]
        hostU = net.get(u)
        hostV = net.get(v)

        hostU.cmd("ip link set %s down" % interfaceNameUV)
        hostV.cmd("ip link set %s down" % interfaceNameVU)
        hostU.cmd("ip link set %s up" % interfaceNameUV)
        hostV.cmd("ip link set %s up" % interfaceNameVU)

def startDocker(G, net):
    bar = IncrementalBar('Starting Containers', max = numberOfNodes)
    for node in G.nodes():
        rew.rewriteConfig(net.get(node).name)
        set.restartExited()
        #print net.get(node).name
        rew.agent_param(net.get(node).name)
        rew.herd_param(net.get(node).name)
        subprocess.call(['docker cp ./tmp/. mn.%s:etc/kraken/.' % net.get(node).name],shell=True)
        if net.get(node).name in set.seeder:
            net.get(node).cmdPrint('docker run --restart=unless-stopped --name registry -d -p 5001:5000 172.17.0.1:5000/registry')
        #subprocess.call(['docker exec mn.%s chmod 777 ./etc/kraken/agent_param.sh ./etc/kraken/herd_param.sh /etc/kraken/herd_start_processes.sh ./etc/kraken/herd_param.sh' % net.get(node).name],shell=True)
        if net.get(node).name in set.servers:
            #net.get(node).cmdPrint('export IP=%s && docker-compose -f stack_server.yml up -d' % net.get(node).IP())
            net.get(node).cmdPrint('source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_server.yml up -d' % net.get(node).IP())
        else:
            #net.get(node).cmdPrint('export IP=%s && docker-compose -f stack_client.yml up -d' % net.get(node).IP())
            net.get(node).cmdPrint('source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_client.yml up -d' % net.get(node).IP())

        bar.next()
    bar.finish()

def containerInfo():
    infoIP = open('infoIP.txt', 'w+')
    infoName = open('infoName.txt', 'w+')
    for node in G.nodes():
        infoIP.write(net.get(node).IP() + '\n')
        infoName.write(net.get(node).name + '\n')

        #net.get(node).cmdPrint('export IP=%s && docker-compose up -d' % net.get(node).IP())

G = nx.read_edgelist(set.edgelist)


remove = [node for node in G.nodes() if not node.startswith('d')]
G.remove_nodes_from(remove)

graphs = list(nx.connected_component_subgraphs(G))

numberOfNodes = 0

for H in graphs:
    if H.number_of_nodes() > numberOfNodes:
        G = H
        numberOfNodes = H.number_of_nodes()


net = Containernet()
graph2Network(G, net)
net.start()

currentInstance = datetime.strftime(datetime.now(),'%Y%m%d%H%M')
subprocess.call(['mkdir measurements/%s/' % currentInstance],shell=True)
#print currentInstance
doc = open('measurements/currentInstance.txt', 'w+')
doc.write(currentInstance)
doc.close()


containerInfo()
set.readNodes()

print("Restarting links for ipv6")
restartLinks(G, net)
print("Start Container")
startDocker(G, net)
print("Limit links")
limitLinks(G, net, 'hallo')
#print("Start Cluster")
time.sleep(5)
print("Check for faulty containers")
check.check()
#First host: 44.0.0.0
#net.get('db0son').cmd('docker exec -it default_database_1 ./cockroach init --insecure')

#set.readNodes()
set.findInterfaces()
set.setupIptables()
set.restartExited()

CLI(net)
net.stop()

#print("hallo")
#nx.draw_kamada_kawai(G)
#plt.show()
