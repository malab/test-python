'''
Created on 24/10/2014

@author: aurelio
'''
import mysql.connector as my
import sys

con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)

anton = '/home/aurelio/Documentos/antonyms.txt'

lin = 0
dic = {}

def creaDict(orig, ants):
    for cada in orig:
        for a in ants:
            dic[cada] = a

def saveRecord(pal, anton):
    pal = pal.split('#')
    pal1 = pal[0]
    pos1 = pal[1][:1]
    sense1 = str(int(pal[1][1:])).rjust(2, '0')
    if int(sense1) > 99:
        sense1 = '00'
    anton = anton.split('#')
    pal2 = anton[0]
    pos2 = anton[1][:1]
    sense2 = str(int(anton[1][1:])).rjust(2, '0')
    if int(sense2) > 99:
        sense2 = '00'
    cur = con.cursor()
    t = "Insert ignore into wn_antonyms (pal,pos1, sense1, anton, pos2, sense2) \
    values (%s, %s, %s, %s, %s, %s);"
    values = (pal1, pos1, sense1, pal2, pos2, sense2)
    try:
        cur.execute(t, values)
    except my.Error as err:
        print("ERROR:", err, t, values)
            
with open(anton, 'rt') as file:
    orig = []
    ants = []
    ant = []
    lines = file.readlines()
    for line in lines:
        line = line[:-1]
        lin +=1
        if not line[0] == "\t":
            orig = []
            pals = line.split(',')
            for pal in pals:
                orig.append(pal)
            ants = []
        else:
            pals = line[1:].split(',')
            for pal in pals:
                ants.append(pal)
        if line.startswith("\t"):
            creaDict(orig, ants)
            # print(orig, ":", ants)   
for k, v in sorted(dic.items()):
    saveRecord(k,v)     
             
    
            