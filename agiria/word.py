'''
Created on 11/10/2014

@author: aurelio
'''
import itertools
from collections import defaultdict
from nltk.corpus import wordnet as wn
import mysql.connector as my
from pprint import pprint


con_data = {'user':'root','password':'agm','host':'127.0.0.1', \
'database':'mywn','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)


class Word(defaultdict):
    
    def definition(self):
        return self.all["definition"]
    
    def synset(self):
        return self.all['synset']
    
    def offset(self):
        return self.all['offset']
    
    def lexname(self):
        return self.all['lexname']
    
    def lemmas(self):
        if self.word['synset']:
            lemmas = []
            l = self.all['lemmas']
            l = l.split(',')
            for cada in l:
                lemmas.append(cada)
            lemmas = [x for x in lemmas if x]
            if lemmas:
                return set(lemmas)
            else:
                return []
    
    def of_entailments(self):
        if self.word['synset']:
            entailments = []
            l = self.all['entailments']
            l = l.split(',')
            for cada in l:
                entailments.append(cada)
            entailments = [x for x in entailments if x]
            if entailments:
                return set(entailments)
            else:
                return [] 
    
    def entailments(self):
        if self.word['synset']:
            entails = []
            for cada in self.word['of_entailments']:
                if cada:
                    entails.append(self.nameFromOffset(cada))
            entails = [x for x in entails if x]
            if entails:
                try:
                    return self.mergeIntoOneList(entails)
                except:
                    listas =  set([inner for outer in entails for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
 
    def of_vgroups(self):
        if self.word['synset']:
            vgroups = []
            l = self.all['vgroups']
            l = l.split(',')
            for cada in l:
                vgroups.append(cada)
            vgroups = [x for x in vgroups if x]
            if vgroups:
                return set(vgroups)
            else:
                return [] 
            
    def vgroups(self):
        if self.word['synset']:
            vgroups = []
            for cada in self.word['of_vgroups']:
                if cada:
                    vgroups.append(self.nameFromOffset(cada))
            vgroups = [x for x in vgroups if x]
            if vgroups:
                try:
                    return self.mergeIntoOneList(vgroups)
                except:
                    listas =  set([inner for outer in vgroups for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
                                  
    def sinonyms(self):
        pass
        
    
    
    def of_antonyms(self):
        if self.word['synset']:
            antos = []
            l = self.all['antos']
            l = l.split(',')
            for cada in l:
                antos.append(cada)
            antos = [x for x in antos if x]
            if antos:
                return set(antos)
            else:
                return []

    def antonyms(self):
        if self.word['synset']:
            antos = []
            for cada in self.word['of_antonyms']:
                if cada:
                    antos.append(self.nameFromOffset(cada))
            antos = [x for x in antos if x]
            if antos:
                return set(antos)
            else:
                return []
        
    
    def of_hypernyms(self):
        if self.word['synset']:
            hypers = []
            l = self.all['hypers']
            l = l.split(',')
            for cada in l:
                hypers.append(cada)
            hypers = [x for x in hypers if x]
            if hypers:
                try:
                    return self.mergeIntoOneList(hypers)
                except:
                    listas =  set([inner for outer in hypers for inner in outer])
                    return self.mergeIntoOneList(listas)
                
            else:
                return []
            
    def hypernyms(self):   
        if self.word['synset']: 
            hypers = []
            for cada in self.word['of_hypernyms']:
                if cada: 
                    hypers.append(self.nameFromOffset(cada))
            hypers = [x for x in hypers if x]
            if hypers:
                try:
                    return self.mergeIntoOneList(hypers)
                except:
                    listas =  set([inner for outer in hypers for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def of_hyponyms(self):
        if self.word['synset']:
            hypos = []
            l = self.all['hypos']
            l = l.split(',')
            for cada in l:
                hypos.append(cada)
            hypos = [x for x in hypos if x]
            if hypos:
                try:
                    return self.mergeIntoOneList(hypos)
                except:
                    listas =  set([inner for outer in hypos for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def hyponyms(self):
        if self.word['synset']:
            hypos = []
            for cada in self.word['of_hyponyms']:
                if cada:
                    hypos.append(self.nameFromOffset(cada))
            hypos = [x for x in hypos if x]
            if hypos:
                try:
                    return self.mergeIntoOneList(hypos)
                except:
                    listas =  set([inner for outer in hypos for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
        
    def of_prod_meronyms(self):
        if self.word['synset']:
            pmeros = []
            l = self.all['pmeros']
            l = l.split(',')
            for cada in l:
                pmeros.append(cada)
            pmeros = [x for x in pmeros if x]
            if pmeros:
                try:
                    return self.mergeIntoOneList(pmeros)
                except:
                    listas =  set([inner for outer in pmeros for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def prod_meronyms(self):
        if self.word['synset']:
            pmeros = []
            for cada in self.word['of_prod_meronyms']:
                if cada:
                    pmeros.append(self.nameFromOffset(cada))
            pmeros = [x for x in pmeros if x]
            if pmeros:
                try:
                    return self.mergeIntoOneList(pmeros)
                except:
                    listas =  set([inner for outer in pmeros for inner in outer])  
                    return self.mergeIntoOneList(listas)    
            else:
                return []
            
    def of_prod_holonyms(self):
        if self.word['synset']:
            pholos = []
            l = self.all['pholos']
            l = l.split(',')
            for cada in l:
                pholos.append(cada)
            pholos = [x for x in pholos if x]
            if pholos:
                try:
                    return self.mergeIntoOneList(pholos)
                except:
                    listas =  set([inner for outer in pholos for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def prod_holonyms(self):
        if self.word['synset']:
            pholos = []
            for cada in self.word['of_prod_holonyms']:
                if cada:
                    pholos.append(self.nameFromOffset(cada))
            pholos = [x for x in pholos if x]
            if pholos:
                try:
                    return self.mergeIntoOneList(pholos)
                except:
                    listas =  set([inner for outer in pholos for inner in outer])   
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    
    def of_sub_meronyms(self):
        if self.word['synset']:
            smeros = []
            l = self.all['smeros']
            l = l.split(',')
            for cada in l:
                smeros.append(cada)
            smeros = [x for x in smeros if x]
            if smeros:
                try:
                    return self.mergeIntoOneList(smeros)
                except:
                    listas =  set([inner for outer in smeros for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def sub_meronyms(self): 
        if self.word['synset']:
            smeros = []
            for cada in self.word['of_sub_meronyms']:
                if cada:
                    smeros.append(self.nameFromOffset(cada))
            smeros = [x for x in smeros if x]
            if smeros:
                try:
                    return self.mergeIntoOneList(smeros)
                except:
                    listas =  set([inner for outer in smeros for inner in outer]) 
                    return self.mergeIntoOneList(listas)    
            else:
                return []
            
    def of_mem_meronyms(self):
        if self.word['synset']:
            mmeros = []
            l = self.all['mmeros']
            l = l.split(',')
            for cada in l:
                mmeros.append(cada)
            mmeros = [x for x in mmeros if x]
            if mmeros:
                try:
                    return self.mergeIntoOneList(mmeros)
                except:
                    listas =  set([inner for outer in mmeros for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def mem_meronyms(self):
        if self.word['synset']:
            mmeros = []
            for cada in self.word['of_mem_meronyms']:
                if cada:
                    mmeros.append(self.nameFromOffset(cada))
            mmeros = [x for x in mmeros if x]
            if mmeros:
                try:
                    return self.mergeIntoOneList(mmeros)
                except:
                    listas =  set([inner for outer in mmeros for inner in outer])        
                    return self.mergeIntoOneList(listas)   
            else:
                return []
            
    def of_sub_holonyms(self):
        if self.word['synset']:
            sholos = []
            l = self.all['sholos']
            l = l.split(',')
            for cada in l:
                if cada:
                    sholos.append(cada)
            sholos = [x for x in sholos if x]
            if sholos:
                try:
                    return self.mergeIntoOneList(sholos)
                except:
                    listas =  set([inner for outer in sholos for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def sub_holonyms(self):
        if self.word['synset']:
            sholos = []
            for cada in self.word['of_sub_holonyms']:
                if cada:
                    sholos.append(self.nameFromOffset(cada))
            sholos = [x for x in sholos if x]
            if sholos:
                try:
                    return self.mergeIntoOneList(sholos)
                except:
                    listas =  set([inner for outer in sholos for inner in outer]) 
                    return self.mergeIntoOneList(listas)     
            else:
                return []
            
    def of_mem_holonyms(self):
        if self.word['synset']:
            mholos = []
            l = self.all['mholos']
            l = l.split(',')
            for cada in l:
                if cada:
                    mholos.append(cada)
            mholos = [x for x in mholos if x]
            if mholos:
                try:
                    return self.mergeIntoOneList(mholos)
                except:
                    listas =  set([inner for outer in mholos for inner in outer])
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def mem_holonyms(self):
        if self.word['synset']:
            mholos = []
            for cada in self.word['of_mem_holonyms']:
                if cada:
                    mholos.append(self.nameFromOffset(cada))
            mholos = [x for x in mholos if x]
            if mholos:
                try:
                    return self.mergeIntoOneList(mholos)
                except:
                    listas =  set([inner for outer in mholos for inner in outer])  
                    return self.mergeIntoOneList(listas)
            else:
                return []
            
    def nameFromOffset(self, offset ):
        retorno = []
        t = "select pal from es_synsets where offset = '%s';" % offset.strip()
        cur = con.cursor()
        cur.execute(t)
        if cur._rowcount> 0:
            for cada in cur.fetchall():
                if cada:
                    retorno.append(cada[0])
            return retorno
        else:
            #search wordnet in mcfr30 database
            t = "select word from mcr30.wei_spa_30_variant where offset = '%s';" % offset.strip()
            cur = con.cursor()
            cur.execute(t)
            if cur._rowcount:
                retorno = []
                for cada in cur.fetchall():
                    if cada:
                        retorno.append(cada[0].decode())
                return retorno
            else:
                #search wordnet in mcfr30 database in english
                t = "select word from mcr30.wei_eng_30_variant where offset = '%s';" % offset.strip()
                cur = con.cursor()
                cur.execute(t)
                if cur._rowcount:
                    retorno = []
                    for cada in cur.fetchall():
                        if cada:
                            retorno.append(cada[0].decode())
                    return retorno
                else:
                    return None
    def mergeIntoOneList(self, lists):
        new = []
        for l in lists:
            if isinstance(l, list):
                new = new + l
            else:
                new.append(l)
        return new
        
    def nullWord(self, word):
        self.word = {}
        self.word['word'] = word
        self.word['definition'] = ""
        self.word['synset'] = ""
        self.word['offset'] = ""
        self.word['lemmas'] = ""
        self.word['lexname'] = ""
        # self.word['of_sinonyms'] = self.of_sinonyms()
        self.word['of_antonyms'] = ""
        self.word['of_hypernyms'] = ""
        self.word['of_hyponyms'] = ""
        self.word['of_prod_meronyms'] = ""
        self.word['of_prod_holonyms'] = ""
        self.word['of_sub_meronyms'] = ""
        self.word['of_sub_holonyms'] = ""
        self.word['of_mem_meronyms'] = ""
        self.word['of_mem_holonyms'] = ""
        self.word['of_entailments'] = ""
        self.word['of_vgroups'] = ""
        
        self.word['antonyms'] = ""
        self.word['hypernyms'] = ""
        self.word['hyponyms'] = ""
        self.word['prod_meronyms'] = ""
        self.word['prod_holonyms'] = ""
        self.word['sub_meronyms'] = ""
        self.word['sub_holonyms'] = ""
        self.word['mem_meronyms'] = ""
        self.word['mem_holonyms'] = ""
        self.word['entailments'] = ""
        self.word['vgroups'] = ""
        
    def __init__(self, word):
        '''
        Constructor
        '''
        t = "Select * from es_synsets where synset = '%s';" % word
        cur = con.cursor()
        try:
            cur.execute(t)
        except my.Error as err:
            print("error: ", err, t)
            
        self.record = []
        self.record = cur.fetchone()
        if cur._rowcount == 0:
            """
            #search in mcr30.wei_spa
            t = "Select * from mcr30.wei_spa_30_variant where word = '%s';" % word
            cur = con.cursor()
            cur.execute(t)
            self.record = []
            self.record = cur.fetchone()
            if cur._rowcount == 0:       
                print("Palabra ", word, " no esta en wordnet")
                self.nullWord(word)
            else:
                print("Palabra ", word, " encontrada en mcr30")
            """
            self.nullWord(word)
            # print("Palabra ", word, " no esta en wordnet")
        else:
            columns = tuple( [d[0] for d in cur.description] )
            self.all = []
            self.all.append(dict(zip(columns, self.record)))
            self.all = self.all[0]
            self.word = {}
            self.word['word'] = word
            self.word['definition'] = self.definition()
            self.word['synset'] = self.synset()
            self.word['offset'] = self.offset()
            self.word['lemmas'] = self.lemmas()
            self.word['lexname'] = self.lexname()
            # self.word['of_sinonyms'] = self.of_sinonyms()
            self.word['of_antonyms'] = self.of_antonyms()
            self.word['of_hypernyms'] = self.of_hypernyms()
            self.word['of_hyponyms'] = self.of_hyponyms()
            self.word['of_prod_meronyms'] = self.of_prod_meronyms()
            self.word['of_prod_holonyms'] = self.of_prod_holonyms()
            self.word['of_sub_meronyms'] = self.of_sub_meronyms()
            self.word['of_sub_holonyms'] = self.of_sub_holonyms()
            self.word['of_mem_meronyms'] = self.of_mem_meronyms()
            self.word['of_mem_holonyms'] = self.of_mem_holonyms()
    
            self.word['antonyms'] = self.antonyms()
            self.word['hypernyms'] = self.hypernyms()
            self.word['hyponyms'] = self.hyponyms()
            self.word['prod_meronyms'] = self.prod_meronyms()
            self.word['prod_holonyms'] = self.prod_holonyms()
            self.word['sub_meronyms'] = self.sub_meronyms()
            self.word['sub_holonyms'] = self.sub_holonyms()
            self.word['mem_meronyms'] = self.mem_meronyms()
            self.word['mem_holonyms'] = self.mem_holonyms()
            self.word['of_entailments'] = self.of_entailments()
            self.word['of_vgroups'] = self.of_vgroups()
            self.word['entailments'] = self.entailments()
            self.word['vgroups'] = self.vgroups()
"""
s = Word('teléfono')
pprint(s.word)
"""

        