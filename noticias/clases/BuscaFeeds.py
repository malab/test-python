#! /usr/bin/env python
#encoding:UTF-8
from __future__ import print_function
import feedparser
import mysql.connector as my
# import pymysql
from config import con_data
from Noticia import *
'''
Created on 05/04/2013

@author: aurelio
'''

class BuscaFeeds:
    '''
    classdocs
    '''


    def __init__(self, datos):
        '''
        Constructor
        '''
        self.con = my.connect(**con_data)
        self.fuente = ''
        self.seccion = ''
        self.url = ''
        self.noticias = 0 #numero de noticias en feed
        self.datos = datos #listas de datos generales de pn en tablas pos y neg, etc.
        
        
    def trae_feed(self, fuente, seccion, url, parse):
        '''
        (fuente, seccion, url) => none
        Busca y guarda las noticias nuevas que haya en cada uno de los feeds
        para cada uno de los medios y seccion tal como está en tabla fuentes1
    
        global keywords, abstract, description, h1, h2, h3, imagen, sonido
        '''
        self.url = url
        self.seccion = seccion
        self.fuente = fuente
        self.parse = parse
        #con = pymysql.connect(**con_data)
        cur = self.con.cursor()
        try:
            contenido = self.trae_contenido()
        except:
            print("Error trayendo noticias de feed ", self.url)
            return
        if isinstance(contenido,str):
            print("Error trayendo noticias de feed ", self.url, "se trajo string en vez de array noticia")
            return
        elif not contenido:
            print ("Nada traído de ", self.url)
            return
        # print("Contenido llegado:", contenido)
        for noticia in contenido.entries:
            self.cls_noticia = Noticia(self.datos)
            self.cls_noticia.noticia = noticia
            self.cls_noticia.fuente = self.fuente
            self.cls_noticia.seccion = self.seccion
            self.cls_noticia.parse = self.parse
            try:
                if not noticia.title.endswith("."):
                    noticia.title +="."
                self.cls_noticia.titulo = noticia.title
            except:
                self.cls_noticia.titulo = 'Sin titulo'
            if hasattr(noticia, 'link'):
                self.cls_noticia.link = noticia.link
            elif hasattr(noticia, 'links'):
                try:
                    self.cls_noticia.link = noticia.links[0].href
                except:
                    print("Error con noticia.links[0].href en BuscaFeeds - trae_feed")
            self.cls_noticia.link = self.cls_noticia.link.replace("http://www.nuevaprensa.com.ve/articulo/", "http://www.nuevaprensa.com.ve/site/articulo/")
            if self.link_duplicado(self.cls_noticia.link):
                # print ("Link duplicado para", self.cls_noticia.titulo, self.cls_noticia.fecha)
                self.cls_noticia = None
                continue
            elif not self.cls_noticia.trae_datos(noticia):
                # print("Noticia vieja de", self.cls_noticia.titulo, self.cls_noticia.fecha)
                self.cls_noticia = None 
                continue 
            if self.cls_noticia.intro == '':
                self.cls_noticia.intro = self.cls_noticia.texto[:400]      
            if self.cls_noticia:
                guarda = 'INSERT IGNORE INTO noticias (fuente, seccion, fecha, titulo, intro,\
                          color, texto, link, abstract, keywords, description, h1, h2, h3,\
                          sonido, video) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
                          %s, %s, %s, %s)'
                datos_noticia = (self.cls_noticia.fuente, self.cls_noticia.seccion, self.cls_noticia.fecha, self.cls_noticia.titulo, \
                                self.cls_noticia.intro, self.cls_noticia.color, self.cls_noticia.texto, self.cls_noticia.link, \
                                self.cls_noticia.abstract, self.cls_noticia.keywords, self.cls_noticia.description, self.cls_noticia.h1, self.cls_noticia.h2, \
                                self.cls_noticia.h3, self.cls_noticia.sonido, self.cls_noticia.video)
                # print("Noticia es ", datos_noticia)
                try:
                    cur.execute(guarda, datos_noticia)
                    # print(cur.statement)
                except my.Error as err:
                    print("\nError guardando registro en noticias ", self.cls_noticia.fuente, self.cls_noticia.titulo)
                    # print ("Los datos son: ", datos_noticia)
                    # print (cur.statement)
                    print(format(err))
                self.con.commit()
                self.cls_noticia._id = cur.lastrowid
                if self.cls_noticia._id > 0: # solo para aquellos insertados no ignorados por duplicidad
                    # Guarda ahora las imagenes de la noticia
                    
                    for ima in self.cls_noticia.imagenes:
                        # print(ima)
                        texto = "insert ignore into not_imagenes (id, ancho,alto, link, caption) values (%s, %s, %s, %s, %s);"
                        datos_imagenes = (self.cls_noticia._id, ima['ancho'], ima['alto'], ima['link'], ima['caption'])
                        try:
                            cur.execute(texto, datos_imagenes)
                            # print(cur.statement)
                        except my.Error as err:
                            print("\nError guardando registro en imagenes de ", self.cls_noticia._id)
                            # print ("Los datos son: ", datos_noticia)
                            # print (cur.statement)
                            print(format(err))                    
    
                
                if self.cls_noticia._id > 0:
                    self.noticias +=1
                if self.cls_noticia.idioma == 'esp' or not self.cls_noticia.idioma:
                    self.cls_noticia.pn = ''
                    #Valora titulo
                    self.cls_noticia.clasifica_pn.valoracion(self.cls_noticia.titulo, self.datos.pondera['titulo'])            
                    #Valora intro
                    self.cls_noticia.clasifica_pn.valoracion(self.cls_noticia.intro, self.datos.pondera['intro']) 
                    #Valora keywords
                    self.cls_noticia.clasifica_pn.valoracion(self.cls_noticia.keywords, self.datos.pondera['keywords'])                
                    #Valora resto texto
                    self.cls_noticia.clasifica_pn.valoracion(self.cls_noticia.texto, self.datos.pondera['texto'])
                    if (self.cls_noticia.clasifica_pn.nneg>0):
                        pos = self.cls_noticia.clasifica_pn.npos
                        pos += self.cls_noticia.clasifica_pn.npos_frases
                        neg = self.cls_noticia.clasifica_pn.nneg
                        neg += self.cls_noticia.clasifica_pn.nneg_frases
                        
                        t_pos = self.cls_noticia.clasifica_pn.datos.num_pos
                        t_pos += self.cls_noticia.clasifica_pn.datos.num_frases_pos
                        t_neg = self.cls_noticia.clasifica_pn.datos.num_neg
                        t_neg += self.cls_noticia.clasifica_pn.datos.num_frases_neg
                        # ajustando los valores por el num de palabras en cada tabla de pos y neg, para igualar posibilidad
                        pos = pos *(1+(t_neg/(t_pos+t_neg)))
                        neg = neg * (1+(t_pos/(t_pos+t_neg)))
                        self.cls_noticia.ratio_pn = (pos/neg)

                        if self.cls_noticia.ratio_pn >=1:
                            self.cls_noticia.pn = 'pos'
                        else:
                            self.cls_noticia.pn = 'neg'
                    else:
                        #valor maximo para positivos, cuando no hay negativos
                        self.cls_noticia.ratio_pn = 999 
                        self.cls_noticia.pn = 'pos'             
                else:
                    self.cls_noticia.pn = self.cls_noticia.idioma
                    self.cls_noticia.ratio_pn = 0
    
                guarda = 'INSERT IGNORE INTO not_clasif (id, pn, ratio_pn) VALUES(%s, %s, %s)'
                # print("Guarda es ", guarda)
                datos_clas = (self.cls_noticia._id, self.cls_noticia.pn, self.cls_noticia.ratio_pn)
                # print("Noticia es ", datos_noticia)
                try:
                    cur.execute(guarda, datos_clas)
                except my.Error as err:
                    #print("Error in not_clasif", cur.statement, format(err))
                    pass 
                    # print("Error guardando registro en not_clasif ", guarda, datos_clas)
                    # print(format(err))
                self.con.commit()
                # Creando y guardando en not_relacion el registro para esta noticia
                guarda = 'INSERT IGNORE INTO not_relacion (id) VALUES('+str(self.cls_noticia._id)+");"
                try:
                    cur.execute(guarda)
                except my.Error as err:
                    print("Error in not_relacion", cur.statement, format(err))
                self.con.commit()                
        cur.close()
        self.con.close()
    
    def trae_contenido(self):
        '''
        url => str
        
        Trae las distintas noticias individuales de cada feed (rss, atom,    etc.)
        '''
        try:
            content = feedparser.parse(self.url)
        except:
            content = ''
        return content
    
    def link_duplicado(self, link):
        try:
            cur = self.con.cursor()
            t1 = "Select count(id) from noticias where link = '%s' and fuente = '%s'" % (self.cls_noticia.link, self.cls_noticia.fuente)
            try:
                cur.execute(t1)
                a = cur.fetchone()
                if a[0] == 0:
                    return False
                else:
                    return True
            except my.Error as err:
                print ("Error seleccionando de noticias para link = "+link, format(err))
            
        except my.Error as err:
            print("Algo ha fallado seleccionando de noticias para link"+link, format(err))
    