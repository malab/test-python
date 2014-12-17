'''
Created on 04/10/2013

@author: aurelio
'''

import re

from pal import Pal


class Sentence():
    '''
    classdocs
    '''
    # pals = []
    
    def inicializa(self):
        # self.sentence = sent
        
        self.pals = []
        self.top = ['top']
        self.verbs = ['co-v', 'dverb', 'vsubord', 'top', 'aux', 'modnorule', 'modnomatch', 'obj-prep', 
                      'cc', 'co-v', 'adj-mod', 'att', 'pred']
        self.verbs1 = ['grup-verb', 'vser', 'verb-pass' , 'grup-verb-inf', 'subord-part', 'verb-pass', 
                       'subord-ger', 's-a-ms', 's-a-mp', 's-a-fs', 'parti-flex', 'forma-ger',  'ger',
                       'sn', 'vaux', '¡infaux-ser']
        self.dobjs = ['dobj']
        self.dobjs1 = ['sn', 'patons', 'subord', 'coor-n']
        self.iobjs = ['iobj', 'dep']
        self.iobjs1 = ['patons', 'grup-sp']
        self.subjects = ['subj', 'subj-pac' ]
        self.subjects1 = ['cc', 'sn', 'subord', 'coor-n']
        self.subord = ['subord-mod', 'vsubord']
        self.subord1 = ['subord', 'subord-rel', 'grup-verb']
        self.circs = ['cc']
        self.circs1 = ['grup-sp', 'sadv', 'sn', 'data', 'sp-de', 'subord-part', 'coor-sp', 'subord-ger',  'sadv']
        self.neg = ['espec']
        self.neg1 = ['neg', 'sadv']
        self.adverbs = ['cc', 'espec']
        self.adverbs1 = ['sadv', 'grup-sp', 'subord-part']
        
    def add_pal(self, pal, num):
        w = Pal(pal, self.con)
        w.num = num
        self.pals.append(w)
        
    def save_sent(self):
        t = "insert into sentences (doc_id, sent_id, sentence) values ('%s', '%s', '%s')" \
        % (self.doc_id, self.sent_id, self.sentence)
        cur = self.con.cursor()
        try:
            cur.execute(t)
        except my.Error as err:
            print("Error saving sent. ", cur.statement)
    
    def set_sentence(self, sentencia):
        sentencia = re.sub(r'([a-z]|[áéíóúñ])-([a-z]|[áéíóúñ])', '\\1\\2',sentencia) # join words with '-' such as 'som-brero'
        sentencia = sentencia.replace('\x96', '-') # replace long - with single -
        sentencia = sentencia.replace("'", "''")  # take care of apostrophe
        sentencia = sentencia.replace('\x0C', '')
        
        self.sentence = sentencia
        
    def set_con(self, con):
        self.con = con
        
    def set_sent_id(self, num):
        self.sent_id = num
        
    def set_doc_id(self, doc_id):
        self.doc_id = doc_id
            
    def busca_ordinadas(self):
        pass
    
    def search_verb(self, pals):
        return [x[2] for x in pals if x[6] in self.verbs and x[7] in self.verbs1]
        
    
    def search_subject(self, pals):
        return [x[2] for x in pals if x[6] in self.subjects and x[7] in self.subjects1]
    
    def search_dobject(self, pals):
        return [x[2] for x in pals if x[6] in self.dobjs and x[7] in self.dobjs1]
    
    def search_iobject(self, pals):
        return [x[2] for x in pals if x[6] in self.iobjs and x[7] in self.iobjs1]
    
    def busca_cuando(self, pals):
        pass
    
    def search_circunstancial(self, pals):
        return [x[2] for x in pals if x[6] in self.circs and x[7] in self.circs]
    
    def search_people(self, pals):
        return [x[2] for x in pals if x[3] == 'NP00SP0']
    
    def search_organizations(self, pals):
        return [x[2] for x in pals if x[3] == 'NP00O00']
    
    def busca_otros(self, pals):
        return [x[2] for x in pals if x[3] == 'NP00V00']
    
    def search_dates(self, pals):
        return [x[2] for x in pals if x[3].startswith('W')]
    
    def search_places(self, pals):
        return [x[2] for x in pals if x[3] == 'NP00G00']
    
    def search_amounts(self, pals):
        return [x[2] for x in pals if x[3].startswith('Z')]
    
    def es_negativa (self, pals):
        pass
    
    def is_question (self, pals):
        q = [x[3] for x in pals if x[3] == 'Fit']
        if len(q):
            return True
        else:
            return False
        
    def is_negation(self, pals):
        q = [x[3] for x in pals if x[3] == 'RN']
        if len(q):
            return True
        else:
            return False        
    def es_respuesta (self, pals):
        pass
    
    def is_interjection(self, pals):
        q = [x[3] for x in pals if x[3] == 'Fat']
        if len(q):
            return True
        else:
            return False        
    
    def __iter__(self):
        return self
    
    def next(self):
        if self.i<len(self.lst)-1:
            self.i += 1         
            return self.lst[self.i]
        else:
            raise StopIteration
        
    def meaning(self):
        t = "select sent_id, sentence from sentences where doc_id = %i order by sent_id;" % self.doc_id
        cur = self.con.cursor()
        cur.execute(t)
        sents = cur.fetchall()
        for sent in sents:
            t = "select pal_id, token, lemma, tag, node1, node2, label, label2 \
            from pals where document = %i and sentence = %i order by pal_id, node1, node2;" \
            % (self.doc_id, sent[0])
            cur = self.con.cursor()
            cur.execute(t)
            pals = cur.fetchall()
            pals = [(pal[0], pal[1].decode(), pal[2].decode(), pal[3].decode(),pal[4], pal[5], pal[6].decode(), pal[7].decode()) for pal in pals]
            print('*'*60)
            print(sent[1].decode('UTF-8'))
            for rec in pals:
                for pal in rec:
                    print(pal," ", end='')
                print()
            print('-'*60)
            
            self.meaning_details(pals)
            self.save_details()
            
            
    def meaning_details(self, pals):
        self.top = self.search_verb(pals)
        self.subject = self.search_subject(pals)
        self.dobj = self.search_dobject(pals)
        self.iobj = self.search_iobject(pals)
        self.people = self.search_people(pals)
        self.places = self.search_places(pals)
        self.organizations = self.search_organizations(pals)
        self.dates = self.search_dates(pals)
        self.amounts = self.search_amounts(pals)
        print('subject', self.subject)
        print('top', self.top)
        print('dobj', self.dobj)
        print('iobj', self.iobj)
        print('people', self.people)
        print('places', self.places)
        print('organizations', self.organizations)
        print('dates', self.dates)
        print('amounts', self.amounts)
        
        
    def save_details(self):
        pass
        t = "insert into sents1 ("    
        
    def __init__(self):
        '''
        Constructor
        '''
        self.inicializa()
        