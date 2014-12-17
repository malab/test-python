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
import time

con_data = {'user':'root','password':'agm','host':'192.168.1.34', \
            'database':'ngrams','raise_on_warnings': True, 'autocommit':True, 'buffered':True}


directorio = '/media/tera/ngrams/esp/3gram'
f = listdir(directorio)

def guarda(pal1, pal2, pal3, year, freq, nfile):
    #Evitar poblemas con encodings raros
    pal4 = pal1.encode('utf-8')
    pal5 = pal2.encode('utf-8')
    pal6 = pal3.encode('utf-8')
    if len(pal1) == len(pal4) and len(pal2) == len(pal5) and len(pal3) == len(pal6):
        t = """INSERT INTO es_ngram3 (pal1, pal2, pal3, year, freq, archivo) 
            VALUES (\"%s\", \"%s\", \"%s\", %s, %s, %s) 
            ON DUPLICATE KEY UPDATE freq = freq + %s""" % (pal1[:40], pal2[:40], pal3[:40], year, freq, nfile, freq)
        try:
            cur.execute(t)
        except my.Error as er:
            try:
                print(("Error guardando fila", er, t))
            except:
                print(("Error de codificación al guardar", er))

def average_year(lineas, freq):
    t = [int(x[3])*int(x[4]) for x in lineas]
    return round(sum(t) / freq)

def resume(lineas, nfile):
    pal1 = lineas[0][0]
    pal1 = pal1.replace('\\', '/')
    pal1 = pal1.replace('\"', '\\"')
    pal2 = lineas[0][1]
    pal2 = pal2.replace('\\', '/')
    pal2 = pal2.replace('\"', '\\"')
    pal3 = lineas[0][2]
    pal3 = pal3.replace('\\', '/')
    pal3 = pal3.replace('\"', '\\"')
    
    # pal2 = pal2.replace('\\', '\\')
    """
    pat = "_ADJ|_ADP|_ADV|_CONJ|_DET|_END|_NOUN|_NUM|_PRON|_PRT|_ROOT|_START|_VERB|_X"
    idx = pal1.find('_')
    tipo1 = tipo2 = tipo3 = ''
    if pal1.startswith('_') and pal1.endswith('_'):
        tipo1 = pal1[1:-1]
    elif idx > 0 and pal1[idx:] in pat:
        tipo1 = pal1[idx+1:]
        pal1 = pal1[0:idx] 
    idx = pal2.find('_')
    if pal2.startswith('_') and pal2.endswith('_'):
        tipo2 = pal2[1:-1] 
    elif idx > 0 and pal2[idx:] in pat:
        tipo2 = pal2[idx+1:]
        pal2 = pal2[0:idx] 
    idx = pal3.find('_')
    if pal3.startswith('_') and pal3.endswith('_'):
        tipo3 = pal3[1:-1]  
    elif idx > 0 and pal3[idx:] in pat:
        tipo3 = pal3[idx+1:]
        pal3 = pal3[0:idx]    
    """            
    freq = 0
    for linea in lineas:
        freq += int(linea[4])
    year = average_year(lineas, freq)
    # solo usar las palabras con más de 600 casos en todos los años.
    if freq >= 250:
        guarda(pal1, pal2, pal3, year, freq, nfile)

def lee_archivo(archivo, nfile):
    with open(archivo, encoding='utf-8', errors="surrogateescape") as f:
        nfile = archivo.split('.')[0].split('-')[1] #file number in file name
        # l = 0
        p1 = p2 = p3 = ''
        lineas = []
        filas = 0
        for linea in f:
            if not linea.startswith('"') and not linea.startswith("'") and not linea.startswith("\\"):
                datos = linea.split()
                filas += 1
                if datos[0] != p1 or datos[1] != p2 or datos[2] != p3:
                    if p1 and p2 and p3:
                        # procesa los datos de la palabra anterior
                        if lineas:
                            resume(lineas, nfile)
                    p1 = datos[0]
                    p2 = datos[1]
                    p3 = datos[2]
                    lineas = []
                    lineas.append(datos)
                elif filas < 10000:
                    # si más de 10000 remite las lineas en trozos de 10000
                    lineas.append(datos)
                else:
                    # si más de 10000 remite las lineas en trozos de 10000
                    lineas.append(datos)
                    if lineas:
                        resume(lineas, nfile)
                        filas = 0
                        lineas = []
                    
                """         
                if l >= 40000:
                    sys.exit(0)
                """

f = sorted(f)
f = [join(directorio, file) for file in f if file.endswith('.csv')]
con = my.connect(**con_data)
cur = con.cursor()
for archivo in f:
    print((time.ctime(), "\n Empezando ", archivo))
    lee_archivo(archivo, cur)
    rename(archivo, archivo + '_done')
