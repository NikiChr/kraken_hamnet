#!/bin/bash

set -ex

source /herd_param.sh

# Start kraken herd.
docker run -d \
    -p ${TESTFS_PORT}:${TESTFS_PORT} \
    -p ${ORIGIN_SERVER_PORT}:${ORIGIN_SERVER_PORT} \
    -p ${ORIGIN_PEER_PORT}:${ORIGIN_PEER_PORT} \
    -p ${TRACKER_PORT}:${TRACKER_PORT} \
    -p ${BUILD_INDEX_PORT}:${BUILD_INDEX_PORT} \
    -p ${PROXY_PORT}:${PROXY_PORT} \
    -p ${PROXY_SERVER_PORT}:${PROXY_SERVER_PORT} \
    -v /etc/kraken/config/origin/development.yaml:/etc/kraken/config/origin/development.yaml \
    -v /etc/kraken/config/tracker/development.yaml:/etc/kraken/config/tracker/development.yaml \
    -v /etc/kraken/config/build-index/development.yaml:/etc/kraken/config/build-index/development.yaml \
    -v /etc/kraken/config/proxy/development.yaml:/etc/kraken/config/proxy/development.yaml \
    -v /herd_param.sh:/herd_param.sh \
    -v /herd_start_processes.sh:/herd_start_processes.sh \
    --name kraken-herd \
    nikitach/kraken-herd:v0.1.3 /herd_start_processes.sh
