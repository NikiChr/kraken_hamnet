import settings as set

set.readNodes()
edgelist = [[],[]]

with open(set.edgelist) as current:
    lines = current.readlines()
    for line in lines:
        tmp = line.split()
        edgelist[lines.index(line)][0].append(tmp[0])
        edgelist[lines.index(line)][1].append(tmp[1])
    print edgelist