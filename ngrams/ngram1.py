'''
Created on 27/11/2013

@author: aurelio
'''
"""
modulo para guardar en mysql, en tabla ngram1, los datos bajados del googleapis ngrams
para 1gram
"""

from os import listdir, rename
from os.path import join
import re
import mysql.connector as my


con_data = {'user':'root','password':'agm','host':'192.168.1.34', \
            'database':'ngrams','raise_on_warnings': True, 'autocommit':True, 'buffered':True}


directorio = '/media/tera/ngrams/esp/1gram'
f = listdir(directorio)

def guarda(pal, year, freq):
    '''
    pal =  re.sub(pat, "", pal)
    '''
    t = """INSERT INTO es_ngram1 (pal, year, freq) 
        VALUES (\"%s\", %s, %s) 
        ON DUPLICATE KEY UPDATE freq = freq + %s""" % (pal,  year, freq, freq)
    try:
        cur.execute(t)
    except my.Error as er:
        print(("Error guardando fila", er, t))

def average_year(lineas, freq):
    t = [int(x[1])*int(x[2]) for x in lineas]
    return round(sum(t) / freq)

def resume(lineas):
    pal = lineas[0][0]
    pal = pal.split('_')[0]
    pal = pal.replace('"', '\\"')
    pal = pal.replace("'", "\\'")
    
    """
    pat = "_ADJ|_ADP|_ADV|_CONJ|_DET|_NOUN|_NUM|_PRON|_PRT|_VERB|_X"
    idx = pal.find('_')
    tipo = ''
    if idx > 0 and pal[idx:] in pat:
        tipo = pal[idx+1:]
        pal = pal[0:idx] 
    """
    freq = 0
    for linea in lineas:
        freq += int(linea[2])
    year = average_year(lineas, freq)
    # solo usar las palabras con más de 200 casos en todos los años.
    if freq >= 200:
        guarda(pal, year, freq)

def lee_archivo(archivo, cur):
    with open(archivo, encoding='utf-8') as f:
        # l = 0
        p = ''
        lineas = []
        for linea in f:
            datos = linea.split()
            if datos[0] != p:
                if p:
                    # procesa los datos de la palabra anterior
                    resume(lineas)
                p = datos[0]
                lineas = []
                lineas.append(datos)
            else:
                lineas.append(datos)


f = sorted(f)
f = [join(directorio, file) for file in f if file.startswith('1gram') 
     and not file.endswith('_done')]
con = my.connect(**con_data)
cur = con.cursor()
for archivo in f:
    print(("Empezando ", archivo))
    lee_archivo(archivo, cur)
    rename(archivo, archivo + '_done')
    
