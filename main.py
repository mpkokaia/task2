from pymongo import Connection
connection = Connection()
db = connection.urfu
class Cluster:
    def __init__(self,UsefullUsers):
        self.UsefullUsers=UsefullUsers

    def socialActive(self,min_count_unik_fr, max_count_unik_fr):
        inp = open('myData.txt')
        socialActive = inp.readlines()
        inp.close()
        return socialActive

    def get_hubs(self,Users):
        hub={}
        for user in Users:
            value=[]
            for i,cluster in enumerate(Users[user]):
                if cluster>0:
                    value.append(i)
            if len(value)>1:   
                hub[user]=value[:]
        return hub

    def claster_students(self,Clusters):
        iterFlag=True
        while(iterFlag):
            iterFlag=False
            UsefullUsers={}
            UseUsers=[j for i in Clusters for j in i]
            students= db.users.distinct('vkid')
    
            for student in students:
                value=[]
                if str(student) in UseUsers:
                    continue
                test=db.users.find({'vkid':student}).distinct('friends_get.user_id')
                if len(test)<20:                       
                    continue
                for Cluster in Clusters:
                    app=0
                    for t in test:    
                        if str(t) in Cluster:
                           app+=1
                    value.append(app)
                if sum(value)>1:
                    UsefullUsers[student] = value[:]            

            for user in UsefullUsers:
                all_info=sum(UsefullUsers[user])
                this_cluster=False                         #index
                this_cluster_max=0

                other_clusters=False
                for i,cluster in enumerate(UsefullUsers[user]):
                    if cluster>this_cluster_max:
                         if 100*this_cluster_max/all_info>10:
                             other_clusters=True                         
                         this_cluster_max=cluster
                         this_cluster=i
                    elif 100*cluster/all_info>10:
                       other_clusters=True
                if other_clusters==False and this_cluster!=False:
                    if 100*this_cluster_max/all_info>50:
                        Clusters[this_cluster].append(str(user))
                        iterFlag=True
            if iterFlag==False:
                rClusters=[]
                for Cluster in Clusters:
                    if len(Cluster)>50:
                        rClusters.append(Cluster)
                    else:
                        iterFlag=True
                Clusters= rClusters[:]  
        hubs=self.get_hubs(UsefullUsers)
        f = open ('hub.txt','w')
        for hub in hubs:
            f.write(str(hub)+':'+','.join([str(i) for i in hubs[hub]]))
            f.write('\n')
        f.close()
        return Clusters

    def get_ActivePeople(self,min_soc,max_soc):
        socialActive = self.socialActive(min_soc,max_soc)
        ActivePeople={}
        NoActivePeople=[]

        for i in range(len(socialActive)-1):
            test1_all=socialActive[i].split(",")
            if test1_all[0] in NoActivePeople:
                continue
            for j in range(i+1,len(socialActive)):
                count=0
                percent1=0
                percent2=0
                test2_all=socialActive[j].split(",")
                for k in test1_all[1:]:
                    if k in test2_all:
                        count+=1
                percent1=100*count/(len(test1_all)-1)
                percent2=100*count/(len(test2_all)-1)
                if percent1>=10:
                    NoActivePeople.append(test1_all[0])
                    continue
                if percent2>=10:
                    NoActivePeople.append(test2_all[0])
            ActivePeople[test1_all[0]]=test1_all[1:]

        test=socialActive[-1].split(",")
        ActivePeople[test[0]]=test1_all[1:]
        return ActivePeople

    def initial_clusters(self,ActivePeople):
        Clusters=[]

        for people in ActivePeople:
            Cluster=[]
            Cluster.append(people)
            for p in ActivePeople[people]:
                Cluster.append(p)
            Clusters.append(Cluster[:])
        return Clusters

UsefullUsers=[]
cl=Cluster(UsefullUsers)
ActivePeople=cl.get_ActivePeople(50,10000)
Clusters=cl.initial_clusters(ActivePeople)
Clusters=cl.claster_students(Clusters)
print 'Clusters len ' + str(len(Clusters))
f = open ('Clusters.txt','w')
for Cluster in Clusters:
    f.write(str(Cluster[0])+':'+','.join([str(i) for i in Cluster[1:]]))
    f.write('\n')
f.close()
