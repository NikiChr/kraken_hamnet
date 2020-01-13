#!/usr/bin/python
# -*- coding: utf-8 -*-
# downloadFiles.py

from scipy.optimize import minimize
from datetime import date
from progress.bar import Bar, IncrementalBar
from datetime import datetime, timedelta
import sys
import subprocess
import time
import os
import settings as set
import check

FNULL = open(os.devnull, 'w')
#set.readNodes()

def checkKrakenContainer():
    sum = 0
    herd = [False] * len(set.servers)
    agent = [False] * len(set.name)
    bar1 = IncrementalBar('Checking herd(s)', max = len(set.servers))
    while sum < len(set.servers):
        for node in set.servers:
            if herd[set.servers.index(node)] == False:
                if 'kraken_herd' in subprocess.check_output(['docker exec mn.%s docker ps' % node],shell=True):
                    sum = sum + 1
                    herd[set.servers.index(node)] = True
                    bar1.next()
                else:
                    sum = sum + 1
    if False in herd:
        print ('\nHerd(s) are not running correctly')
    else:
        print ('\nHerd(s) running')

    sum = 0
    bar2 = IncrementalBar('Checking agent(s)', max = len(set.name))
    while sum < len(set.name) - len(set.servers):
        #print complete
        for node in set.name:
            if agent[set.name.index(node)] == False:
                if 'kraken_agent' in subprocess.check_output(['docker exec mn.%s docker ps' % node],shell=True):
                    sum = sum + 1
                    agent[set.name.index(node)] = True
                    bar2.next()
                    #print ('\n' + node)
                else:
                    sum = sum + 1
    if False in agent:
        print ('\nAgent(s) are not running correctly')
    else:
        print ('\nAgent(s) running\n')



def download(image, iteration, outage = False, oNr = 0, oTime = 0):

    doc = open('./measurements/%s/%s/results/setup.txt' % (currentInstance, currentTest), 'w+')
    doc.write('Server:%s\nHosts:%s\nSeeders:%s\nImage:%s\nServer outage:%s\nOutage number:%s\nOutage start:%s' % (str(len(set.servers)), str(len(set.name)), str(len(set.seeder)), image, outage, oNr, oTime))
    doc.close()

    #edit input and starting environment
    image = image.strip()
    for node in set.name:
        subprocess.call(['docker exec mn.%s sh -c "rm -rf times/*"' % (node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
        subprocess.call(['docker exec mn.%s sh -c "mkdir times/"' % (node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

    #iteration
    for i in range(int(iteration)):
        print ('\n###\nTest #%s\n###' % (i + 1))
        print datetime.now()
        image = image.strip()

        #prepare downloads
        subprocess.call(['mkdir measurements/%s/%s/%s/' % (currentInstance,currentTest,i)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
        subprocess.call(['mkdir measurements/%s/%s/%s/time/' % (currentInstance,currentTest,i)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
        subprocess.call(['mkdir measurements/%s/%s/%s/traffic/' % (currentInstance,currentTest,i)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)


        #####################
        #deleting and Restarting
        deleted = [False] * len(set.name)
        restarted = [False] * len(set.name)
        sum = 0
        print 'Deleting images and restarting container'
        bar_restart = IncrementalBar('Finished cleanup(s)', max = len(set.name))
        for node in set.name:
            #if not node in set.seeder:
            subprocess.call(['docker exec -it mn.%s docker image rm -f localhost:16000/%s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            if node in set.servers:
                subprocess.call(['docker exec -it mn.%s sh -c "(docker stop kraken_agent kraken_herd && docker rm kraken_agent kraken_herd)"&' % (node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                #subprocess.call(['docker exec -it mn.%s sh -c "(docker stop kraken_agent kraken_herd && docker rm kraken_agent kraken_herd && source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_server.yml up -d)"' % (node, set.ip[set.name.index(node)])],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            else:
                subprocess.call(['docker exec -it mn.%s sh -c "(docker stop kraken_agent && docker rm kraken_agent)"&' % (node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                #subprocess.call(['docker exec -it mn.%s sh -c "(docker stop kraken_agent && docker rm kraken_agent && source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_client.yml up -d)"' % (node, set.ip[set.name.index(node)])],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            #else:
                #deleted[set.name.index(node)] = True
                #restarted[set.name.index(node)] = True
                #bar_restart.next()
                #sum = sum + 1
            subprocess.call(['docker exec -it mn.%s sh -c "iptables -Z"' % (node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

        while sum < len(set.name):
            for node in set.name:
                if 'localhost:16000/%s' % image in subprocess.check_output(['docker exec mn.%s docker image ls' % node],shell=True):
                    subprocess.call(['docker exec mn.%s docker image rm -f localhost:16000/%s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                if deleted[set.name.index(node)] == False: #delete
                    if node in set.servers:
                        if not ('kraken_agent' and 'kraken_herd') in subprocess.check_output(['docker exec mn.%s docker ps' % node],shell=True):
                            deleted[set.name.index(node)] = True
                        else:
                            if not ('docker rm' or 'docker stop') in subprocess.check_output(['docker exec mn.%s sh -c "ps -a"' % node],shell=True):
                                subprocess.call(['docker exec mn.%s sh -c "(docker stop kraken_agent kraken_herd && docker rm kraken_agent kraken_herd )"&' % (node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                    else:
                        if not 'kraken_agent' in subprocess.check_output(['docker exec mn.%s docker ps' % node],shell=True):
                            deleted[set.name.index(node)] = True
                        else:
                            if not ('docker rm' or 'docker stop') in subprocess.check_output(['docker exec mn.%s sh -c "ps -a"' % node],shell=True):
                                subprocess.call(['docker exec mn.%s sh -c "(docker stop kraken_agent && docker rm kraken_agent)"&' % node],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                else:
                    if restarted[set.name.index(node)] == False:
                        if node in set.servers:
                            if ('kraken_agent' and 'kraken_herd') in subprocess.check_output(['docker exec mn.%s docker ps' % node],shell=True):
                                sum = sum + 1
                                restarted[set.name.index(node)] = True
                                bar_restart.next()
                            else:
                                if not ('compose') in subprocess.check_output(['docker exec mn.%s sh -c "ps -a"' % node],shell=True):
                                    subprocess.call(['docker exec mn.%s sh -c "(source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_server.yml up -d)"&' % (node, set.ip[set.name.index(node)])],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
                                    #print node
                        else:
                            if 'kraken_agent' in subprocess.check_output(['docker exec mn.%s docker ps' % node],shell=True):
                                sum = sum + 1
                                restarted[set.name.index(node)] = True
                                bar_restart.next()
                            else:
                                if not ('compose') in subprocess.check_output(['docker exec mn.%s sh -c "ps -a"' % node],shell=True):
                                    subprocess.call(['docker exec mn.%s sh -c "(source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_client.yml up -d)"&' % (node, set.ip[set.name.index(node)])],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
            time.sleep(5)


        #print ('Restart successful')
        print ('\nAll traces of %s deleted on every host' % image)
        #checkKrakenContainer()

        check.check()
        while check.repeat == True:
            check.check()
        #time.sleep(60)
        bar_restart.finish()

        #prepare seeder
        print ('Preparing seeder(s)')
        #time.sleep(240)
        for node in set.seeder:
            subprocess.call(['docker exec mn.%s docker pull %s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker exec mn.%s docker tag %s localhost:15000/%s' % (node, image, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            print ('Pushing %s to registry(s) for sharing' % image)
            test = False
            while test == False:
                subprocess.call(['docker exec mn.%s sh -c "docker push localhost:15000/%s &> push.txt"' % (node, image)],shell=True)
                subprocess.call(['docker cp mn.%s:push.txt ./push.txt' % node],shell=True)
                with open('push.txt', 'r') as file:
                    data = file.read()
                    if 'received unexpected HTTP status: 502 Bad Gateway' in data:
                        print ('ERROR: %s' % data)
                    if 'received unexpected HTTP status: 500 Internal Server Error' in data:
                        print ('ERROR: %s' % data)
                    else:
                        test = True
                        print 'success'

        #start download
        sum = 0
        complete = [False] * len(set.name)
        print ('Starting download(s)')
        iStart = datetime.now()
        print iStart
        bar_download = IncrementalBar('Waiting for download(s)', max = len(set.name))
        for node in set.name:
            if not node in set.seeder:
                #time.sleep(0.1)
                subprocess.call(['docker exec mn.%s sh -c "(date +"%%Y-%%m-%%dT%%T.%%6N" > times/%s_%s_start.txt && docker pull localhost:16000/%s && date +"%%Y-%%m-%%dT%%T.%%6N" > times/%s_%s_end.txt)"&' % (node, node, i, image, node, i)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            else:
                complete[set.name.index(node)] = True
                bar_download.next()
                sum = sum + 1
                iPrev = datetime.now()

        #waiting for outage
        if outage == True:
            print ('Waiting %s seconds for outage...' % oTime)
            time.sleep(int(oTime))
            for j in range(1,int(oNr)+1):
                print set.servers[j]
                subprocess.call(['docker exec mn.%s docker stop kraken_herd &' % (set.servers[-j])],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

        #check download
        while sum < len(set.name):
            for node in set.name:
                if complete[set.name.index(node)] == False:
                    if ('localhost:16000/%s' % image) in subprocess.check_output(['docker exec mn.%s docker image ls' % node],shell=True):
                        print ('Docker pull successful for mn.%s' % node)
                        sum = sum + 1
                        complete[set.name.index(node)] = True
                        bar_download.next()
                    else:
                        if not ('localhost:16000/%s' % image) in subprocess.check_output(['docker exec mn.%s sh -c "ps -a"' % node],shell=True):
                            subprocess.call(['docker exec mn.%s sh -c "(docker pull localhost:16000/%s && date +"%%Y-%%m-%%dT%%T.%%6N" > times/%s_%s_end.txt)"&' % (node, image, node, i)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                            print ('Docker pull restarted for mn.%s' % node)
            time.sleep(1)
        bar_download.finish()
        print 'Download(s) successful'

        #grab data
        print 'Grabbing data after download(s)'
        for node in set.name:
            subprocess.call(['docker cp mn.%s:times/%s_%s_start.txt measurements/%s/%s/%s/time/%s_start.txt' % (node, node, i, currentInstance, currentTest, i, node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker cp mn.%s:times/%s_%s_end.txt measurements/%s/%s/%s/time/%s_end.txt' % (node, node, i, currentInstance, currentTest, i, node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(["docker exec mn.%s sh -c 'iptables -L INPUT -n -v -x > tmp_IN.txt'" % node ],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker cp mn.%s:tmp_IN.txt measurements/%s/%s/%s/traffic/%s_IN.txt' % (node, currentInstance, currentTest, i, node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(["docker exec mn.%s sh -c 'iptables -L OUTPUT -n -v -x > tmp_OUT.txt'" % node ],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker cp mn.%s:tmp_OUT.txt measurements/%s/%s/%s/traffic/%s_OUT.txt' % (node, currentInstance, currentTest, i, node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

        #in case of outage restarted
        #if outage == True:
            #for i in range(int(oNr)):
                #subprocess.call(['docker exec mn.%s sh -c "source /etc/kraken/agent_param.sh && export AGENT_REGISTRY_PORT AGENT_PEER_PORT AGENT_SERVER_PORT && export IP=%s && docker-compose -f stack_server.yml up -d"' % (set.servers[i], set.ip[set.name.index(node)])],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)

    set.measureTime(False, currentInstance, currentTest, iteration)
    set.measureTraffic(False, currentInstance, currentTest, iteration)
    #set.measureTime(image, False, currentInstance, currentTest, iteration)
    #set.measureTraffic(image, False, currentInstance, currentTest, iteration)

with open('measurements/currentInstance.txt','r+') as current:
    lines = current.readlines()
    currentInstance = str(lines[-1])

set.readNodes()
currentTest = datetime.strftime(datetime.now(),'%Y%m%d%H%M')
print currentTest
subprocess.call(['mkdir measurements/%s/%s/' % (currentInstance, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
subprocess.call(['mkdir measurements/%s/%s/results/' % (currentInstance, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

testImage = raw_input("Please enter image: ")
serverOutage = set.chooseBoolean()
outageNr = 0
outageTime = 0
if serverOutage == True:
    outageNr = raw_input("Please enter number of servers to be shut down (max. %s): " % len(set.servers))
    outageNr = outageNr.strip()
    outageTime = raw_input("Please enter time in seconds when server(s) shut(s) down: ")
    outageTime = outageTime.strip()

download(testImage, set.testIterations(), serverOutage, outageNr, outageTime)

print ('Output in: measurements/%s/%s/' % (currentInstance, currentTest))

#os.path.getctime(path)
#print set.name
#print ip
