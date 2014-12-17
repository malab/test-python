'''
Created on 12/09/2013

@author: aurelio
'''
#! /usr/bin/env python
#encoding:UTF-8

import os
import mysql.connector as my
import urllib.request as ur
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
import feedparser
from bs4 import BeautifulSoup as bs
from PIL import Image
from datetime import datetime
from datetime import timedelta
from time import mktime
import re
#from bs4 import UnicodeDammit

con_data = {'user':'root','password':'agm','host':'localhost', \
'database':'mx_noticias','raise_on_warnings': True, 'autocommit':True, 'buffered':True}


def trae_feed(fuente, seccion, url, parse, regu, busca):
    link = ''
    print(fuente, url, parse, regu,  busca)
    cur = con.cursor()
    try:
        contenido = trae_contenido(url)
    except:
        print("Error trayendo noticias de feed ", url)
        return
    if isinstance(contenido,str):
        print("Error trayendo noticias de feed ", url, "se trajo string en vez de array noticia")
        return
    elif not contenido:
        print ("Nada traído de ", url)
        return
    #print("Contenido llegado:", contenido)
    
    for noticia in contenido.entries:
        try:
            # print(noticia)
            #break
            if not noticia.title.endswith("."):
                noticia.title +="."
            titulo = noticia.title
        except:
            titulo = 'Sin titulo'
        if hasattr(noticia, 'link'):
            link = noticia.link
        elif hasattr(noticia, 'links'):
            try:
                link = noticia.links[0].href
            except:
                print("Error con noticia.links[0].href en BuscaFeeds - trae_feed")
        elif hasattr(noticia, 'base'):
            link = noticia.base
        con_ac = 'áéíóúü'
        sin_ac = 'aeiouu'
        #print('0')
        if link:
            #print('00')
            conv = str.maketrans(con_ac, sin_ac)
            link = link.translate(conv)
            trae_datos(noticia, fuente, link, parse, regu, busca)
            


def trae_contenido(url):
    #print(url)
    try:
        content = feedparser.parse(url)
    except:
        content = ''
    #print("contenido de feed:",content)
    return content

def trae_datos(noticia, fuente, link, parse, regu, busca):
    # Proviene de Busca_Feeds
    try:
        if 'published_parsed' in noticia:
            fecha2 = noticia.published_parsed
        elif 'updated_parsed' in noticia:
            fecha2 = noticia.updated_parsed
        fecha1 = datetime.fromtimestamp(mktime(fecha2))
        fecha = datetime.isoformat(fecha1)
        #fecha1 = datetime(fecha)
    except:
        fecha1 = datetime.now()
        fecha = datetime.isoformat(fecha1)
    fecha = fecha.replace('T', ' ')   
    dif = timedelta(days=-1)
    # print(fecha1)
    if fecha1 < datetime.now()+dif:
        # es anterior a un día (24 horas)
        return False
    try:
        texto = noticia.summary
    except:
        texto = ''
    # Quitamos tags del intro
    #primero quitamos las tags de enlaces <a>, pero dejando el texto (si no, se quita todo, incluyendo el texto)
    if texto:
        '''
        texto = re.sub('<a\shref=.*>', '', texto, re.DOTALL|re.IGNORECASE)
        texto = re.sub('</a>', '', texto, re.IGNORECASE)
        art = bs(texto) 
        for mitag in quitar:
            todas = art.find_all(mitag)
            [cada.extract() for cada in todas]
        #Quita también comentarios
        comments = art.find_all(text=lambda text:isinstance(text, Comment))
        [comment.extract() for comment in comments]   
        intro = art.text
        #quitar enlaces del intro, pero dejando el texto que se enlaza
        intro = re.sub('<a\s*href.*>(.*)</a>','\\1', intro, re.IGNORECASE)          
        if len(intro) > 400:
            intro = intro[:400]+"..."
        '''
        intro = texto
    else:
        intro = ''
    # print (intro)
    try:
        # print (link, fuente, busca)
        trae_articulo(link, fuente, parse, busca)
    except:
        print("Error en trae_articulo")
        pass
    # trae_otros()
    
    if not texto:
        return ''
    if texto == '':
        print("Artículo sin datos \n")

    # busca_imagen()

    # anal_idioma = texto
    return True

def trae_articulo(link, fuente, parse, busca):
    try:
        print('1', link)
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7' }
        # print('2')
        req = ur.Request(link, None, headers)
        # print('3', link)
        art1 = ur.urlopen(req)
        # print('4')
        art2 = art1.read()
        # print('5')
        art1.close()
    except HTTPError as e:
        print("error", e.code)
        if e.code == 400:
            link = e.geturl()     
            print(link)
            e = None
            trae_articulo(link, fuente, busca)
    '''
        print (e.code)
        print (e.read())
        print("<a href = "+link+">link no valido </a>")
        print(art2[:250])
    except URLError as e:
        print ('We failed to reach a server.')
        print ('Reason: ', e.reason)
    '''

    try:
        # print('6')
        #print(art2)
        articulo = bs(art2)
        # print('7')
        texto = ''
        if (articulo):
            texto = noticia_completa(articulo, regu, link)
            '''
            if parse == 'bs':
                #pass
                # print('8')
                texto = noticia_completa(articulo, regu, link)
            elif parse == 'solo':
                pass
                # print('8')
            '''
                # texto = solo_texto(articulo)
            # print("El texto del articulo es \n", texto)
            try:
                # print('9')
                busca_fotos(articulo, fuente, link, busca)
            except:
                print("Error en busca_fotos")
    except:
        print("<a href='"+link+"'>Error trayendo articulo de "+ fuente+"</a>")
        mitexto = ''

def noticia_completa(articulo, regu, link):
    # pass
    conteo = 0
    mitexto = ''
    minimo = 20
    #print(5)
    print("EL ENCODING DEL TEXTO ES:")
    if articulo.original_encoding.upper() != 'UTF-8':
        original = articulo.original_encoding
        print(original)
        mitexto = ''
        return mitexto
        '''
        texto = articulo.prettify(original)
        antes = ['Ăł', 'Ăş', 'Ăą']
        despues = ['ó','ú', 'ñ']
        #conv = bytes.translate(antes, despues)
        texto = texto.translate(antes,despues)
        # print(texto[:900])
        #articulo = articulo.__str__('latin-1')
        #print(articulo[:800])
        #articulo = texto.encode('UTF-8')
        #articulo = articulo.prettify('latin-1')
        articulo = bs(texto)
        '''
    try:
        con = my.connect(**con_data)
        t1 = ("select regu from reg_fuente where fuente = %(fuente)s and orden > 0 \
               order by orden;")
        cur = con.cursor()
        t2 = {'fuente':fuente}
        cur.execute(t1, (t2))
    except my.Error as err:
        print("Hubo error en mysql: {}".format(err))

    # print('10')
    # print("el link es", link)
    #print("articulo llega a regus así", articulo)

    for row in cur:
        try:
            regu = ''.join(row[0]) # pasar el tuple a string
        except:
            pass

    #for (reg, orden) in row:
    # print ('regu: ', regu)
    if regu.startswith ('#'):
        filas = articulo.find_all(id = regu[1:len(regu)])
        # print ("buscando: id = ", regu[1:len(regu)])
    elif regu.startswith('.'):
        filas = articulo.find_all(class_ = regu[1:len(regu)])
        print ("buscando: class_ = ", regu[1:len(regu)])
    else:
        filas = articulo.find_all(regu)
        # print ("buscando: ", regu)
        #filas = art._all('p')
    print ("todas las filas para ", regu, " son: ", len(filas))
    if len(filas) > 0:
        for fila in filas:
            para = fila.text
            if len(para) > minimo:
                mitexto += " \n" + para + ". ";
                conteo += len(para);
        mitexto.strip()
        if mitexto and not mitexto.endswith("."):
            mitexto += "."
    '''
        except:
            print("error localizando parrafos de ", fuente, link)
    cur.close()
    '''
    # print('11')

    print("mitexto es ", mitexto)
    if mitexto:
        pass
        #mitexto = aplica_regex(mitexto)
    else:
        print("<a href = "+link+">No hay mitexto en noticia_completa() para "+fuente+"</a>")
    # print("Para ", titulo, "texto corregido tras regex", mitexto)
    #print(8)
    # print(9, "mitexto:", mitexto)
    return mitexto

def busca_fotos(articulo, fuente, url, busca):
    print(url + "\n")
    try:
        if busca.startswith('#'):
            posible = articulo.find(id = busca[1:])
        elif busca.startswith('@'):
            posible = articulo.find('img')
        else:
            posible = articulo.find(class_ = busca)
        # print("posibles uno: ", posible)
    except:
        print("error en findall de buscafotos")      

    try:
        # print('2', url)
        foto =  posible.find('img')
        # print(foto)
        link_foto = foto.get('src')
        # print('3', link_foto)
        # print(link_foto)
        #link_foto = link_foto.replace('../', '/')
        # si direccion relativa, no absoluta
        if link_foto.startswith('/'):
            o = urlparse(url)
            link_foto = 'http://' + o.hostname + link_foto
            # print(link_foto)
        elif link_foto.startswith('./'):
            o = urlparse(url)
            partes = url.split('/')
            link_foto = 'http://' + o.hostname + '/' + partes[len(partes)-2] + link_foto[1:]
            # print(link_foto)
        elif link_foto.startswith('../'):
            '''
            o = urlparse(url)
            partes = url.split('/')
            link_foto = 'http://' + o.hostname + '/' + partes[len(partes)-3] + link_foto[2:]
            '''
            (directorio, archivo) = os.path.split(url)
            # print(directorio)
            link_foto = os.path.normpath(os.path.join(directorio,link_foto))
            link_foto = link_foto.replace('\\', '/', )
            link_foto = link_foto.replace('http:/www', 'http://www')
            # print('4', link_foto)
        elif not link_foto.startswith('http:'):
            o = urlparse(url)
            partes = url.split('/')
            link_foto = 'http://' + o.hostname + '/' + link_foto
            print(link_foto)
        # print(link_foto)
        #arregla algunos
        link_foto = link_foto.replace('clarin.feedsportal.com', 'www.clarin.com')
        link_foto = link_foto.replace('http://eluniversal.com.co.feedsportal.com', 'http://www.eluniversal.com.co')
        if fuente == 65:
            link_foto = link_foto.replace('feedproxy.google.com', 'mexico.cnn.com')
        elif fuente == 11:
            link_foto = link_foto.replace('feedproxy.google.com', 'elfinanciero.com.mx')
        try:
            ancho = 0
            alto = 0
            ancho = foto.get('width')
            alto = foto.get('height')
            caption = foto.get('alt')
            if not ancho:
                im = ur.urlretrieve(link_foto)
                img = Image.open(im[0])
                ancho, alto = img.size        
            print("Tenemos foto de ancho "+ancho +" y alto " + alto +" en ", link_foto)
        except:
            print("Tenemos foto pero sin ancho ", ancho , " ni alto ", alto, " en ", link_foto)
    except:
        print("No hay datos de imagen")
fuente =9
busca = 'image_holder'
con = my.connect(**con_data)
cur = con.cursor() 
t = 'select f1.id_fuente as fuente, f1.seccion, f1.rss_seccion as rss, \
f.parse, r.regu from fuentes1 f1 inner join fuentes f on f.id = f1.id_fuente \
left join reg_fuente r on f.id = r.fuente \
where id_fuente = %i' % fuente 
cur.execute(t)
for fuente, seccion, rss, parse, regu in cur.fetchall():
    trae_feed(fuente, seccion, rss, parse, regu, busca)
