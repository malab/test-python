'''
Created on 2/11/2014

@author: aurelio
''' 
import re
import subprocess
from operator import itemgetter
from conexion import Connection
from freebase import bringNec


class Document(object):
    '''
    classdocs
    '''
    def addSentence(self, sentence, num):
        sent = Sentence(sentence, num)
        sent.index = num
        self.sentences.append(sent)

    def printDoc(self):
        pass
        """
        print(self. text)
        
        for k, tipo in tipos.items():
            print ("*"*50, k.upper(), "*"*50)
            tipo = [item for sublist in tipo for item in sublist]
            for pers in tipo:
                for sent in sents.values():
                        times = [item for item in sent if item[0] == pers]
                        if times:
                            desde = max(0, sent.index(times[0])-rango)
                            hasta = min(len(sent), sent.index(times[0])+rango)
                            newSent = [x[0] for x in sent]
                            print("----", pers, "-----\n"," ".join(newSent[desde:hasta]))
        """

    def countOccurrences(self):
        # summarize words in sentences by lemma and by lemma+tag
        dic_pos = {}
        dicc = {}
        
        interest = ['NP', 'W', 'Z']
        for cada in self.sentences:
            for word in cada.words:
                for i in interest:
                    if word.tag[:len(i)] == i:
                        if word.lemma not in dicc:
                            dicc[word.lemma] = 1
                        else:
                            dicc[word.lemma] +=1
                        if word.lemma+'-'+word.tag not in dic_pos:
                            dic_pos[word.lemma+'-'+word.tag] = 1
                        else:
                            dic_pos[word.lemma+'-'+word.tag] +=1
        # self.occurrences = sorted(dic.items(), key=itemgetter(0), reverse = False)
        self.occur_lemmas_tag = dic_pos
        self.occur_lemmas = dicc
        multiples = [(k,v) for (k, v) in dicc.items() if v > 1]
        for mult in multiples:
            det = [(k.split('-'), v) for (k, v) in dic_pos.items() if k.split('-')[0] == mult[0]]
            if len(det) > 1:
                print(det)
        """
        for key, value in self.occur_lemmas:
            print(key, value)
        """
    def findPos(self, pal):
        #first let's see if such word already exists in doc
        tag = [y.tag for x in self.sentences for y in x.words if y.text ==pal.text and y.tag !='']
        if tag:
            pal.tag = tag[0] #select first one ?
            self.sentences[pal.sentid].words[pal.index].tag = tag[0]

        else:
            #search in dicc
            cur = self.con.cursor()
            t = "select codigo, origen, offset from agiria.dicc d left join mywn.wn_words w \
            on d.pal = w.spa where pal = '%s' and w.pos = left(codigo,1);" % pal.text.lower()
            try:
                cur.execute(t)
                found = cur.fetchone()
                if found:
                    tag = found[0]
                    lema = found[1]
                    offs = found[2]
                    self.sentences[pal.sentid].words[pal.index].tag  = tag
                    self.sentences[pal.sentid].words[pal.index].lemma  = lema
                    self.sentences[pal.sentid].words[pal.index].offset  = offs + '-' + tag[:1].lower()
                else:
                    self.sentences[pal.sentid].words[pal.index].tag  = 'NP00V00'
            except:
                print("Error: ", t)
                self.sentences[pal.sentid].words[pal.index].tag  = 'NP00V00'

            
    def isPerson(self, word):
        pals = word.lemma.split('_')
        if len(pals) > 1:
            if not len([False for x in pals[1].upper() if x not in 'IVXDM']):
            #if pals[1] in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx', 'xxi', 'xxii', 'xxiii']:
                #it's king
                word.tag = 'NP00SP0'
                #word[2] = 'NP00SP0'
                return True
            if pals[0].lower() in ['padre', 'papa', 'san', 'santo']:
                word.tag = 'NP00SP0'
                #word[2] = 'NP00SP0'
                return True
        return False

    def romanNumber(self, word):
        if not len([False for x in word.text if x not in 'IVXDM']): #it's a century Change to date
            self.sentences[word.sentid].words[word.index].tag = 'W'
            self.sentences[word.sentid].words[word.index].lemma = '[s:'+word.text.lower()+']'
            return True
        return False

    def saveNec(self, word, nec):
        t = "Insert into necs (`word`, `res`, `name`, `notable`, `text`, `score`) values \
        (%s, %s, %s, %s, %s, %s)"
        values = (word, nec['res'], nec['nombre'], nec['propiedad'], nec['significado'], int(nec['score']))
        cur = self.con.cursor()
        try:
            cur.execute(t, values)
        except self.error as err:
            print("Error insertando necs", err, t, values)
        

    def checkFBase(self, word):
        t = "Select word, res from necs where word = '%s';" % word.text
        cur = self.con.cursor()
        cur.execute(t)
        row = cur.fetchone()
        if row:
            ner = row[1]
        else:
            nec = bringNec(word.text)
            if nec:
                ner = nec['res']
                self.saveNec(word.text, nec)
            else:
                ner = ''
        if ner == 'p':
            #print (nec, word.text, word.tag)
            tag = 'NP00SP0'
        elif ner == 'g':
            #print (nec, word.text, word.tag)
            tag = 'NP00G00'
        elif ner == 'o':
            tag = 'NP00O00'
            #print (nec, word.text, word.tag)
        else:
            #print (nec, word.text, word.tag)
            tag = 'NP00V00'
        
        if tag:
            if word.tag != tag:
                if ner:
                    print ("A CAMBIAR: ",tag, ner, "y en freeling:", word.text, word.tag)
                else:
                    print("NO ENCONTRADO: ",tag, ner, word.text, word.tag)
                #self.sentences(word.sentid).words(word.index).tag = tag
                return False
            else:
                if ner:
                    print("ACEPTADO: ", tag, ner, word.text, word.tag)
                    return True
                else:
                    print("NO ENCONTRADO: ",tag, ner, word.text, word.tag)
                    return True                    
        else:
            print ("NO TAG: ", nec, word.text, word.tag)
            return False
        
    def NERS(self):
        for sent in self.sentences:
            for word in sent.words:
                if word.tag == '':
                    self.findPos(word)
                if word.tag.startswith('NP'):
                    # print("checking:", word.text, word.tag)
                    changed = self.checkFBase(word)
                    if not changed:
                        if not self.isPerson(word):
                            if not self.romanNumber(word):
                                pass
                            
                    
    def finishing(self):
        self.NERS()
        self.countOccurrences()
    
        

    def __init__(self, file):
        '''
        Constructor
        '''
        self.text = file
        self.sentences = []
        new = Connection('mysql')
        self.error = new.error
        self.con = new.con
        self.dataFB = {}
        
#*****************************************************************       
class Sentence(object):
    '''
    classdocs
    '''
    
    def addWord(self, word):
        #word.text = word[0]
        if word.lemma:
            self.words.append(word)
            if word.index >= 0:
                self.words[word.index].prev1 = self.words[word.index-1]
                self.words[word.index-1].next1 = self.words[word.index]
                if word.index > 2:
                    self.words[word.index].prev2 = self.words[word.index-2]
                    self.words[word.index-2].next2 = self.words[word.index]
                


    def cleanALittle(self):
        frase = self.text
        frase = re.sub('bgcolor','',frase )
        frase = re.sub('style$','',frase )
        frase = re.sub('align=\"center\"', '', frase)
        frase = re.sub('align$','',frase )
        frase = re.sub('align=','',frase )
        frase = re.sub('center$','',frase )
        frase = re.sub('span$','',frase )
        frase = re.sub('\"right\"','',frase )
        frase = re.sub('right$','',frase )
        frase = re.sub('left$','',frase )
        frase = re.sub('col$','',frase )
        frase = re.sub('\"width\d*px\"', '', frase)
        frase = re.sub(self.hexaPattern, '', frase)
        frase = re.sub(self.hexaPattern2, '', frase)
        frase = re.sub('\d{1,3}px','',frase )
        frase = re.sub(r'(\d+)\s+(?=\d)', r'\1', frase)
        frase = re.sub(r'(\d+)\D{1,3}(\d+)', r'\1,\2', frase)
        frase = re.sub(r'colspan = \" \d \"', '', frase)
        frase = re.sub(r'JPGthumb', '', frase)
        frase = re.sub(r'jpg', '', frase)
        frase = re.sub(r'\\', '', frase)
        frase = re.sub(r'(\w*)\ss([\s|\.,])', r'\1s\2', frase)
        frase = re.sub(r'(\d{4})[,\.](\d{4})', r'\1, \2', frase)
        frase =  re.sub(r'([a-z]+)([A-Z]+)', r'\1, \2',  frase)
        frase = re.sub(r'(^[A-Z][a-z]+)(\d{1,4})', r'\1 \2', frase)
        
        self.text = frase
        

    def isDate(self, number, adjacents):
        #comes from quantitiesDates
        ind1 = [adjacents.index(x) for x in adjacents if x.text == number][0]
        lWords = ['en', 'de', 'desde', 'durante', 'años']
        rWords = ['-', ',', '(']
        """
        if re.findall(r'\d{4}',self.text):
            return True
        """
        if not number.isdigit():
            return False
        if ind1-1 >= 0:
            if adjacents[ind1-1].lemma in lWords:
                return True
            elif int(number) > 1500 and int(number) < 2100: # too general, but ...
                return True

        elif ind1 + 1 < len(adjacents):
            if adjacents[ind1+1].lemma in rWords:
                return True
        elif int(number) > 1500 and int(number) < 2100: # too general, but ...
            return True
        else:
            return False
        
    def changePos(self, word, tag):   
        word.tag = tag
        word.lemma = '[??:??/??/' + word.text + ':??.??:??]'
             
    def quantitiesDates(self):
        #check if in this sentence there are words tagged as quantities (Z) which should be tagged dates
        rango2 = 3 #number of words before and after the quantity
        cants = []
        cants.append([x.text for x in self.words if x.tag.startswith('Z')])
        for cant in cants[0]:
            try:
                num = int(cant)
            except:
                #its string
                num = 0
                posNum = re.findall(r'\d{4}',cant)
                if posNum:
                    num = int(posNum[0])
                else:
                    continue
            if num > 100 and num < 2100:
                try:
                    ind = [self.words.index(x) for x in self.words if x.text == cant][0]
                except:
                    continue
                desde = max(0, ind -rango2)
                hasta = min(len(self.words), ind +rango2)    
                # ind1 = cants.index(cant)
                if self.isDate(cant, self.words[desde:hasta]):
                    # ind1 = cants.index(cant)
                    #dates = changePos(dates, info, ind, 'W')
                    self.changePos(self.words[ind], 'W')
                    # cants[sent_num-1].pop(ind1)
    
    def freeling(self):
        self.cleanALittle()
        p1 = subprocess.Popen("analyzer_client agm2:%i <<<'%s' 1>&1" % (self.port1, self.text), shell=True, stdout=subprocess.PIPE,executable = '/bin/bash')
        (output1, err) = p1.communicate()
        output1 = output1.decode()  
        self.analyzed = output1.split("\n")
        num = 0
        for w in self.analyzed:
            x = w.split(' ')
            if len(x) > 1:
                #correct lemmas with words grouped like 'jaime_i._campamento' which should be considered two different lemmas
                if '._' in x[1]:
                    palsLemma = x[1].split('._')
                    palsText = x[0].split('._')
                    w0 = w1 = []
                    w0 = [palsText[0], palsLemma[0], '', 0, '']
                    y = Word(w0, num)
                    y.sentid = self.index
                    self.addWord(y)
                    num +=1
                    w1 = [palsText[1], palsLemma[1], '', 0, '']
                    y = Word(w1, num)
                    y.sentid = self.index
                    self.addWord(y)
                    num +=1
                    continue                    
                    
                y = Word(x, num)
                y.sentid = self.index
                self.addWord(y)
                num +=1

    def __init__(self, sentence, num):
        '''
        Constructor
        '''
        self.hexaPattern = re.compile(r'\"#[0-9a-fA-F]*?\"')
        self.hexaPattern2 = re.compile(r'#[0-9a-fA-F]*?')
        self.port1 = 50005
        self.port2 = 50006  
        self.text = sentence
        self.index = num
        self.words = []
        self.freeling()
        self.quantitiesDates()
        
#*****************************************************************
class Word(object):
    '''
    classdocs
    '''


    def __init__(self, word, num):
        '''
        Constructor
        '''
        if len(word) > 1:
            #self.word = word
            self.text = word[0]
            self.lemma = word[1]
            self.tag = word[2]
            self.prob = word[3]
            if len(word[4]) > 2:
                self.offset = str(word[4][:8])
            else:
                self.offset = ''
            self.index = num
            self.sentid = 0
            self.prev1 = ''
            self.prev2 = ''
            self.next1 = ''
            self.next2 = ''
            
        else:
            self.word = None
        