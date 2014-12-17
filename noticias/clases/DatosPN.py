#! /usr/bin/env python
#encoding:UTF-8
import sys
import mysql.connector as my
import traceback

from config import *
'''
Created on 05/04/2013

@author: aurelio

Genera las variables constantes requeridas en Noticia y Clasifica, como son las
palabras positivas o negativas de control de sus correspondientes tablas pos y neg, etc.


'''

class DatosPN(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.pos_neg = ['pos', 'neg'] # los dos tipos (positivo y negativo) que se analizan
        self.pos = [] # list de palabras positivas
        self.neg = [] # list of palabras negativas
        self.num_pos = 0 # numero de palabras positivas en tabla control pos,    con todas variaciones
        self.num_neg = 0 # numero de palabras negativas en tabla control neg,    con todas variaciones
        self.num_frases_pos = 0 # numero de frases positivas en tabla control, con variaciones
        self.num_frases_neg = 0 # numero de frases negativas en tabla control, con variaciones
        self.frases_pos = [] # list con las frases positivas de tabla, con variaciones
        self.frases_neg = [] # list con las frases negativas de tabla, con variaciones
        #Ponderación del valor de cada pal/frase según dónde esté.
        self.pondera = {'titulo':6, 'keywords':3, 'intro':2, 'texto':1} 
        #Siguientes para identificar el idioma
        self.cat = [] # las mil (+/-) palabras más comunes en catalan, de tabla comun_cat
        self.esp = [] # idem español
        self.eus = [] # idem euskera
        self.gal = [] # idem gallego
        self.eng = [] # idem inglés
        self.idiomas = [self.cat, self.esp, self.eus, self.gal, self.eng] #todos los idiomas
        self.nom_idioma = ['cat', 'esp', 'eus', 'gal', 'eng'] #ident de idiomas
        self.negaciones = ['no', 'ni', 'tampoco', 'nada', 'sin'] 
        self.quitar = ['script', 'style', 'img','noscript', 'object'] # tags a eliminar de textos
        self.con = my
        try:
            self.con = my.connect(**con_data)
            # self.con = pymysql.connect(**con_data)
            cur = self.con.cursor()             
            #Crea lista 'pos' de palabraS positivas (solo palabras, no frases)
            texto = 'select lcase(d.pal) as pal, c.tipo as tipo from pos c inner join dicc d on c.pal = d.origen \
                     and c.tipo = d.tipo where c.compuesto = 0 Union select lcase(c.pal) as pal, c.tipo as tipo from pos c \
                     left join dicc d on c.pal = d.origen and c.tipo = d.tipo where d.pal is null and c.compuesto = 0 order by pal;'
            try:
                cur.execute(texto)
                self.num_pos = cur.rowcount
                for row in cur:
                    pal = ''.join(row[0])
                    self.pos.append(pal)
            except my.Error as err:
                print("Error seleccionando conjunto pals positivas en DatosPN", format(err))
                print ("Se cerrará el programa")
                sys.exit()
            #Crea lista 'neg' de palabraS negativas (solo palabras, no frases)    
            texto = 'select lcase(d.pal) as pal, c.tipo as tipo from neg c inner join dicc d on c.pal = d.origen \
                     and c.tipo = d.tipo where c.compuesto = 0 Union select lcase(c.pal) as pal, c.tipo as tipo from neg c \
                     left join dicc d on c.pal = d.origen and c.tipo = d.tipo where d.pal is null and c.compuesto = 0 order by pal;'
            try:
                cur.execute(texto)
                for row in cur:
                    pal = ''.join(row[0])
                    self.neg.append(pal)     
                self.num_neg = cur.rowcount
            except my.Error as err:
                print("Error seleccionando conjunto pals negativas en DatosPN", format(err))    
                print ("Se cerrará el programa")
                sys.exit()                    
            #Crea lista de frases positivas
            texto = "select lcase(pal) as frase from pos where compuesto = 1";
            try:
                cur.execute(texto)
                for frase in cur:
                    frase = ''.join(frase)
                    self.frases_pos.append(frase)
                self.frases_pos = self.variaciones_frases(self.frases_pos) 
                self.num_frases_pos = len(self.frases_pos)  
            except my.Error as err:
                print("Error seleccionando conjunto frases positivas en DatosPN", format(err))   
                print ("Se cerrará el programa")
                sys.exit()       
            #Crea lista de frases negativas
            texto = "select lcase(pal) as frase from neg where compuesto = 1";
            try:
                cur.execute(texto)
                self.frases_neg = []
                for frase in cur:
                    frase = ''.join(frase)
                    self.frases_neg.append(frase)
                self.frases_neg = self.variaciones_frases(self.frases_neg)     
                self.num_frases_neg = len(self.frases_neg)
            except my.Error as err:
                print("Error seleccionando conjunto pals negativas en DatosPN", format(err))
                print ("Se cerrará el programa")
                sys.exit()
            #crear ahora indice de ignorados
            texto = "select lcase(esp) as pal from stopwords order by esp;";   
            try:  
                cur.execute(texto)
                self.ignorados = []
                for pal in cur:
                    pal = ''.join(pal)
                    self.ignorados.append(pal)
            except my.Error as err:
                print("Error seleccionando conjunto de stopwords en DatosPN", format(err))
                print ("Se cerrará el programa")
                sys.exit()
            #negativos son aquellas palabras que cambian el significado de otra
            self.negativos = ['no', 'ni', 'tampoco', 'nada', 'sin']
            #Punto de partida en la valoracion
            self.antes = {'pos':0.50, 'neg':0.50}
            #num de palabras encontradas en el texto para pos y neg
            # self.encontradas = {'pos':0, 'neg':0}
            # Ponderación subjetiva de las palabras pos/neg encontradas según de dónde vengan
            #Siguiente para identificar idioma
            if IDIOMAS:
                for nombre, idioma in zip(self.nom_idioma, self.idiomas):
                    texto = "Select pal from comun_"+nombre
                    cur.execute(texto)
                    for pal in cur.fetchall():
                        pal1 = ''.join(pal)
                        idioma.append(pal1.lower())
            cur.close()
        except:
            print("Error inicializando clase DatosPN", traceback.print_exc())
            print ("Se cerrará el programa")
            sys.exit()
        '''
        finally:
            print("Pals y frases positivas:", self.num_pos, self.num_frases_pos)
            print("Pals y frases negativas:", self.num_neg, self.num_frases_neg)
        '''
            
    def variaciones_frases(self, frases):
        for frase in frases:
            pals = frase.split(' ')
            for pal in pals:
                if pal.startswith('*'):
                    pal_antigua = pal
                    frases.remove(frase)
                    pal = pal[1:]
                    #buscar en dicc todas las variaciones posibles de esa frase
                    texto1 = "select pal from dicc where origen = '%s'" %pal
                    cur = self.con.cursor()
                    try:
                        cur.execute(texto1)
                        for pal in cur:
                            pal = ''.join(pal)
                            nueva = frase.replace(pal_antigua, pal)
                            frases.append(nueva)
                            # print ("Hemos añadido", nueva, "a la vieja", frase)
                    except my.Error as err:
                        print("Error seleccionando conjunto pals de dicc en variaciones frases en DatosPN", format(err))
                        print ("Se cerrará el programa")
                        sys.exit()
        frases = set(frases)
        return frases                    


