from pymongo import Connection

connection = Connection()
db = connection.urfu
nodelist = []
students = db.users.distinct('vkid')
f = open('myData.txt', 'w')

count = []
for student in students:
    unik_fr = db.users.find({'friends_get.user_id': student}).distinct('vkid')
    if len(unik_fr) > 50:
        unik_fr.insert(0, student)
        f.write(','.join([str(i) for i in unik_fr]))
        f.write('\n')
f.close()
