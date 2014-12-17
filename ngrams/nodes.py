'''
Created on 27/11/2013

@author: aurelio
'''
"""
modulo para guardar en mysql, en tabla ngram2, los datos bajados del googleapis ngrams
para 2gram (bigrams)
"""

from os import listdir, rename
from os.path import join
import re
import mysql.connector as my
import sys


con_data = {'user':'root','password':'agm','host':'localhost', \
            'database':'ngrams','raise_on_warnings': True, 'autocommit':True, 'buffered':True}


directorio = '/media/tera/ngrams/eng/syntactic/nodes'
f = listdir(directorio)

def guarda(pal, pos, parse, freq, cur):
    t = """INSERT INTO nodes (pal, pos, parse, freq) 
        VALUES (\"%s\", \"%s\", \"%s\", %s) 
        ON DUPLICATE KEY UPDATE freq = freq + %s""" % (pal, pos, parse, freq, freq)
    try:
        cur.execute(t)
    except my.Error as er:
        print(("Error guardando fila", er, t))

"""
def average_year(lineas, freq):
    t = [int(x[2])*int(x[3]) for x in lineas]
    return round(sum(t) / freq)
"""

def resume(lineas):
    pal = lineas[0]
    try:
        dat = lineas[1].split("/")
    except: # si es una list en vez de string
        dat = lineas[0][1].split("/")
    pos = dat[1]
    parse = dat[2]   
    try: 
        freq = int(lineas[2])
    except:
        freq = 0
    """
    for linea in lineas:
        freq += int(linea[3])
    year = average_year(lineas, freq)
    """
    # solo usar las palabras con más de 20 casos en la suma de todos los años.
    if int(freq) >= 20:
        guarda(pal[:40], pos, parse, freq, cur)

def lee_archivo(archivo, cur):
    with open(archivo, encoding='utf-8') as f:
        # l = 0
        p1 = p2 = ''
        lineas = []
        filas = 0
        for linea in f:
            datos = linea.split()
            filas += 1
            if datos[0] != p1 or datos[1] != p2:
                if p1 and p2:
                    # procesa los datos de la palabra anterior
                    resume(lineas[0])
                    """
                    if l > 39500:
                        print(datos)
                    l += 1
                    """
                p1 = datos[0]
                p2 = datos[1]
                # freq = datos[3]
                lineas = []
                lineas.append(datos)
            elif filas < 10000:
                # si más de 10000 remite las lineas en trozos de 10000
                lineas.append(datos)
            else:
                # si más de 10000 remite las lineas en trozos de 10000
                lineas.append(datos)
                resume(lineas)
                filas = 0
                
            """         
            if l >= 40000:
                sys.exit(0)
            """

f = sorted(f)
f = [join(directorio, file) for file in f if file.startswith('nodes') and not file.endswith('_done')]
con = my.connect(**con_data)
cur = con.cursor()
for archivo in f:
    print(("Empezando ", archivo))
    lee_archivo(archivo, cur)
    rename(archivo, archivo + '_done')
