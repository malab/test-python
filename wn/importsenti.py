'''
Created on 13/10/2014

@author: aurelio
'''
import mysql.connector as my
import re
import json

con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)
cur = con.cursor()

file = "/home/aurelio/desarrollo/python/agiria/sentiment/sentiwordnet/new_sentiwn.csv"

def saveRecord(pal, offset, synset, pos, neg):
    t = "insert into senti_new (pal, offset, synset, pos, neg) values (%s, %s, %s, %s,%s);"
    try:
        cur.execute(t, (pal, offset, synset, pos, neg))
    except my.Error as err:
        print("ERROR - ", err, t)
    

with open(file, 'rt') as f:
    lines = f.readlines()
    for line in lines:
        dat2 = line.split(',')
        dato = [x for x in dat2 if x][:-1]
        num = (len(dato)-4)/2
        if num > 1:
            pass
        offset = dato[1]
        pos =  dato[0]
        ps = float(dato[2])
        ng = float(dato[3])
        for a in range(0, int(num*2), 2):
            rec = a + 4
            pal = dato[rec]
            pal = pal.replace('\047', '\134\047')
            try:
                synset = dato[rec] + "." + pos + '.' + str(dato[rec+1].rjust(2, '0'))
                #print(pal, offset, synset, ps, ng)
                saveRecord(pal, offset, synset, ps, ng)
            except:
                print("error - ", pal, offset, ps, ng )
            # saveRecord(pal, offset, synset, ps, ng)
    
    
pass
    