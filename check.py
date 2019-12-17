#!/usr/bin/python
# -*- coding: utf-8 -*-
# test.py

from progress.bar import Bar, IncrementalBar
from progress.spinner import Spinner
import time
import os
import subprocess
import settings as set

global repeat
repeat = False

def check():
    repeat = False
    global repeat
    overallCheck = True
    #set.readNodes()
    sumB = 0
    babeld = []
    sumA = 0
    agent = []
    sumH = 0
    herd = []
    for node in set.name:
        tmp = subprocess.check_output(['docker exec mn.%s docker ps' % node],shell=True)
        doc = open('./tmp.txt', 'w+')
        doc.write(tmp)
        doc.close()
        checkB = False #Check for babeld container
        checkA = False #Check for dragonfly_client container
        checkH = False #Check for opentracker container

        with open('./tmp.txt') as info:
            lines = info.readlines()
            for line in lines:
                tmp = line.split()
                #print tmp[-1]
                if tmp[-1] == 'babeld':
                    checkB = True
                if tmp[-1] == 'kraken_agent':
                    checkA = True
                if node in set.servers:
                    if tmp[-1] == 'kraken_herd':
                        checkH = True
                else:
                    checkH = True
        if checkB == False:
            overallCheck = False
            babeld.append(node)
            sumB = sumB + 1
        if checkA == False:
            overallCheck = False
            agent.append(node)
            sumA = sumA + 1
        if checkH == False:
            overallCheck = False
            herd.append(node)
            sumH = sumH + 1

    print ('%s container(s) not running babeld: %s' % (str(sumB),babeld))
    print ('%s container(s) not running kraken_agent: %s' % (str(sumA),agent))
    print ('%s container(s) not running kraken_herd: %s' % (str(sumH),herd))

    #print ('%s babeld container not running correctly\n%s kraken_agent container not running correctly\n%s kraken_herd container not running correctly' % (str(sumB), str(sumA), str(sumH)))

    for node in babeld:
        if node in set.servers:
            subprocess.call(['docker exec -it mn.%s sh -c "source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_server.yml up -d"' % (node, set.ip[set.name.index(node)])],shell=True)
        else:
            subprocess.call(['docker exec -it mn.%s sh -c "source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_client.yml up -d"' % (node, set.ip[set.name.index(node)])],shell=True)
    for node in agent:
        if not node in babeld:
            if node in set.servers:
                subprocess.call(['docker exec -it mn.%s sh -c "source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_server.yml up -d"' % (node, set.ip[set.name.index(node)])],shell=True)
            else:
                subprocess.call(['docker exec -it mn.%s sh -c "source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_client.yml up -d"' % (node, set.ip[set.name.index(node)])],shell=True)
    for node in herd:
        if not node in (babeld or agent):
            subprocess.call(['docker exec -it mn.%s sh -c "source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_server.yml up -d"' % (node, set.ip[set.name.index(node)])],shell=True)

    if overallCheck == True:
        repeat = False
    else:
        repeat = True
    #return repeat
