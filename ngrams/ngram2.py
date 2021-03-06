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

def guarda(pal1, pal2, year, freq, nfile):
    #Evitar poblemas con encodings raros
    pal3 = pal1.encode('utf-8')
    pal4 = pal2.encode('utf-8')
    if len(pal1) == len(pal3) and len(pal2) == len(pal4):
        t = """INSERT INTO es_ngram2 (pal1, pal2, year, freq, archivo) 
            VALUES (\"%s\", \"%s\", %s, %s, %s) 
            ON DUPLICATE KEY UPDATE freq = freq + %s""" % (pal1[:40], pal2[:40], year, freq, nfile, freq)
        try:
            cur.execute(t)
        except my.Error as er:
            try:
                print(("Error guardando fila", er, t))
            except:
                print(("Error de codificación al guardar", er))

def average_year(lineas, freq):
    t = [int(x[2])*int(x[3]) for x in lineas]
    return round(sum(t) / freq)

def resume(lineas, nfile):
    pal1 = lineas[0][0]
    pal1 = pal1.replace('"', '\\"')
    pal1 = pal1.replace("'", "\\'")
    pal1 = pal1.replace('\\', '\\\\')
    pal2 = lineas[0][1]
    pal2 = pal2.replace('"', '\\"')
    pal2 = pal2.replace("'", "\\'")
    pal2 = pal2.replace('\\', '\\\\')
    nfile = int(nfile)
    """
    pat = "_ADJ|_ADP|_ADV|_CONJ|_DET|_NOUN|_NUM|_PRON|_PRT|_VERB|_X"
    idx = pal1.find('_')
    tipo1 = ''
    if idx > -1 and pal1[idx:-1] in pat:
        tipo1 = pal1[idx+1:]
        if pal1[0:idx]:
            pal1 = pal1[0:idx] 
    if not tipo1 and idx > -1:
        tipo1 = pal1[1:-1]
    idx = pal2.find('_')
    tipo2 = ''
    if idx > -1 and pal2[idx:] in pat:
        tipo2 = pal2[idx+1:]
        if pal2[0:idx]:
            pal2 = pal2[0:idx] 
    if not tipo2 and idx > -1:
        tipo2 = pal2[1:-1]
    """
    freq = 0
    for linea in lineas:
        freq += int(linea[3])
    year = average_year(lineas, freq)
    # solo usar las palabras con más de 300 casos en todos los años.
    if freq >= 300:
        guarda(pal1, pal2, year, freq, nfile)

def lee_archivo(archivo, cur):
    with open(archivo, encoding='utf-8', errors="surrogateescape") as f:
        nfile = archivo.split('.')[0].split('-')[1] #file number in file name
        # l = 0
        p1 = p2 = ''
        lineas = []
        filas = 0
        for linea in f:
            if not linea.startswith('"') and not linea.startswith("'") and not linea.startswith("\\"):
                datos = linea.split()
                filas += 1
                if datos[0] != p1 or datos[1] != p2:
	                if p1 and p2:
	                    # procesa los datos de la palabra anterior
	                    resume(lineas, nfile)
	                p1 = datos[0]
	                p2 = datos[1]
	                lineas = []
	                lineas.append(datos)
                elif filas < 10000:
	                # si más de 10000 remite las lineas en trozos de 10000
	                lineas.append(datos)
                else:
	                # si más de 10000 remite las lineas en trozos de 10000
	                lineas.append(datos)
	                resume(lineas, nfile)
	                filas = 0
	
                """         
                if l >= 40000:
	                sys.exit(0)
                """


con_data = {'user':'root','password':'agm','host':'192.168.1.34', \
            'database':'ngrams','raise_on_warnings': True, 'autocommit':True, 'buffered':True}


directorio = '/media/tera/ngrams/esp/2gram'
# directorio = '/home/aurelio/Escritorio/Enlace hacia .gvfs/ngrams en agm2/esp/2gram'
f = listdir(directorio)

f = sorted(f)
f = [join(directorio, file) for file in f if file.endswith('.csv')]
con = my.connect(**con_data)
cur = con.cursor()
for archivo in f:
    print((time.ctime(), "\n Empezando ", archivo))
    lee_archivo(archivo, cur)
    rename(archivo, archivo + '_done')

