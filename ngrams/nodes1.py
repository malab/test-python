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
        pal, pos, parse, freq = fila
        prob = round(100 * freq / total, 6)
        guarda(con, cur3,  pal, pos, parse, freq, prob)
        

def guarda(con, cur3, pal, pos, parse, freq, prob):
    # print(pal1, pal2, year)
    # datos vienen en bytes. Pasar a unicode
    pal = pal.decode('utf-8')
    pos = pos.decode('utf-8')
    parse = parse.decode('utf-8')
    # escapar comillas
    pal = pal.replace('"', '\\"')
    pal = pal.replace("'", "\\'")
    if pal == '"':
        pal = '\\"'
    if pal == "''":
        pal = "\\'\\'"
    if pal == "'":
        pal = "\\'"
    # calcula len para ver si hay chars extraños que anulen la query
    pal3 = pal.encode('utf-8')
    if len(pal) == len(pal3):
        t = "update nodes set prob = %s where pal = '%s' and pos = '%s' and parse = '%s'" % (prob, pal, pos, parse)
        try:
            cur3.execute(t)
        except (my.Error) as err:
            print(("ERROR:",t, err))

        
    '''
    else:
        print("error en decoding caracteres extraños")
    '''
def main(con_data):
    con = my.connect(**con_data)
    # continua = True
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()
    cur4 = con.cursor()
    t = "select pal from nodes group by pal;"
    try:
        cur.execute(t)
    except:
        print("Error en primera seleccion")
    rows = cur.fetchall()
    for row in rows:
        try:
            pal = row[0].decode('utf-8')
        except:
            pal = ''
        if pal:
            if pal == "'":
                pal = "\\'"
            if pal == '"':
                pal = '\\"'
            if pal == "''":
                pal = "\'\'"
            t = "select sum(freq) from nodes where pal = \"%s\" and parse regexp '[A-Za-z]+$';" % pal
            cur2.execute(t)
            total_pal = cur2.fetchone()
            if total_pal[0]:
                total = int(total_pal[0])
                t = "select pal, pos, parse, freq from nodes where pal = \"%s\";" % pal
                # print(t)
                cur2.execute(t)
                filas = cur2.fetchall()
                if cur2.rowcount > 0:
                    fila_unica(con, cur3, filas, total)

        
    
if __name__ == "__main__":
    main(con_data)
    
    ''