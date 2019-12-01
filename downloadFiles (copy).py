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

def downloadImage(image, iterations, outage = False, oNr = 0, oTime = 0):
    FNULL = open(os.devnull, 'w')

    image = image.strip()

    for iteration in range(int(iterations)):
        print ('\n###\nTest #%s\n###' % (iteration + 1))

        checkKrakenContainer()
        subprocess.call(['mkdir measurements/%s/%s/%s/' % (currentInstance,currentTest,iteration)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
        subprocess.call(['mkdir measurements/%s/%s/%s/time/' % (currentInstance,currentTest,iteration)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
        subprocess.call(['mkdir measurements/%s/%s/%s/traffic/' % (currentInstance,currentTest,iteration)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

        #delete existing image and log files on hosts
        sum = 0
        deleted = [False] * len(set.name)
        print ('Waiting for torrents to clean up')
        time.sleep(300)
        bar1 = IncrementalBar('Deleting existing log files ', max = len(set.name))
        #subprocess.call(['rm -fR time/*'],stdout=FNULL, stderr=subprocess.STDOUT,shell=True) #root/.small-dragonfly/logs/*
        for node in set.name:
            if not node in set.seeder:
                #subprocess.call(['docker exec -it mn.%s docker image rm -f %s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                subprocess.call(['docker exec -it mn.%s docker image rm -f localhost:16000/test/%s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            else:
                subprocess.call(['docker exec -it mn.%s docker image rm -f localhost:15000/test/%s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(["docker exec mn.%s sh -c 'iptables -Z'" % node ],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            bar1.next()
        bar1.finish()
        print ('%s deleted on every host\n' % image)

        #Prepare seeder
        sum = 0
        seederPrep = [False] * len(set.seeder)
        bar2 = IncrementalBar('Prepare seeder(s)', max = len(set.seeder))
        for node in set.seeder:
            subprocess.call(['docker exec mn.%s docker pull %s &' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT, shell=True)
        while sum < len(set.seeder):
            for node in set.seeder:
                if seederPrep[set.seeder.index(node)] == False:
                    if image in subprocess.check_output(['docker exec mn.%s docker image ls' % node],shell=True):
                        sum = sum + 1
                        bar2.next()
            time.sleep(1)
        print ('\nPushing %s to registry for sharing' % image)
        for node in set.seeder:
            subprocess.call(['docker exec mn.%s docker tag %s localhost:15000/test/%s' % (node, image, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker exec mn.%s docker push localhost:15000/test/%s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
        bar2.finish()

        #Start download
        sum = 0
        complete = [False] * len(set.name)
        print ('Starting download(s)')
        bar3 = IncrementalBar('Waiting for download(s)', max = len(set.name))
        #doc = open('measurements/%s/%s/%s/time/start.txt' % (currentInstance, currentTest, iteration), 'w+')
        #starttime = str(datetime.strftime(datetime.now(),'%Y-%m-%d')) + 'T' + str(datetime.strptime(datetime.strftime(datetime.now(),'%H:%M:%S.%f'),'%H:%M:%S.%f') - datetime.strptime('1','%H'))
        #print '\n'+starttime
        #print datetime.strftime(starttime,'%Y-%m-%dT%H:%M:%S')
        #doc.write(str(starttime))
        #doc.close()
        for node in set.name:
            subprocess.call(["docker exec mn.%s sh -c 'iptables -Z'" % node ],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            #print node
            if not node in set.seeder:
                #print('docker exec mn.%s sh -c "(date +"%%Y-%%m-%%dT%%T.%%6N" >> times/%s%s_%s_start.txt; docker pull localhost:16000/test/%s > dump.txt; date +"%%Y-%%m-%%dT%%T.%%6N" > times/%s%s_%s_end.txt)"&' % (node, image, iteration, currentTest, image, image, iteration, currentTest))
                subprocess.call(['docker exec mn.%s sh -c "(date +"%%Y-%%m-%%dT%%T.%%6N" >> times/%s%s_%s_start.txt; docker pull localhost:16000/test/%s > dump.txt; date +"%%Y-%%m-%%dT%%T.%%6N" > times/%s%s_%s_end.txt)"&' % (node, image, iteration, currentTest, image, image, iteration, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                #print node
                #subprocess.call(['docker exec mn.%s sh -c "(date +"%%Y-%%m-%%dT%%T.%%6N" >> times/timer_start.txt; docker pull alpine > bullshit.txt; date +"%%Y-%%m-%%dT%%T.%%6N" >> times/timer_end.txt)"&' % (node)],shell=True)
            if node in set.seeder:
                complete[set.name.index(node)] = True
                bar3.next()
                sum = sum + 1

        #Server outage
        if outage == True:
            print ('\nWaiting %s seconds for outage...' % oTime)
            time.sleep(int(oTime))
            for i in range(int(oNr)):
                print set.servers[i]
                subprocess.call(['docker exec mn.%s docker stop kraken_herd &' % (set.servers[i])],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

        while sum < len(set.name):
            #time.sleep(5)
            for node in set.name:
                if complete[set.name.index(node)] == False:
                    if 'localhost:16000/test/%s' % (image) in subprocess.check_output(['docker exec mn.%s docker image ls' % node],shell=True):
                        sum = sum + 1
                        complete[set.name.index(node)] = True
                        bar3.next()
                        #subprocess.call(["docker exec mn.%s sh -c 'docker logs -t --since %s kraken_agent > tmp.txt'" % (node, starttime)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                        #subprocess.call(['docker cp mn.%s:tmp.txt measurements/%s/%s/%s/time/%s.txt' % (node, currentInstance, currentTest, (iteration + 1), node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
                    #else:
                        #if sum/len(set.name) >= 0.9:
                            #subprocess.call(['docker exec mn.%s docker pull localhost:16000/%s &' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            time.sleep(10)
        bar3.finish()
        print '\nDownload(s) successful'

        #grabbing files with times
        for node in set.name:
            #subprocess.call(['docker cp mn.%s:tmp.txt measurements/%s/%s/%s/time/%s.txt' % (node, currentInstance, currentTest, (iteration + 1), node)],stdout=FNULL, stderr=subp
            subprocess.call(['docker cp mn.%s:times/%s%s_%s_start.txt measurements/%s/%s/%s/time/%s_start.txt' % (node, image, iteration, currentTest, currentInstance, currentTest, iteration, node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker cp mn.%s:times/%s%s_%s_end.txt measurements/%s/%s/%s/time/%s_end.txt' % (node, image, iteration, currentTest, currentInstance, currentTest, iteration, node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            #subprocess.call(["docker exec mn.%s sh -c 'docker logs -t --since %s kraken_agent > tmp.txt'" % (node, starttime)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            #subprocess.call(['docker cp mn.%s:tmp.txt measurements/%s/%s/%s/time/%s.txt' % (node, currentInstance, currentTest, (iteration), node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(["docker exec mn.%s sh -c 'iptables -L INPUT -n -v -x > tmp_IN.txt'" % node ],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker cp mn.%s:tmp_IN.txt measurements/%s/%s/%s/traffic/%s_IN.txt' % (node, currentInstance, currentTest, (iteration), node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(["docker exec mn.%s sh -c 'iptables -L OUTPUT -n -v -x > tmp_OUT.txt'" % node ],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker cp mn.%s:tmp_OUT.txt measurements/%s/%s/%s/traffic/%s_OUT.txt' % (node, currentInstance, currentTest, (iteration), node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(["docker exec mn.%s sh -c 'iptables -L FORWARD -n -v -x > tmp_OUT.txt'" % node ],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
            subprocess.call(['docker cp mn.%s:tmp_OUT.txt measurements/%s/%s/%s/traffic/%s_FOR.txt' % (node, currentInstance, currentTest, (iteration), node)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

        if outage == True:
            time.sleep(int(oTime))
            for i in range(int(oNr)):
                subprocess.call(['docker exec mn.%s docker start kraken_herd' % (set.servers[i])],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
    for node in set.name:
        subprocess.call(['docker exec -it mn.%s docker image rm -f localhost:15000/test/%s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
        subprocess.call(['docker exec -it mn.%s docker image rm -f localhost:16000/test/%s' % (node, image)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

    set.measureTime(image, False, currentInstance, currentTest, iterations)
    set.measureTraffic(image, False, currentInstance, currentTest, iterations)

with open('measurements/currentInstance.txt','r+') as current:
    lines = current.readlines()
    currentInstance = str(lines[-1])

set.readNodes()
currentTest = datetime.strftime(datetime.now(),'%Y%m%d%H%M')
print currentTest
subprocess.call(['mkdir measurements/%s/%s/' % (currentInstance, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
subprocess.call(['mkdir measurements/%s/%s/results/' % (currentInstance, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
#subprocess.call(['mkdir measurements/%s/%s/results/time/' % (currentInstance, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
#subprocess.call(['mkdir measurements/%s/%s/0/' % (currentInstance, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
#subprocess.call(['mkdir measurements/%s/%s/0/time/' % (currentInstance, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)
#subprocess.call(['mkdir measurements/%s/%s/torrents/' % (currentInstance, currentTest)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

testImage = raw_input("Please enter image: ")
serverOutage = set.chooseBoolean()
outageNr = 0
outageTime = 0
if serverOutage == True:
    outageNr = raw_input("Please enter number of servers to be shut down (max. %s): " % len(set.servers))
    outageNr = outageNr.strip()
    outageTime = raw_input("Please enter time in seconds when server(s) shut(s) down: ")
    outageTime = outageTime.strip()

for node in set.seeder:
    subprocess.call(['docker exec -it mn.%s docker image rm -f %s' % (node, testImage)],stdout=FNULL, stderr=subprocess.STDOUT,shell=True)

downloadImage(testImage, set.testIterations(), serverOutage, outageNr, outageTime)

print ('Output in: measurements/%s/%s/' % (currentInstance, currentTest))

#os.path.getctime(path)
#print set.name
#print ip
