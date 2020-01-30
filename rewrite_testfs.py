import settings as set
import subprocess

def serverList(spaces,port=''): #Immer mit :
    serverString = ''
    for node in set.servers:
        serverString = serverString + '%s- %s%s\n' % (spaces,set.ip[set.name.index(node)],port)
    return serverString

def allowed_cidrs(node):
    subprocess.call(["docker exec -it mn.%s sh -c 'ifconfig | grep -A 1 %s > %s_interfaces.txt'" % (node, node, node) ],shell=True)
    subprocess.call(["docker cp mn.%s:%s_interfaces.txt ./interfaces/%s_interfaces.txt" % (node, node, node) ],shell=True)
    cidrs = ''
    with open('./interfaces/%s_interfaces.txt' % (node)) as input:
        lines = input.readlines()
        for line in lines:
            if node == line[:len(node)]:
                tmp = lines[lines.index(line)+1]
                tmp = tmp.split()
                tmp = tmp[1]
                tmp = tmp[5:]
                cidrs = cidrs + '  - %s\n' % tmp
    #print cidrs
    return cidrs

def agent_param(node):
    doc = open('tmp/agent_param.sh', 'w+')
    doc.write('AGENT_REGISTRY_PORT="16000"\nAGENT_PEER_PORT="16001"\nAGENT_SERVER_PORT="16002"\nHOSTNAME=%s\nAGENT_CONTAINER_NAME=kraken_agent' % set.ip[set.name.index(node)] )
    doc.close()

def herd_param(node):
    doc = open('tmp/herd_param.sh', 'w+')
    doc.write('TESTFS_PORT=14000\nREDIS_PORT=14001\n\nPROXY_PORT=15000\nORIGIN_PEER_PORT=15001\nORIGIN_SERVER_PORT=15002\nTRACKER_PORT=15003\nBUILD_INDEX_PORT=15004\nPROXY_SERVER_PORT=15005\n\nHOSTNAME=%s' % set.ip[set.name.index(node)] )
    doc.close()

def agent_development(node):
    agent_doc = open('tmp/config/agent/development.yaml', 'w+')
    agent_doc.write('extends: base.yaml\n\ntracker:\n  hosts:\n    static:\n%s\n\nbuild_index:\n  hosts:\n    static:\n%s\n\nallowed_cidrs:\n  - 127.0.0.1\n  - 172.17.0.0/8\n  - 172.18.0.1\n  - 172.19.0.1\n  - 44.0.0.0/8\ntls:\n  name: kraken\n  cas:\n  - path: /etc/kraken/tls/ca/server.crt\n  server:\n    disabled: true\n    cert:\n      path: /etc/kraken/tls/ca/server.crt\n    key:\n      path: /etc/kraken/tls/ca/server.key\n    passphrase:\n      path: /etc/kraken/tls/ca/passphrase\n  client:\n    cert:\n      path: /etc/kraken/tls/client/client.crt\n    key:\n      path: /etc/kraken/tls/client/client.key\n    passphrase:\n      path: /etc/kraken/tls/client/passphrase\nstore:\n      cache_cleanup:\n        tti: 10m\n      download_cleanup:\n        tti: 10m' % (serverList('      ',':15003'), serverList('      ',':15004')))
    agent_doc.close()

def agent_base(node):
    agent_doc = open('tmp/config/agent/base.yaml', 'w+')
    agent_doc.write('zap:\n  level: info\n  development: false\n  encoding: console\n  disableStacktrace: true\n  encoderConfig:\n    messageKey: message\n    nameKey: logger_name\n    levelKey: level\n    timeKey: ts\n    callerKey: caller\n    stacktraceKey: stack\n    levelEncoder: capital\n    timeEncoder: iso8601\n    durationEncoder: seconds\n    callerEncoder: short\n  outputPaths:\n    - stdout\n    - /var/log/kraken/kraken-agent/stdout.log\n  errorOutputPaths:\n    - stdout\n    - /var/log/kraken/kraken-agent/stdout.log\n\nmetrics:\n  m3:\n    service: kraken-agent\n\nscheduler:\n  log:\n    timeEncoder: iso8601\n  torrentlog:\n    service_name: kraken-agent\n    path: /var/log/kraken/kraken-agent/torrent.log\n    encoding: json\n    timeEncoder: epoch\n  dispatch:\n    piece_request_policy: rarest_first\n  conn:\n    bandwidth:\n      enable: true\n  seeder_tti: 1m\n\nstore:\n  download_dir: /var/cache/kraken/kraken-agent/download/\n  cache_dir:  /var/cache/kraken/kraken-agent/cache/\n  download_cleanup:\n    ttl: 10m\n  cache_cleanup:\n    ttl: 10m\n\nregistry:\n  docker:\n    version: 0.1\n    log:\n      level: error\n    http:\n      net: unix\n      addr: /tmp/kraken-agent-registry.sock\n\npeer_id_factory: addr_hash\n\nallowed_cidrs:\n  - 127.0.0.1\n  - 172.17.0.0/8\n  - 172.18.0.1\n  - 172.19.0.1\n  - 44.0.0.0/8\n\nnginx:\n  name: kraken-agent\n  cache_dir: /var/cache/kraken/kraken-agent/nginx/\n  log_dir: /var/log/kraken/kraken-agent/\n')
    agent_doc.close()

def build_index_development():
    build_index_doc = open('tmp/config/build-index/development.yaml', 'w+')
    build_index_doc.write('extends: base.yaml\n\nbackends:\n  - namespace: test/.*\n    backend:\n      registry_tag:\n        address: localhost:5001\n  - namespace: .*\n    backend:\n      testfs:\n        address: localhost:14000\n        root: tags\n        name_path: docker_tag\n  - namespace: library/.*\n    backend:\n      registry_tag:\n        address: index.docker.io\n        security:\n          basic:\n            username: ""\n            password: ""\n\ncluster:\n  hosts:\n    static:\n%s\n\norigin:\n  hosts:\n    static:\n%s\n\nremotes: {}\n\ntag_replication:\n  retry_interval: 100ms\n  poll_retries_interval: 250ms\n\ntag_types:\n  - namespace: .*\n    type: docker\n    root: tags\n\ntag_store:\n  write_through: false\n\nwriteback:\n  retry_interval: 100ms\n  poll_retries_interval: 250ms\n\nnginx:\n  cache_dir: /tmp/kraken-build-index-nginx/\ntls:\n  name: kraken\n  cas:\n  - path: /etc/kraken/tls/ca/server.crt\n  server:\n    disabled: true\n    cert:\n      path: /etc/kraken/tls/ca/server.crt\n    key:\n      path: /etc/kraken/tls/ca/server.key\n    passphrase:\n      path: /etc/kraken/tls/ca/passphrase\n  client:\n    cert:\n      path: /etc/kraken/tls/client/client.crt\n    key:\n      path: /etc/kraken/tls/client/client.key\n    passphrase:\n      path: /etc/kraken/tls/client/passphrase' % (serverList('      ',':15004'),serverList('      ',':15002')))
    build_index_doc.close()

def origin_development():
    origin_doc = open('tmp/config/origin/development.yaml', 'w+')
    origin_doc.write('extends: base.yaml\n\nbackends:\n  - namespace: test/.*\n    backend:\n      registry_blob:\n        address: localhost:5001\n        security:\n          tls:\n            client:\n              disabled: true\n  - namespace: .*\n    backend:\n      testfs:\n        address: localhost:14000\n        root: blobs\n        name_path: identity\n  - namespace: library/.*\n    backend:\n      registry_blob:\n        address: index.docker.io\n        security:\n          basic:\n            username: ""\n            password: ""      \n\ncluster:\n  static:\n%s\n\nhashring:\n  max_replica: 20\n\nwriteback:\n  retry_interval: 100ms\n  poll_retries_interval: 250ms\n\ntls:\n  name: kraken\n  cas:\n  - path: /etc/kraken/tls/ca/server.crt\n  server:\n    disabled: true\n    cert:\n      path: /etc/kraken/tls/ca/server.crt\n    key:\n      path: /etc/kraken/tls/ca/server.key\n    passphrase:\n      path: /etc/kraken/tls/ca/passphrase\n  client:\n    cert:\n      path: /etc/kraken/tls/client/client.crt\n    key:\n      path: /etc/kraken/tls/client/client.key\n    passphrase:\n      path: /etc/kraken/tls/client/passphrase\nstore:\n      cache_cleanup:\n        tti: 10m\n      download_cleanup:\n        tti: 10m' % (serverList('    ',':15002')))
    origin_doc.close()

def proxy_development():
    proxy_doc = open('tmp/config/proxy/development.yaml', 'w+')
    proxy_doc.write('extends: base.yaml\n\norigin:\n  hosts:\n    static:\n%s\n\nbuild_index:\n  hosts:\n    static:\n%s\n\nnginx:\n  cache_dir: /tmp/kraken-proxy-nginx/\n\ntls:\n  name: kraken\n  cas:\n  - path: /etc/kraken/tls/ca/server.crt\n  server:\n    disabled: true\n    cert:\n      path: /etc/kraken/tls/ca/server.crt\n    key:\n      path: /etc/kraken/tls/ca/server.key\n    passphrase:\n      path: /etc/kraken/tls/ca/passphrase\n  client:\n    cert:\n      path: /etc/kraken/tls/client/client.crt\n    key:\n      path: /etc/kraken/tls/client/client.key\n    passphrase:\n      path: /etc/kraken/tls/client/passphrase' % (serverList('      ',':15002'),serverList('      ',':15004')))
    proxy_doc.close()

def tracker_development():
    tracker_doc = open('tmp/config/tracker/development.yaml', 'w+')
    tracker_doc.write('extends: base.yaml\n\npeerstore:\n  redis:\n    peer_set_window_size: 1h\n    max_peer_set_windows: 5\n    addr: 127.0.0.1:14001\n\norigin:\n  hosts:\n    static:\n%s\n\ntrackerserver:\n  announce_interval: 3s\n\nnginx:\n  cache_dir: /tmp/kraken-tracker-nginx/\n\ntls:\n  name: kraken\n  cas:\n  - path: /etc/kraken/tls/ca/server.crt\n  server:\n    disabled: true\n    cert:\n      path: /etc/kraken/tls/ca/server.crt\n    key:\n      path: /etc/kraken/tls/ca/server.key\n    passphrase:\n      path: /etc/kraken/tls/ca/passphrase\n  client:\n    cert:\n      path: /etc/kraken/tls/client/client.crt\n    key:\n      path: /etc/kraken/tls/client/client.key\n    passphrase:\n      path: /etc/kraken/tls/client/passphrase' % (serverList('      ',':15002')))
    tracker_doc.close()

def rewriteConfig(node):
    agent_development(node)
    agent_base(node)
    build_index_development()
    origin_development()
    proxy_development()
    tracker_development()
