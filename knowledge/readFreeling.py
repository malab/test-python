'''
Created on 2/11/2014

@author: aurelio
''' 
import re
import subprocess
from operator import itemgetter

hexaPattern = re.compile(r'\"#[0-9a-fA-F]*?\"')
hexaPattern2 = re.compile(r'#[0-9a-fA-F]*?')
port1 = 50005
port2 = 50006  

class Document(object):
    '''
    classdocs
    '''
    def addSentence(self, sentence):
        sent = Sentence(sentence)
        sent.text = sentence
        self.sentences.append(sent)

    def printDoc(self):
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

    def countOccurrences(self):
        dic = {}
        interest = ['NP', 'W', 'Z']
        for cada in self.sentences:
            for word in cada.words:
                for i in interest:
                    if word[2][:len(i)] == i:
                        if word[1]+'-'+word[2] not in dic:
                            dic[word.lemma+'-'+word.tag] = 1
                        else:
                            dic[word.lemma+'-'+word.tag] +=1
        for key, value in sorted(dic.items(), key=itemgetter(0), reverse = False):
            print(key, value)
        

    def __init__(self, file):
        '''
        Constructor
        '''
        self.text = file
        self.sentences = []
        
#*****************************************************************       
class Sentence(object):
    '''
    classdocs
    '''
    
    def addWord(self, word):
        #word.text = word[0]
        self.words.append(word)

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
        frase = re.sub(hexaPattern, '', frase)
        frase = re.sub(hexaPattern2, '', frase)
        frase = re.sub('\d{1,3}px','',frase )
        frase = re.sub(r'(\d+)\s+(?=\d)', r'\1', frase)
        frase = re.sub(r'(\d+)\D{1,3}(\d+)', r'\1,\2', frase)
        frase = re.sub(r'colspan = \" \d \"', '', frase)
        frase = re.sub(r'JPGthumb', '', frase)
        frase = re.sub(r'jpg', '', frase)
        frase = re.sub(r'\\', '', frase)
        frase = re.sub(r'(\w*)\ss\s', r'\1s ', frase)
        frase = re.sub(r'(\d{4})[,\.](\d{4})', r'\1, \2', frase)
        frase =  re.sub(r'([a-z]+)([A-Z]+)', r'\1 \2',  frase)
        
        self.text = frase
        
    def isDate(self, number, adjacents):
        ind1 = [adjacents.index(x) for x in adjacents if x[0] == number][0]
        lWords = ['en', 'de', 'durante', 'años']
        rWords = ['-', ',', '(']
        if re.findall(r'\d{4}',self.text):
            return True
        if ind1-1 >= 0:
            if adjacents[ind1-1][1].lower() in lWords:
                return True

        elif ind1 + 1 < len(adjacents):
            if adjacents[ind1+1][1] in rWords:
                return True
        else:
            return False
        
    def changePos(self, word, tag):   
        word[2] = tag
        word.tag = tag
             
    def quantitiesDates(self):
        rango2 = 3 #number of words before and after the quantity
        cants = []
        cants.append([x[0] for x in self.words if x[2].startswith('Z')])
        for cant in cants:
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
                    ind = [self.words.index(x) for x in self.words if x[0] == cant][0]
                except:
                    continue
                desde = max(0, ind -rango2)
                hasta = min(len(self.words), ind +rango2)    
                ind1 = cants.index(cant)
                if self.isDate(cant, self.words[desde:hasta]):
                    ind1 = cants.index(cant)
                    #dates = changePos(dates, info, ind, 'W')
                    self.changePos(self.words[ind], 'W')
                    # cants[sent_num-1].pop(ind1)
    
    def freeling(self):
        self.cleanALittle()
        p1 = subprocess.Popen("analyzer_client agm2:%i <<<'%s' 1>&1" % (port1, self.text), shell=True, stdout=subprocess.PIPE,executable = '/bin/bash')
        (output1, err) = p1.communicate()
        output1 = output1.decode()  
        self.analyzed = output1.split("\n")
        for w in self.analyzed:
            x = w.split(' ')
            y = Word(x)
            self.addWord(y)

    def __init__(self, sentence):
        '''
        Constructor
        '''
        self.text = sentence
        self.words = []
        self.freeling()
        
#*****************************************************************
class Word(object):
    '''
    classdocs
    '''


    def __init__(self, word):
        '''
        Constructor
        '''
        if len(word) > 1:
            self.word = word
            self.text = self.word[0]
            self.lemma = self.word[1]
            self.tag = self.word[2]
        