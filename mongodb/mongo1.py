'''
Created on 1/10/2014

@author: aurelio
'''

from pymongo import MongoClient as mc
from datetime import datetime
from bson.son import SON
from bson.code import Code
from pymongo.son_manipulator import SONManipulator
#from bson.binary import Binary

import gridfs

"""
Following not really needed
def to_binary(custom):
   return Binary(str(custom.x()), 128)

def from_binary(binary):
   return Custom(int(binary))

class Custom(object):
   def __init__(self, x):
     self.__x = x

   def x(self):
     return self.__x


class TransformToBinary(SONManipulator):
    def transform_incoming(self, son, collection):
        for (key, value) in son.items():
            if isinstance(value, Custom):
                son[key] = to_binary(value)
            elif isinstance(value, dict):
                son[key] = self.transform_incoming(value, collection)
        return son

    def transform_outgoing(self, son, collection):
        for (key, value) in son.items():
            if isinstance(value, Binary) and value.subtype == 128:
                son[key] = from_binary(value)
            elif isinstance(value, dict):
                son[key] = self.transform_outgoing(value, collection)
        return son

"""
#client = mc()
client = mc('agm2.local', 27017)

mydb = client.tutorial
up = mydb.topics
"""
# following is for insertion of new records
topics = {"author": "Duke",
           "title" : "PyMongo 101",
           "tags" : ["MongoDB", "PyMongo", "Tutorial"],
           "date" : datetime.utcnow()
          }

up_id = up.insert(topics)

new_posts = [{"author": "Mike",
               "text": "Another post!",
               "tags": ["bulk", "insert"],
               "date": datetime.utcnow()},
              {"author": "Eliot",
               "title": "MongoDB is fun",
               "text": "and pretty easy too!",
               "date": datetime.utcnow()}]
up_id = up.insert(new_posts)
"""
print((up.find_one()))
print((up.find_one({"author": "Mike"})))

# aggregation
db = mc().test

"""
# for insertion
db.things.insert({"x": 1, "tags": ["dog", "cat"]})
db.things.insert({"x": 2, "tags": ["cat"]})
db.things.insert({"x": 3, "tags": []})
"""
aggr = db.things.aggregate([
         {"$unwind": "$tags"},
         {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
         {"$sort": SON([("count", -1), ("_id", -1)])}
     ])
print(("Aggregation: ", aggr))

#map/reduce
mapper = Code("""
               function () {
                 this.tags.forEach(function(z) {
                   emit(z, 1);
                 });
               }
               """)
reducer = Code("""
                function (key, values) {
                  var total = 0;
                  for (var i = 0; i < values.length; i++) {
                    total += values[i];
                  }
                  return total;
                }
                """)
result = db.things.map_reduce(mapper, reducer, "results")
for doc in result.find():
    print(doc)

#with a filter:
result = db.things.map_reduce(mapper, reducer, "results", query={"x": {"$lt": 4}})
for doc in result.find():
    print(("count lower than 5: ", doc))
    
# gridfs
db = mc().gridfs_example
fs = gridfs.GridFS(db)
a = fs.put("hello world".encode("UTF-8"))
fs.get(a).read()

b = fs.put(fs.get(a), filename="foo", bar="baz")
out = fs.get(b)
print(out)
print((out.read().decode()))
print((out.filename))
print((out.bar))
print((out.upload_date))

