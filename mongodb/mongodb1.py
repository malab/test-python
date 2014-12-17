'''
Created on 1/10/2014

@author: aurelio
'''

from pymongo import MongoClient as mc

client = mc()
#client = client = mc('localhost', 12345)
mydb = client.test_database


if __name__ == '__main__':
    pass