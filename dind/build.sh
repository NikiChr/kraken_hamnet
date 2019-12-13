#!/bin/bash
docker pull registry:2.6
docker tag registry:2.6 172.17.0.1:5000/registry
docker push 172.17.0.1:5000/registry

docker pull nikitach/kraken-agent:v0.1.3
docker tag nikitach/kraken-agent:v0.1.3 172.17.0.1:5000/kraken-agent
docker push 172.17.0.1:5000/kraken-agent

docker pull nikitach/kraken-herd:v0.1.3
docker tag nikitach/kraken-herd:v0.1.3 172.17.0.1:5000/kraken-herd
docker push 172.17.0.1:5000/kraken-herd

docker build -t kraken_stage1 .
docker run --privileged -d --name kraken_build kraken_stage1
sleep 10
docker exec kraken_build docker-compose up --no-start
sleep 10
docker stop kraken_build
docker commit kraken_build kraken_dind
docker rm kraken_build
echo '***Image kraken_dind erstellt!'

#docker build -t kraken_dind .
