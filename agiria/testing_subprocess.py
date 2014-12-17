'''
Created on 10/10/2014

@author: aurelio
'''

import subprocess
import time
import operator
from word import Word
# import sys, os
from pprint import pprint
import mysql.connector as my
from decimal import *

"""
from subprocess import TimeoutExpired
from subprocess import call
from threading import Timer
from pprint import pprint
"""
import re


con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'mywn','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)

def commonWords(lang='es'):
    data = 'data/'
    if lang == 'es':
        fil = data + 'wes.csv'
    elif lang == 'en':
        fil = data + 'wen.csv'
    pals =  open(fil, 'rt').readlines()
    words = [pal[:-1] for pal in pals]
    for pal in pals:
        word = Word(pal)
        words.append(word.word)
    return [w for w in words if w['synset']]

def wordInfo(pal):
    return Word(pal)
    

def splitOut(group):
    p = group.split("\n")
    lista = []
    for l in p:
        n = l.count(" ", 0, 10) #node rank bases on spaces
        sp = l.split("/", 2)
        if len(sp) > 2:
            w = sp[2].replace("(", "").replace(")", "").split()
            dic = {'orden':999, 'rank':int(n/2), 'label1': sp[0], 'label2': sp[1], 'word':w[:3]}
            lista.append(dic)
    return lista

def buscaSent(word):
    #Using average since we do not have yet the correct sense acepcion) of the word
    t = "select avg(s.posscore), avg(s.negscore) from sentinet s \
    inner join mcr30.wei_spa_30_variant v \
    on s.id = v.offset and s.type = v.pos \
    group by v.word having v.word = '%s';" % word
    cur = con.cursor()
    cur.execute(t)
    retorno = cur.fetchall()
    if retorno:
        return retorno[0]
    else:
        return None

def sentencement(lista):
    posit = negat = float(0.0)
    for cada in lista:
        if len(cada) > 2:
            lem = cada.split()[1]
            pos = cada.split()[2]
            if pos[0] in "ANV" and pos[1] !='P': # only if adjective, noun or verb for sentiment analysis
                ret = buscaSent(lem)
                if ret:
                    posit += float(ret[0])
                    negat += float(ret[1])
    return posit - negat
        
def numberWords(tagged, dic):
    for word in dic:
        tag1 = tagged.split("\n")
        tag2 = [x.split() for x in tag1]
        tag3 = [x[0] for x in tag2 if len(x)]
        num = tag3.count(word['word'][0])
        if num == 1:
            dic[dic.index(word)]['orden'] = tag3.index(word['word'][0])
        elif num > 1:
            inicio = 0
            final = len(tag3)
            pases = 0
            for pal in dic:
                if pal['word'][0] == word['word'][0]:
                    pases +=1
                    inicio += tag3[inicio:final].index(pal['word'][0])
                    if pal['orden'] == 999:
                        if pases == 1:
                            dic[dic.index(pal)]['orden'] = tag3[inicio:final].index(pal['word'][0]) + inicio
                        elif pases == 2:
                            dic[dic.index(pal)]['orden'] = tag3[inicio+1:final].index(pal['word'][0]) + inicio + 1
                            inicio += tag3[inicio:final].index(pal['word'][0])
                        else:
                            rango = 12
                            num = tag3[max(0,dic.index(pal)-rango):min(dic.index(pal)+rango,final)].count(word['word'][0])
                            if num == 1:
                                dic[dic.index(pal)]['orden'] = tag3[max(0, \
                                    dic.index(pal)-rango):min(dic.index(pal)+rango,final)].index(pal['word'][0]) \
                                    +dic.index(pal) - rango
                            else:
                                rango2 = rango//4
                                x = 1
                                while x < 4:
                                    try:
                                        dic[dic.index(pal)]['orden'] = tag3[max(0, \
                                            dic.index(pal)-rango2/x):min(dic.index(pal)+rango2/x,final)].index(pal['word'][0]) \
                                            +dic.index(pal) - rango2/x 
                                        break
                                    except:                               
                                        x+=1
                        break
    return dic

cfg1 = 'es.cfg'
cfg2 = 'es_t.cfg'
proc1 = 50005
proc2 = 50006
# common words
#words = commonWords('es')

inicio = time.time()

# pprint(words)  
# print("Tiempo para cargar words: ", time.time() - inicio, " segundos")
#sys.exit()
# inicio = time.time()
frase = ""
#frase = "Juan vino llorando y suplicando por el perdón de María."
file = '/home/aurelio/desarrollo/python/agiria/agiria/documentos/es/durruti.txt'
if frase:
    file = frase.split("\n")
else:
    file = open(file, 'rt').readlines()

# p1 = subprocess.Popen("analyze -f %s <<<'%s' 1>&1" % (cfg1, file), shell = True, stdout = subprocess.PIPE, executable = '/bin/bash')
for frase in file:
    if frase:
        p1 = subprocess.Popen("analyzer_client agm2:%i <<<'%s' 1>&1" % (proc1, frase), shell=True, stdout=subprocess.PIPE,executable = '/bin/bash')
        (output1, err) = p1.communicate()
        output1 = output1.decode()  
        sentim = sentencement(output1.split("\n"))
        print(frase, "---------POS/NEG: ", sentim, "\n")
        p2 = subprocess.Popen("analyzer_client agm2:%i <<<'%s' 1>&1" % (proc2, output1), shell = True, stdout = subprocess.PIPE, executable='/bin/bash')
        (output2, err) = p2.communicate()
        output2 = output2.decode()
        splitted = splitOut(output2)
        ya = numberWords(output1, splitted)
        ya.sort(key=operator.itemgetter('orden'))
        """
        try:
            os.utime('data/testing.txt', None)
        except:
            open('data/testing.txt', 'a').close()
        """
        with open('data/durruti.txt', 'at') as file:
            for w in ya:
                ex = ""
                # ex = next((item for item in words if item["word"] == w['word'][1]), None) #if lemma in words
                try:
                    w_p = w['word'][1] + "." + w['word'][2][0].lower() + ".01" #lemma of word plus POS. it takes first meaning (01)
                    ex = wordInfo(w_p).word
                except:
                    print("error: ", w['word'])
                if ex:
                    w['wn'] = ex
                file.write(w['word'][0] + '\n')
                for cada, valor in w.items():
                    if cada == 'wn':
                        file.write("\t" + cada + '\n')
                        for uno, val in valor.items():
                            if val:
                                if isinstance(val, list):
                                    try:
                                        file.write("\t\t" + str(uno) + " : " + ", ".join(val) + "\n")
                                    except:
                                        print("error en ", w['word'][0], " en ", uno, val)
                                else:
                                    file.write("\t\t" + uno + " : " + str(val) + "\n")
                    else:
                        if isinstance(valor, list):
                            file.write("\t" + cada + " : " + ", ".join(valor) + "\n")
                        elif isinstance(valor, str):
                            file.write("\t" + cada + " : " + valor + "\n")
                        else:
                            file.write("\t" + cada + " : " + str(valor) + "\n")

final = time.time()
print("tiempo: ", final - inicio, " segundos")

