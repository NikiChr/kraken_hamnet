from datetime import datetime
from progress.bar import Bar, IncrementalBar
import subprocess
import time

size = raw_input("Please enter total image size in MB: ")
layerNr = raw_input("Please enter number of layers: ")
testNr = raw_input("Please enter number of images: ")

subprocess.call(['mkdir -p images/%simages_%smb_%slayers/' % (testNr, size, layerNr)],shell=True)
subprocess.call(['mkdir -p images/%simages_%smb_%slayers/images/' % (testNr, size, layerNr)],shell=True)
setup = open('images/%simages_%smb_%slayers/setup.txt' % (testNr, size, layerNr),'w+')
setup.write('Number of test images: %s\nTotal size of each test image: %sMB\nLayers per image:%s\nDate of creation:%s' %(testNr,size,layerNr,datetime.now()))
setup.close()

for i in range(int(testNr)):
    subprocess.call(['mkdir -p images/%simages_%smb_%slayers/%s/' % (testNr, size, layerNr, i)],shell=True)
    image = open('images/%simages_%smb_%slayers/%s/Dockerfile' % (testNr, size, layerNr, i),'w+')
    image.write('FROM scratch\n')
    for j in range(int(layerNr)):
        subprocess.call(['dd if=/dev/urandom of=images/%simages_%smb_%slayers/%s/%s.txt bs=1048576 count=%s ' % (testNr, size, layerNr, i, j, str(int(size)/int(layerNr)))],shell=True)
        image.write('COPY images/%simages_%smb_%slayers/%s/%s.txt /\n' % (testNr, size, layerNr, i, j) )
    image.close()
    subprocess.call(['docker build -f images/%simages_%smb_%slayers/%s/Dockerfile -t %stest%smb%s .' % (testNr, size, layerNr, i, i, size, layerNr)],shell=True)
    subprocess.call(['docker save -o images/%simages_%smb_%slayers/images/%stest%smb%s.tar %stest%smb%s' % (testNr, size, layerNr, i, size, layerNr, i, size, layerNr)],shell=True)
    subprocess.call(['docker image rm %stest%smb%s' % (i, size, layerNr)],shell=True)
