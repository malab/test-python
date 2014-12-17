#! /usr/bin/env python
#encoding:UTF-8
'''
Created on 06/11/2012

@author: aurelio
'''
import re
import os
import urllib.request
from urllib.parse import urlparse
# import signal
# import socket
from datetime import datetime
from datetime import timedelta
from time import mktime
import inspect
from PIL import Image
from bs4 import BeautifulSoup as bs, Comment
# import re
import mysql.connector as my
import justext
from config import *
# from DatosPN import *
from Clasifica import *


class Noticia():
    '''
    classdocs
    '''

    def inicia(self, datos):
        self._id = 0
        self.fuente = ''
        self.seccion = ''
        self.link = ''
        self.fecha = ''
        self.titulo = ''
        self.intro = ''
        self.texto = ''
        self.articulo = ''
        self.color = ''
        self.abstract = ''
        self.keywords = ''
        self.description = ''
        self.h1 = ''
        self.h2 = ''
        self.h3 = ''
        self.imagenes = []
        self.sonido = ''
        self.video = ''
        self.idioma = ''
        self.parse = ''
        self.pn = ''
        self.ratio_pn = 0 
        self.clasifica_pn = Clasifica(datos)
        self.datos = datos # los datos inicializados en datosPN, segÃºn tablas
        self.minimo = 50 # variable para caracteres mÃ­nimos a aceptar en pÃ¡rrafos de noticias
        # acentos es para corregir ciertos textos que no están bien en utf-8
        self.acentos = {'Ã¡':'á','Ã­':'í', 'Ã³':'ó','Ãº':'ú', 'Ã±':'ñ'}
        # timeout in seconds
        # timeout = 60
        # socket.setdefaulttimeout(timeout)
        
    def handler(self, signum, frame):
        print ('Signal handler called with signal', signum)
        
    def cambia_acentos(self, texto, dic):
        for i, j in dic.items():
            texto = texto.replace(i, j)
        return texto
                
    def trae_datos(self, noticia):
        
        # Proviene de Busca_Feeds
        try:
            if 'published_parsed' in noticia:
                fecha2 = noticia.published_parsed
            elif 'updated_parsed' in noticia:
                fecha2 = noticia.updated_parsed
            fecha1 = datetime.fromtimestamp(mktime(fecha2))
            self.fecha = datetime.isoformat(fecha1)
            #fecha1 = datetime(fecha)
        except:
            # print('fuente y seccion no tiene fecha', self.fuente, self.seccion)
            fecha1 = datetime.now()
            self.fecha = datetime.isoformat(fecha1)
        self.fecha = self.fecha.replace('T', ' ')   
        dif = timedelta(days=-1)
        if fecha1 < datetime.now()+dif:
            self = None # es anterior a un dí­a (24 horas)
            return False
        # print('Fecha1:', self.fecha)
        try:
            self.texto = noticia.summary
        except:
            self.texto = ''
        # Quitamos tags del intro
        #primero quitamos las tags de enlaces <a>, pero dejando el texto (si no, se quita todo, incluyendo el texto)
        if self.texto:
            self.texto = re.sub('<a\shref=.*>', '', self.texto, re.DOTALL|re.IGNORECASE)
            self.texto = re.sub('</a>', '', self.texto, re.IGNORECASE)
            try:
                self.art = bs(self.texto) 
            except:
                self.art = bs('')
            for mitag in self.datos.quitar:
                todas = self.art.find_all(mitag)
                [cada.extract() for cada in todas]
            #Quita tambiÃ©n comentarios
            comments = self.art.find_all(text=lambda text:isinstance(text, Comment))
            [comment.extract() for comment in comments]   
            self.intro = self.art.text
            #quitar enlaces del intro, pero dejando el texto que se enlaza
            self.intro = re.sub('<a\s*href.*>(.*)</a>','\\1', self.intro, re.IGNORECASE)          
            if len(self.intro) > 400:
                self.intro = self.intro[:400]+"..."
        else:
            self.intro = ''
        # print (self.intro)
        try:
            if self.parse == 'bs':
                self.texto = self.trae_articulo_viejo()
            elif self.parse == 'solo':
                self.texto = self.solo_texto()
            else:
                self.texto = self.solo_texto()
        except:
            pass

        # Ajusta el texto aplicando ciertas reglas de regex
        self.texto = self.aplica_regex(self.texto)
        
        # Anulado de momento el gtraer otros (keywords, etc.)
        # self.trae_otros()
        
        
        # self.texto = self.articulo.text
        if not self.texto:
            # print ("Aquí no hay articulo:", self.link, "\n")
            return False
        if self.texto == '':
            print("Artículo sin datos \n")
            self.imprime()

        self.busca_imagen()

        if IDIOMAS == True:
            anal_idioma = self.texto
            
            #Identifica idioma, solo si hay suficiente texto
    
            if len(anal_idioma) > 500:
                self.idioma = self.clasifica_pn.lang_ident(anal_idioma)
            else:
                self.idioma = 'esp'
            
            
    
        return True
    
    def solo_texto(self):
        '''
         Proviene de trae_datos donde pasa a self.texto
        Trae el contenido de cada url individual (cada noticia) por urllib.request.urlopen() y BeautifulSoup
        
        '''
        if self.link:
            con_ac = 'áéíóúüñ'
            sin_ac = 'aeiouun'
            conv = str.maketrans(con_ac, sin_ac)
            self.link = self.link.translate(conv)
        texto = ''     
        try:
            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers={'User-Agent':user_agent,} 
            req = urllib.request.Request(self.link, None, headers)
            art1 = urllib.request.urlopen(req)
            # signal.alarm(0) 
        except:
            print("<a href = '"+self.link+"'>Sin conexion (solo_texto) al link</a>")
            return False
        art2 = art1.read()
        art1.close()
        try:
            #metas = parseString(art2)
            #print(1)  
            try:         
                paras = justext.justext(art2, justext.get_stoplist('Spanish'))
            except:
                print("Error en justext")
            for para in paras:
                if para['class'] == 'good':
                    parra = para['text']
                    parra = self.cambia_acentos(parra, self.acentos)
                    parra = parra.replace('Ã', 'Ó')
                    if parra.endswith('.'):
                        texto += " " + parra
                    else:
                        texto += " " +parra + "."
            if not texto:
                print("<a href='"+self.link+"'>No hay texto recibido en trae_articulo"  + self.fuente+"</a>")
            else:
                self.articulo = bs(art2)
                #print(2)
                if (self.articulo):
                    self.busca_fotos()
                    #print(3) 
                return texto
        except:
            print("<a href = '"+self.link+"'>Errores en justext para link </a>")
            return False
            
       
        
    
    
    def trae_articulo_viejo(self):
        '''
        url, fuente => str
        
        
        Proviene de trae_datos donde pasa a self.texto
        Trae el contenido de cada url individual (cada noticia) por urllib.request.urlopen() y BeautifulSoup
        
        '''

        try:
            # signal.alarm(60)
            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers={'User-Agent':user_agent,} 
            req = urllib.request.Request(self.link, None, headers)
            art1 = urllib.request.urlopen(req)
            # signal.alarm(0) 
        except:
            print("<a href = '"+self.link+"'>Conexión (trae_articulo_viejo) no válida para link </a>")
            return False
        art2 = art1.read()
        art1.close()
        try:
            #metas = parseString(art2)
            #print(1)
            self.articulo = bs(art2)
            #print(2)
            if (self.articulo):
                self.busca_fotos()
                #print(3)
                self.quita_tags()
                #print(4)
                # print("link", self.link)
                # print("Articulo despues de quita_tags", self.articulo) 
                mitexto = self.noticia_completa();
                #print(10)
                if not mitexto:
                    print("<a href='"+self.link+"'>No hay mitexto recibido en trae_articulo"  + self.fuente+"</a>")
            else:
                print("BS no formó artí­culo")
        except:
            print("<a href='"+self.link+"'>Error trayendo articulo de "+ self.fuente+"</a>")
            mitexto = ''
        return mitexto
    
    def noticia_completa(self):
        '''
        art(beautifulsoup), int, fuente(str), url(str) => str
        
        Proviene de trae_articulo
        Intenta extraer del html total (art) que se recibe en trae_articulo
        los pÃ¡rrafos que corresponden a la noticia, eliminando anuncios, cabeceras, tablas de enlaces, etc.
        Esto se hace con ayuda de la tabla reg_fuente, donde se indica para cada medio (fuente) cÃ³mo
        identificar en base a ids y clases la noticia

        '''
        conteo = 0
        mitexto = ''
        #print(5)
        # si se usa otro encoding y hay caracteres raros como 'Ăł'
        if self.articulo.original_encoding.upper() != 'UTF-8' and self.articulo.find('Ăł') >0:
            original = self.articulo.original_encoding
            print(self.fuente, self.link, ' esta en ', original)
            mitexto = ''
            return mitexto

        try:
            con = my.connect(**con_data)
            t1 = ("select regu from reg_fuente where fuente = %(fuente)s and orden > 0 \
                   order by orden;")
            cur = con.cursor()
            t2 = {'fuente':self.fuente}
            cur.execute(t1, (t2))
        except my.Error as err:
            print("Hubo error en mysql: {}".format(err))
        #print(6)
        # print("el link es", self.link)
        # print("self.articulo llega a regus asÃ­", self.articulo)
        for row in cur:
            try:
                regu = ''.join(row[0]) # pasar el tuple a string
                if (conteo < self.minimo*4):
                    #for (reg, orden) in row:
                    # print ('regu: ', regu)
                    if regu[0] == '#':
                        filas = self.articulo.find_all(id = regu[1:len(regu)])
                        # print ("buscando: id = ", regu[1:len(regu)])
                    elif regu[0] == '.':
                        filas = self.articulo.find_all(class_ = regu[1:len(regu)])
                        # print ("buscando: class_ = ", regu[1:len(regu)])
                    else:
                        filas = self.articulo.find_all(regu)
                        # print ("buscando: ", regu)
                        #filas = art._all('p')
                    # print ("todas las filas para ", regu, " son: ", len(filas))
                    if len(filas) > 0:
                        for fila in filas:
                            para = fila.text
                            if len(para) > self.minimo:
                                mitexto += " \n" + para + ". ";
                                conteo += len(para);
                        mitexto.strip()
                        if mitexto and not mitexto.endswith("."):
                            mitexto += "."
            except:
                print("error localizando parrafos de ", self.fuente, self.link)
        cur.close()
        con.close()
        return mitexto
    
    def aplica_regex(self, mitexto):
        # Proviene de noticia_completa()
        #Distintos regex para eliminar html content que no forma parte de la noticia
        
        #Elimina puntos al comienzo de texto
        try:
            if self.parse == 'bs':
                mitexto = re.sub('^[\.|\n][\.|*\s]*','', mitexto)
                # Eliminan varios strings remanentes de javascript 
                # o de html no relacionados con noticia.
    
                # separa con punto y espacio cuando dos palabras estÃ¡n unidas por punto sin espacio
                mitexto = re.sub('\.([A-Z])','. \\1', mitexto)
                #Elimina publicidad (Canarias7)
                mitexto = re.sub('^Publicidad\sTwittear', '', mitexto, flags = re.IGNORECASE)
                #Elimina frase copyright
    
                mitexto = re.sub('Â©\sEL\sCOMERCIO.*RESERVADOS:', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('Â©\sEL\sCORREO.*RESERVADOS:', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('Â©\sIdeal.*RESERVADOS:', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('Copyright\sÂ©\sFactor.*RESERVADOS:', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('Rellena\slos\ssiguientes.*oposici\.n\sexpresa', '', mitexto, flags = re.DOTALL)
                mitexto = re.sub('Queda\sprohibida.*oposiciÃ³n\sexpresa', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('Temas relacionados', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('Inicio\smultimedia.*Fin\smultimedia:', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('Contenidos\smultimedia\speso\s8\sFin\scontenidos\smultimedia\speso\s8', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('TAGS\sRELACIONADOS.*votos[\s\.]', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                #  Elimina palabra publicidad en canarias7 al inicio
                mitexto = re.sub('^Publicidad\s', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                #Elimina Ãºltimas frases de publicdad en diez minutos
                mitexto = re.sub('DescÃ¡rgate.*Diez\sMinutos', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('MÃ¡s\informaciÃ³n.*euronews', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('JavaScript\ses\snecesario\spara\sver\seste\svÃ­deo\.', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('Imprimir\sEnviar\d*\sCOMENTAR\sTweet', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('//\sSaber\smÃ¡s\.{1,3}\s{1,3}Temas.*', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('Levante-emv.com\scuenta.*', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('Noticias\srelacionadas', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('VÃ­deos\srelacionados', '', mitexto,flags =  re.IGNORECASE)
                mitexto = re.sub('\|.*\|', '|', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('Escribe\sel\stexto\sdel\scampo.*', '', mitexto, flags = re.DOTALL|re.IGNORECASE)
                mitexto = re.sub('\(mÃ¡s\sinformaciÃ³n,\sen\sla\sediciÃ³n\simpresa\)\.', '', mitexto,flags =  re.IGNORECASE)
                mitexto = re.sub('MÃ�S\sINFORMACIÃ“N\sEN\sLA\sEDICIÃ“N\sIMPRESA\.', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('MÃ¡s\sinformaciÃ³n\sen\sla\sediciÃ³n\simpresa\.', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('Compartir\s>\s>\s', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('Imprime\sesta\spÃ¡gina\s', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('Siga\sleyendo\sla\snoticia\sen\sOrbyt.*sin\slÃ­mites\.', '', mitexto,flags =  re.IGNORECASE)
                mitexto = re.sub('//\s?Comentarios.*', '', mitexto, flags = re.IGNORECASE)
                mitexto = re.sub('Rellena\slos\ssiguientes\scampos.*', '', mitexto,flags = re.S|re.I)
                # Elimina puntos y espacios al final de pÃ¡rrafo, dejando solo un punto
                mitexto = re.sub('[\.|*\s]*$','.', mitexto)
                # Elimina cualquier nÃºmero de lineas en blanco dejando solo una
                mitexto = re.sub('\\n{1,}', '\n', mitexto)

                # para el economista
                if self.fuente == 8:
                    mitexto = re.sub('\\n', '', mitexto)
                    mitexto = re.sub('Tweet.*\spara\siPad\.', '', mitexto, re.S | re.M | re.I)
                    
            mitexto = self.aplica_regex_todos(mitexto)
                        
            
        except:
            print("Error aplicando regex")
        return mitexto
    
    def aplica_regex_todos(self, mitexto):
        #proviene de aplica_regex
        # aplica regex para cada fuente, según formula guardada en tabla regex
        try:
            con = my.connect(**con_data)
            cur = con.cursor()
            t = 'select regex, dejar from regex where fuente = %i order by orden' % self.fuente
            cur.execute(t)
            for regex, dejar in cur.fetchall():
                regex = regex.decode('UTF-8')
                mitexto = re.sub(regex, dejar, mitexto,flags = re.S|re.I)
                mitexto = re.sub('^\.[\.|*\s]*','', mitexto)
            cur.close()
        except:
            print("Error aplicando regex_todos") 
        finally:
            cur.close()
            con.close()
        return mitexto
                           
                           
    
    def trae_otros(self):
        # Proviene de trae_datos()
        try:
            self.keywords = self.articulo.find(attrs={"name":"keywords"})['content']
        except:
            try:
                self.keywords = self.articulo.find(attrs={"name":"Keywords"})['content']
            except:
                self.keywords=''
                # print("no keywords en ", art.title)
        try:
            self.description = self.articulo.find(attrs={"name":"description"})['content']
        except:
            try:
                self.description = self.articulo.find(attrs={"name":"Description"})['content']
            except:
                self.description=''
                # print("no description en ", art.title)
        try:
            self.abstract = self.articulo.find(attrs={"name":"abstract"})['content']
        except:
            try:
                self.abstract = self.articulo.find(attrs={"name":"Abstract"})['content']
            except:
                self.abstract=''
                # print("no abstract en ", art.title)
        try:
            self.h1 = self.articulo.find('h1').text
            self.h2 = self.articulo.find('h2').text
            self.h3 = self.articulo.find('h3').text
        except:
            pass
        # Si no hay intro, recogerlo de    description, abstract o, en Ãºltimo lugar, primera parte del articulo
        if not self.intro:
            if self.description:
                self.intro = self.description
            elif self.abstract:
                self.intro = self.abstract
            else:
                self.intro = ''                
            '''
            elif self.articulo.text:
                self.intro = self.articulo.text[:250]
            '''

        elif len(self.intro) < len(self.description):
            self.intro = self.description
        if self.intro and not self.intro.endswith("."):
            self.intro += "."
        if not self.intro:
            pass
            # print("en ", self.link, "no hay intro. Recibido", self.noticia)
                
    def busca_imagen(self):
        try:
            if hasattr(self.noticia, 'links'):
                if len(self.noticia.links) > 1:
                    for link in self.noticia.links:
                        if link.type == 'image/jpeg' or link['type'] == 'image/jpeg':
                            # print(link)
                            im = urllib.request.urlretrieve(link.href)
                            img = Image.open(im[0])
                            ancho, alto = img.size
                            self.imagenes.append({'link':link.href, 'ancho':ancho, 'alto':alto, 'caption':''})
                            # Algunos medios tienen varias imÃ¡genes de tamaÃ±o pequeÃ±o, medio y grande. Buscamos medio
                            # return self.imagenes
                            
                        if link.type == 'audio/mpeg' or link['type'] == 'audio/mpeg':
                            self.sonido = link.href
                            return self.sonido
                    return self.imagenes
                elif hasattr(self.noticia, 'media_content'):
                    for link in self.noticia.media_content:
                        if link['type'] == 'image/jpeg':
                            im = urllib.request.urlretrieve(link['url'])
                            img = Image.open(im[0])
                            ancho, alto = img.size
                            self.imagenes.append({'link':link.href, 'ancho':ancho, 'alto':alto, 'caption':''})
                            # return self.imagenes
                        if link['type'] == 'audio/mpeg':
                            self.sonido = link['url']
                            return self.sonido
                    # return self.imagenes
                else:
                    pass
        except:
            pass
            # print("Error en busca_imagen")    

    def busca_fotos(self):
        t = 'select img from reg_imagen where fuente = %i and anulado = 0 order by orden;' % self.fuente
        con = my.connect(**con_data)
        cur = con.cursor()
        cur.execute(t)
        for img in cur.fetchall():
            busca = img[0]

            try:
                if busca.startswith('#'):
                    posible = self.articulo.find(id = busca[1:])
                else:
                    posible = self.articulo.find(class_ = busca)
                #print("posibles uno: ", posibles)
            except:
                print("error en findall de buscafotos")      

            try:
                foto =  posible.find('img')
                # print(foto)
                link_foto = foto.get('src')
                # print(link_foto)
                #link_foto = link_foto.replace('../', '/')
                # si direccion relativa, no absoluta
                if link_foto.startswith('/'):
                    o = urlparse(self.link)
                    link_foto = 'http://' + o.hostname + link_foto
                    # print(link_foto)
                elif link_foto.startswith('./'):
                    o = urlparse(self.link)
                    partes = self.link.split('/')
                    link_foto = 'http://' + o.hostname + '/' + partes[len(partes)-2] + link_foto[1:]
                    # print(link_foto)
                elif link_foto.startswith('../'):
                    '''
                    o = urlparse(url)
                    partes = url.split('/')
                    link_foto = 'http://' + o.hostname + '/' + partes[len(partes)-3] + link_foto[2:]
                    '''
                    (directorio, archivo) = os.path.split(self.link)
                    # print(directorio)
                    link_foto = os.path.normpath(os.path.join(directorio,link_foto))
                    link_foto = link_foto.replace('\\', '/', )
                    link_foto = link_foto.replace('http:/www', 'http://www')
                    # print(link_foto)
                elif not link_foto.startswith('http:'):
                    o = urlparse(self.link)
                    partes = self.link.split('/')
                    link_foto = 'http://' + o.hostname + '/' + link_foto
                    #print(link_foto)
                # print(link_foto)
                #arregla algunos
                link_foto = link_foto.replace('clarin.feedsportal.com', 'www.clarin.com')
                link_foto = link_foto.replace('http://eluniversal.com.co.feedsportal.com', 'http://www.eluniversal.com.co')
                link_foto = link_foto.replace('feedproxy.google.com', 'www.elfinanciero.com.mx')
                try:
                    ancho = 0
                    alto = 0
                    ancho = foto.get('width')
                    alto = foto.get('height')
                    caption = foto.get('alt')
                    if not ancho:
                        im = urllib.request.urlretrieve(link_foto)
                        img = Image.open(im[0])
                        ancho, alto = img.size        
                    #print("Tenemos foto de ancho "+ancho +" y alto " + alto +" en ", link_foto)
                except:
                    pass
                    #print("Tenemos foto pero sin ancho ", ancho , " ni alto ", alto, " en ", link_foto)
                if 60<int(ancho)<680:
                    if not alto:
                        alto = 0
                    self.imagenes.append({'link':link_foto, 'ancho':ancho, 'alto':alto, 'caption':caption})
            except:
                #print("No hay datos de imagen")
                pass

    def quita_tags(self):
        '''
        texto = re.sub('<.*javascript.*>.*</.*script>', '', texto, re.DOTALL|re.IGNORECASE) 
        texto = re.sub('<!--.*-->', '', texto, re.DOTALL)
        self.art = bs(texto) 
        
        Viene de trae_articulo()
        '''
        try:
            #primero quita las tags de enlaces <a>, pero dejando el texto (si no, se quita todo, incluyendo el texto)
            '''
            chequear
            mitexto = self.articulo.text
            mitexto = re.sub('<a\shref=.*>', '', mitexto, re.IGNORECASE)
            mitexto = re.sub('</a>', '', mitexto, re.IGNORECASE)
            self.articulo = bs(mitexto)
            '''
            
            for mitag in self.datos.quitar:
                todas = self.articulo.find_all(mitag)
                [cada.extract() for cada in todas]
            #Quita tambiÃ©n comentarios
            comments = self.articulo.find_all(text=lambda text:isinstance(text, Comment))
            [comment.extract() for comment in comments]
        except:           
            print("Error en quita_tags")
        ''' chequeo
        '''
        if not self.articulo:
            pass
            '''
            print("inicial: ", self.texto)
            print("Final", self.articulo)
            '''
    def imprime(self):
        print ("Imprimiendo......")
        a = inspect.getmembers(self)
        for b in a:
            if not b[0].startswith("__"):
                print(b)



    def __init__(self, datos):
        '''
        Constructor
        '''
        self.inicia(datos)
