#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 05/12/2013

@author: aurelio
'''


import mysql.connector as my
import re
con_data = {'user':'root','password':'agm','host':'localhost', \
            'database':'ngrams','raise_on_warnings': True, 'autocommit':True, 'buffered':True}



def fila_unica(con, cur3, filas, total):
    for fila in filas:
        pal, tipo, year, freq = fila
        prob = round(100 * freq / total, 5)
        guarda(con, cur3,  pal, tipo, year, freq, prob)
        

def guarda(con, cur3, pal, tipo, year, freq, prob):
    # print(pal1, pal2, year)
    # datos vienen en bytes. Pasar a unicode
    pal = pal.decode('utf-8')
    tipo = tipo.decode('utf-8')
    # escapar comillas
    pal = pal.replace('"', '\\"')
    pal = pal.replace("'", "\\'")
    pal = re.sub('o\W', 'o', pal)
    pal = pal.replace('\"', '\\"')
    if pal.endswith('"'):
      pal = pal[:-1]
    if pal == '"':
        pal = '\\"'
    if pal == "''":
        pal = "\\'\\'"
    if pal == "'":
        pal = "\\'"
    # calcula len para ver si hay chars extraños que anulen la query
    pal3 = pal.encode('utf-8')
    if len(pal) == len(pal3):
        t = "insert ignore into es_1gram2 (pal, tipo, year, freq, prob_pal) values (\"%s\", \"%s\", %s, %s, %s)" % (pal, tipo, year, freq, prob)
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
    t = "select distinct n1.pal from es_ngram1 n1 left join es_1gram2 n2 on n1.pal = n2.pal where n2.pal is null order by pal;"
    try:
        cur4.execute(t)
    except:
        print("Error en primera seleccion")
    rows = cur4.fetchall()
    for row in rows:
        try:
            pal = row[0].decode('utf-8')
        except:
            pal = ''
        pal = pal.replace('\"', '\\"')
        if pal:
            t = "Select pal from es_ngram1 where pal = \"%s\" and tipo > '' limit 1;" % pal
            try:
                cur.execute(t)
            except my.Error as err:
                print((t, err))
            fila = cur.fetchone()
            if fila:
                pal = fila[0].decode('utf-8')
                if pal == "'":
                    pal = "\\'"
                if pal == '"':
                    pal = '\\"'
                if pal == "''":
                    pal = "\'\'"
                t = "select sum(freq) from es_ngram1 where pal = \"%s\" and tipo > '';" % pal
                try:
                   cur2.execute(t)
                   total_pal = cur2.fetchone()
                   t = "select pal, tipo, year, freq from es_ngram1 where pal = \"%s\" and tipo > '';" % pal
                   # print(t)
                   cur2.execute(t)
                   filas = cur2.fetchall()
                   if cur2.rowcount > 0:
                       fila_unica(con, cur3, filas, total_pal[0])
                except:
                   print(("Hubo un error con ", t))

        
    
if __name__ == "__main__":
    main(con_data)
    
    ''
