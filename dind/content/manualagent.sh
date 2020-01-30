#!/bin/bash
docker run -it --privileged -p 16000:16000 -p 16001:16001 -p 16002:16002 -v /etc/kraken/config/agent/base.yaml:/etc/kraken/config/agent/base.yaml -v /etc/kraken/config/agent/development.yaml:/etc/kraken/config/agent/development.yaml  172.17.0.1:5000/kraken-agent /bin/bash
