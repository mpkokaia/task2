import warnings
import pygraphviz as pgv

from pymongo import Connection
connection = Connection()
db = connection.urfu

warnings.simplefilter('ignore', RuntimeWarning)

A=pgv.AGraph(layout='fdp',overlap = False, splines = True)

f = open('Clusters.txt')
data_Clusters = f.readlines() 
f.close()
Cluster=[]
for line in data_Clusters:
    data = line.split(':')
    if len(data)==2:
        users = data[1].split(',')
        fname = db.users.find_one({'vkid':int(data[0])},{'_id':0, 'users_get.last_name':1})['users_get']['last_name']
        Cluster.append(unicode(fname))
A.add_nodes_from(Cluster,color='red')
f = open('hub.txt')
data_hubs = f.readlines() 
f.close()
hubs={}
for line in data_hubs:
    line=line.strip()
    data = line.split(':')    
    users = data[1].split(',')
    hubs[data[0]]=users[:]
all_hubs={}
edges=[]
for en,h in enumerate(hubs):
    for i in range(len(hubs[h])-1):
        for j in range(i+1,len(hubs[h])):
            if (hubs[h][i], hubs[h][j]) not in edges:
                if (hubs[h][j], hubs[h][i]) not in edges:
                    edges.append((Cluster[int(hubs[h][i])], Cluster[int(hubs[h][j])]))
for edg in edges:
    A.add_edge(unicode(edg[0]),unicode(edg[1]))
A.draw('2Dgraph.png',prog='dot')
