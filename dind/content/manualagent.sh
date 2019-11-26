#!/bin/bash
docker run -it --privileged -p 16000:16000 -p 16001:16001 -p 16002:16002 -v /etc/kraken/config/agent/base.yaml:/etc/kraken/config/agent/base.yaml -v /etc/kraken/config/agent/development.yaml:/etc/kraken/config/agent/development.yaml  172.17.0.1:5000/kraken-agent /bin/bash
 

 
#/usr/bin/kraken-agent --config=/etc/kraken/config/agent/development.yaml --peer-ip=44.44.12.2 --peer-port=16001 --agent-server-port=16002 --agent-registry-port=16000
