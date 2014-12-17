#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 05/12/2013

@author: aurelio
'''


import mysql.connector as my

con_data = {'user':'root','password':'agm','host':'localhost', \
            'database':'ngrams','raise_on_warnings': True, 'autocommit':True, 'buffered':True}



def fila_unica(con, cur3, filas, total):
    for fila in filas:
        pal1, pal2, year,freq = fila
        prob = round(100 * freq / total, 6)
        guarda(con, cur3,  pal1, pal2, year, freq, prob)
        

def guarda(con, cur3, pal1, pal2, year, freq, prob):
    # print(pal1, pal2, year)
    # datos vienen en bytes. Pasar a unicode
    pal1 = pal1.decode('utf-8')
    pal2 = pal2.decode('utf-8')
    # escapar comillas
    pal1 = pal1.replace('"', '\\"')
    pal2 = pal2.replace('"', '\\"')
    pal1 = pal1.replace("'", "\\'")
    pal2 = pal2.replace("'", "\\'")
    if pal1 == '"':
        pal1 = '\\"'
    if pal2 == '"':
        pal2 = '\\"'
    if pal1 == "''":
        pal1 = "\\'\\'"
    if pal2 == "''":
        pal2 = "\\'\\'"
    if pal1 == "'":
        pal1 = "\\'"
    if pal2 == "'":
        pal2 = "\\'"
    # calcula len para ver si hay chars extraños que anulen la query
    pal3 = pal1.encode('utf-8')
    pal4 = pal2.encode('utf-8')
    if len(pal1) == len(pal3) and len(pal2) == len(pal4):
        t = "insert ignore into 1ngram2 (pal1, pal2, year, freq, prob_pal2) values (\"%s\", \"%s\", %s, %s, %s)" % (pal1, pal2, year, freq, prob)
        try:
            cur3.execute(t)
        except (my.Error, my.connection.errors) as err:
            print(("ERROR:",t, err))

        
    '''
    else:
        print("error en decoding caracteres extraños")
    '''
def main(con_data):
    con = my.connect(**con_data)
    continua = True
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    pal = ""
    while continua == True:
        t = "Select pal1 from x1ngram2 where pal1 > \"%s\" and pal2 REGEXP '^_[A-Z]{3,6}_$' limit 1;" % pal
        try:
            cur.execute(t)
        except my.Error as err:
            print((t, err))
        row = cur.fetchone()
        pal = row[0].decode('utf-8')
        if pal == "'":
            pal = "\\'"
        if pal == '"':
            pal = '\\"'
        if pal == "''":
            pal = "\'\'"
        t = "select sum(freq) from x1ngram2 where pal1 = \"%s\" and pal2 REGEXP '^_[A-Z]{3,6}_$';" % pal
        cur2.execute(t)
        total_pal = cur2.fetchone()
        t = "select pal1, pal2, year, freq from x1ngram2 where pal1 = \"%s\" and pal2 REGEXP '^_[A-Z]{3,6}_$';" % pal
        # print(t)
        cur2.execute(t)
        filas = cur2.fetchall()
        if cur2.rowcount > 0:
            fila_unica(con, cur3, filas, total_pal[0])
        '''
        else:
            continua = False
        '''
        
    
if __name__ == "__main__":
    main(con_data)
    
    ''