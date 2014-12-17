'''
Created on 24/10/2014

@author: aurelio
'''
import subprocess
import operator
import mysql.connector as my
from copy import deepcopy
from nltk.corpus import wordnet as wn

con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)
cur = con.cursor()

cfg1 = 'es.cfg'
cfg2 = 'es_t.cfg'
proc1 = 50005
proc2 = 50006
notValid = ''# 'DISPRS' #'DIS' #'ACFINVPRSVWZ' #first letter of tag e.g. V=verb, A = adjective
signif = 'ACFNRSVWZ'

def offsets(word, pos):
    t = "select distinct offset from mywn.wn_words where spa = %s and pos = %s;"
    values = (word, pos)
    cur.execute(t, values)
    prim = cur.fetchone()
    if prim:
        return prim[0] + '-' + pos
    else:
        return None

def synset(offset, pos):
    t = "select distinct eng from mywn.wn_words where offset = %s and pos = %s;"
    values = (offset, pos)
    cur.execute(t, values)
    # select first one (!)
    prim = cur.fetchone()
    if prim:
        syns = wn.synsets(prim[0])
        syn = [x for x in syns if x.pos() == pos] #double checking that pos is correct for this synset
        # return first one (!)
        if syn:
            return syn[0].name()
        else:
            return None
    else:
        return None

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


def processStep1(frase):
    p1 = subprocess.Popen("analyzer_client agm2:%i <<<'%s' 1>&1" % (proc1, frase), shell=True, stdout=subprocess.PIPE,executable = '/bin/bash')
    (output1, err) = p1.communicate()
    output1 = output1.decode()
    return  output1

def processStep2(step1):
    p2 = subprocess.Popen("analyzer_client agm2:%i <<<'%s' 1>&1" % (proc2, step1), shell = True, stdout = subprocess.PIPE, executable='/bin/bash')
    (output2, err) = p2.communicate()
    output2 = output2.decode()
    splitted = splitOut(output2)    
    return splitted

def numberWords(tagged, dic):
    # Returns the original order to the dic (returned by process2 and ranked by labels)
    for word in dic:
        # tag1 = tagged.split("\n")
        tag2 = [x.split() for x in tagged]
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

def improveIt(original, numbered):
    for a, cada in enumerate(original):
        if cada == numbered[a]['word'][1]:
            pass
        else:
            cambio = [x for x in numbered if x['orden']== 999]
            if cambio:
                if cambio[0]['word'][1] == cada:
                    cambio[0]['orden'] = a
                    numbered.sort(key=operator.itemgetter('orden'))
    return numbered
        
    
def main():
    file = '/home/aurelio/desarrollo/python/agiria/agiria/documentos/es/durruti.txt'
    file = open(file, 'rt').readlines()
    """
    frase = "Nació en León el 14 de julio de 1897, en el seno de familia numerosa, sin más subsidios que la caridad humillante. 
    Siete hermanos y una hermana, pocas letras y mucha ira contenida, ira que debió de irse desbordando a medida que los niños se hacían hombres, sobre todo si se tiene en cuenta la influencia del padre, anarquista, y el momento social, que sensibilizaba muy pronto al proletario capaz de discurrir. "
    file = frase.split("\n")
    """
    for frase in file:
        print(frase)
        new = []
        new_ = []
        new_0 = []
        new_1 = []
        new_2 = []
        new_4 = []
        new2 = []
        new2_ = []
        if frase:
            oput1 = processStep1(frase)
            oput2 = processStep2(oput1)
            oput1 =  oput1.split("\n")
            op2 = [x.split(' ') for x in oput1]
            op2Copy = deepcopy(op2)
            namesCopy = [x[1] for x in [y for y in op2Copy] if x[0]!= '']
            for a in op2:
                if a and a[0]:
                    # op2 = a.split(' ')
                    if a[2][0] not in notValid:
                        # print(op2[1], op2[2])
                        new.append(a[0])
                    if a[2][0] in signif:
                        new_.append(a[0])
                    new_0.append(a[0])
                    new_1.append(a[1])
                    new_2.append(a[2])
                    """
                    if a[4] == '-' and a[2][0] in 'ANV':
                        offset = offsets(a[1], a[2][0].lower())
                    new_4.append(offset)
                    """
                    if len(a[4]) > 5:
                        syn = synset(a[4][:-2], a[2][0].lower() )
                        if syn != None:
                            a[4] = syn
                        else:
                            a[4] = ''
                    else:
                        a[4] = ''
                    new_4.append(a[4])

            ya = numberWords(oput1, oput2)
            ya.sort(key=operator.itemgetter('orden'))
            retorno = improveIt(namesCopy, ya)
            try:
                retorno = [x for x in retorno if x['word'][2][0] not in notValid]
            except:
                pass
                #print("ERROR")
            """
            rank= 99                   
            for a in retorno:
                print(a)
                if a:
                    if 'sub' in a['label1'] and 'subord' in a['label2']:
                        rank = a['rank']
                    elif a['rank'] > rank:
                        pass
                    else:
                        rank = 99
                        new2.append(a['word'][0])
            """
            print(" ".join(new))
            print(" ".join(new_0))
            print(" ".join(new_1))
            print(" ".join(new_2))
            #print(" ".join(new_4))
            print(new_4)
            print(" ".join(new_))
            #print('-'*40)
            #print(" ".join(new2))
            print('*'*40, "\n")
                    
                    

if __name__ == '__main__':
    main()