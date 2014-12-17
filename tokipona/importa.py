import mysql.connector as my
from pprint import pprint
import re


con_data = {'user':'root','password':'agm','host':'localhost', \
'database':'tokipona','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)

fname = '/home/aurelio/linguistics/tokipona_sentences_es2.csv'

def saveRecord(dic):
    cur = con.cursor()
    tk = dic['tk']
    for k,v in dic.items():
        if k == 'tk':
            tk = v
        else:
            
            for cada in v:
                cada = cada.replace("'", "\\'")
                vals = (tk, cada)
                try:
                    t = "Insert into tk_sents (tk, esp) values ('%s', '%s');" % (vals)
                    cur.execute(t)
                except my.Error as err:
                    print("Error insertando ", err, t)
                              
        

with open(fname, 'rt') as file:
    lines = file.readlines()
    for line in lines:
        line = line[:-1]
        line = line.split('=')
        datos = [x.split(',') for x in line]
        datos = [item for sublist in datos for item in sublist]
        dic = {}
        dic['tk'] = datos[0].strip()
        dic['esp'] = []
        for i in range(len(datos)):
            if i > 0 and datos[i].strip():
                    dic['esp'].append(datos[i].strip())
        """
        for k, v in dic.items():
            print(k, v)
        """
        if dic:
            saveRecord(dic)



