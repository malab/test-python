#! /usr/bin/env python
#encoding:UTF-8
import re
from nltk import wordpunct_tokenize
# from config import con_data

'''
Created on 04/11/2012

@author: aurelio
'''

class Clasifica():
    '''
    classdocs
    '''


    def __init__(self, datos):
        '''
        datos (clase DatosPN)
        Constructor
        '''
        self.npos = 0 # numero de veces que aparece alguna palabra positiva de las de self.pos, en texto analizado * pondera
        self.nneg = 0 # numero de veces que aparece alguna palabra negativa de las de self.neg, en texto analizado*ponder
        self.npos_frases = 0 #idem veces de frases positivas, multiplicados por pondera
        self.nneg_frases = 0 # veces frases negativas multiplicados por pondera
        self.datos = datos
        self.positivos = [] #lista de palabras positivas encontradas en texto
        self.negativos = [] #idem negativas
        self.frases_positivas = [] #lista de frases positivas encontradas en texto
        self.frases_negativas = [] #idem negativas
        self.veces = 0
     
    def valoracion(self,texto, pondera):
        #self.imprime()
        t_lower = texto.lower()
        # lo siguiente para comparaciones de pals pos y neg
        self.tokens = wordpunct_tokenize(t_lower)
        self.set_tokens = sorted(set(self.tokens))
        pos_temp = list(set(self.tokens) & set(self.datos.pos))
        neg_temp = list(set(self.tokens) & set(self.datos.neg))
        self.npos += len(pos_temp) * pondera
        self.nneg += len(neg_temp) * pondera
        self.positivos += pos_temp
        self.negativos += neg_temp      
        self.valora(pondera, pos_temp, neg_temp)
        #lo siguiente para comparacion de frases frases_pos y frases_neg
        self.valora_frase(texto, pondera)
        '''
        if pondera == 1:
            print (pondera, "Todos positivos:", self.positivos)
            print (pondera, "Todos negativos:", self.negativos)
        '''

    def valora(self, tipo, pos_temp, neg_temp):
        #usando conteo de palabras de control para pos y neg, ajustado por numero total de pos y neg 

        for cada in pos_temp:           
            if pos_temp.count(cada)> 0:
                #mira si precedida por alguna negación
                indice = self.tokens.index(cada)
                buscamos = self.tokens[indice-3:indice]
                hay_neg = list(set(buscamos) & set(self.datos.negaciones))
                if len(hay_neg) > 0:
                    # print("Hay negaciones en positivas: ", hay_neg, cada)
                    self.nneg += self.tokens.count(cada) * tipo
        #puntos_pos = log(pos*(self.num_pos+self.num_neg)/self.num_pos*
        for cada in neg_temp:
            #mira si precedida por alguna negación
            
            if neg_temp.count(cada)> 0:
                #mira si precedida por alguna negación
                indice = self.tokens.index(cada)
                buscamos = self.tokens[indice-3:indice]
                hay_pos = list(set(buscamos) & set(self.datos.negaciones))
                if len(hay_pos) > 0:
                    # print("Hay negaciones en negativas en: ", hay_pos, cada)
                    self.npos += self.tokens.count(cada) * tipo


    def valora_frase(self, texto, pondera):
        # tipos = [[self.datos.frases_pos], [self.datos.frases_neg]]
        # for tipo in self.datos.frases_pos:
        for frase in self.datos.frases_pos:
            # print ("Frase es ",frase)
            # print ("y texto es", texto)
            self.veces_frase(texto, frase)
            if self.veces > 0:
                self.npos_frases +=self.veces*pondera
                self.frases_positivas.append(frase)
                # print ("found", frase, self.veces, "(veces) en", texto)
        for frase in self.datos.frases_neg:
            # print ("Frase es ",frase)
            # print ("y texto es", texto)
            self.veces_frase(texto, frase)
            if self.veces > 0:
                self.nneg_frases += self.veces*pondera
                self.frases_negativas.append(frase)
                # print ("found", frase, self.veces, "(veces) en", texto)
        
    
    def lang_ident(self, texto):
        #Identica el idioma comparando los tokens del texto con las tablas-dict (comun_idio) para cada idioma
        # y seleccionando aquel idioma que contenga más coincidencias.
        todas = wordpunct_tokenize(texto)
        # solo minúsculas para evitar nombre propis
        V = set(todas)
        tokens = [pal for pal in V if pal.islower()]
        int_cat1 = list(set(tokens) & set(self.datos.cat))
        int_esp1 = list(set(tokens) & set(self.datos.esp))
        int_eus1 = list(set(tokens) & set(self.datos.eus))
        int_gal1 = list(set(tokens) & set(self.datos.gal))
        int_eng1 = list(set(tokens) & set(self.datos.eng))

        valor_idioma = [int_cat1, int_esp1, int_eus1, int_gal1, int_eng1]
        #Partimos de que el idioma será español y solo si hay más de diez coincidencias con otro idioma se cambia
        #Esto es para evitar textos cortos muy difíciles de distinguir entre idiomas
        inicial = 'esp'
        identificado = inicial
        conteo = len(int_esp1)
        for lang, valor in zip(self.datos.nom_idioma, valor_idioma):
            if len(valor) > conteo: 
                conteo = len(valor)
                identificado = lang
        if identificado != 'esp':
            print("idioma para noticia ", identificado)
        return identificado
    

    def veces_frase(self, a_str, sub):
        self.veces = a_str.count(sub, 0)
        '''
        start = 0
        self.veces = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            # yield start
            start += len(sub)
            self.veces +=1
        '''