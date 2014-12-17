'''
Created on 14/10/2014

@author: aurelio
'''

from bs4 import BeautifulSoup as bs
import mysql.connector as my
import urllib.request as ur
import time
# import sys
import re


con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)

link = "http://www.wordreference.com/es/translation.asp?tranword="
allPos = {}
global ERRORES
ERRORES = 0
global n
n = 46180

def readPos(file):
    with open(file, 'rt') as f:
        lines = f.readlines()
        for line in lines:
            line = line[:-1]
            if line:
                datos = line.split(':')
                allPos[datos[0].strip()] = datos[1].strip()


def importWords():
    global n
    cur = con.cursor()
    #This is the standard

    t = "select s.pal, s.offset, s.synset, n.gloss from senti_new s inner join sentinet n on s.offset = n.id \
     where s.spa = '' order by s.pal limit %s, 100000;" % n
    """
    t = "select s.pal, s.offset, s.synset, n.gloss from senti_new s \
    inner join senti_trans_old2 n on s.offset = n.offset \
    and s.pal = n.en_word group by s.pal, s.offset limit %s, 25000;" % n
    """
    cur.execute(t)
    todos = cur.fetchall()
    return todos

def bringArticle(pal):
    global n
    miLink = link + pal
    header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error 
    req = ur.Request(miLink, headers = header)
    try:
        art1 = ur.urlopen(req)
    except: 
        print("error en Comunicación ", pal)
        global ERRORES
        ERRORES +=1
        if ERRORES > 9:
            print("-+"*20, time.ctime())
            time.sleep(600)
            ERRORES = 0
            n = n-12
            main()
        return None
    art2 = art1.read()
    art1.close()
    if isinstance(art2, str):
        if "WordReference can't translate this exact phrase" in art2 or \
        "No translation found for " in art2:
            return None
    elif isinstance(art2, bytes):
        if "WordReference can't translate this exact phrase" in art2.decode()  or \
        "No translation found for " in art2.decode():
            return None        
    art = bs(art2)
    #print(art)
    #time.sleep(0.25)
    return art

                
def findPals_1(sig):
    pals = []
    palAnt = info2Ant = pal_esAnt = transAnt = tr_esAnt = ''
    for cada in sig:
        word = cada.find(class_='FrWrd')
        if word:
            word = word.contents[0].string
            palAnt = word
        else:
            word  = palAnt
        if word:
            info1 = word
            try:
                info2 = word.find_next('td').contents[0].string
            except:
                info2 = ''
            info2 = info2.replace("(", '').replace(")", '')
            if info2:
                info2Ant = info2
            else:
                info2 = info2Ant
            pal_es = cada.find(class_='ToWrd')
            if pal_es:
                pal_es = pal_es.contents[0].string
                pal_esAnt = pal_es
            else:
                pal_es = pal_esAnt
            tipo = cada.find(class_="tooltip POS2")
            if tipo:
                tipo = tipo.contents[0].string
            else:
                tipo = ''
            trans = cada.find(class_='FrEx')
            if trans:
                trans = trans.contents[0].string
                transAnt = trans
            else:
                trans = transAnt
            tr_es = cada.find(class_='ToEx')
            if tr_es:
                tr_es = tr_es.contents[0].string
                tr_esAnt = tr_es
            else:
                tr_es = tr_esAnt
            if not tipo and pals:
                pals[-1]['example'] = str(trans).strip()
                pals[-1]['ejemplo'] = str(tr_es).strip()
            elif word:
                if ',' in str(pal_es).strip():
                    pal2 = pal_es.split(',')
                    for p in pal2:
                        p2 = {}
                        p2['word'] = str(p.strip())
                        p2['info1'] = str(info1).strip()
                        p2['info2'] = str(info2).strip()
                        p2['example'] = str(trans).strip()
                        p2['ejemplo'] = str(tr_es).strip()
                        p2['tipo'] = str(tipo).strip()  
                        pals.append(p2)   
                else:     
                    pal = {}
                    pal['word'] = str(pal_es).strip()
                    pal['info1'] = str(info1).strip()
                    pal['info2'] = str(info2).strip()
                    pal['example'] = str(trans).strip()
                    pal['ejemplo'] = str(tr_es).strip()
                    pal['tipo'] = str(tipo).strip()
                    pals.append(pal)
    return pals
                # print("de tabla1 ","pal:", pal, "esp:", pal_es, "info2:", info2, "tipo:", tipo, "trans:", trans, "tr_es:", tr_es)
                
def findPals_2(word, sig):
    pals = []
    info1Ant = info2Ant = pal_esAnt = transAnt = tr_esAnt = ''
    for cada in sig:
        info1 = cada.find(class_='FrWrd')
        if info1:
            info1 = info1.contents[0].string
            info1Ant = info2Ant = pal_esAnt = transAnt = tr_esAnt = ''
            info1Ant = info1
            
        else:
            info1  = info1Ant
        if info1:
            try:
                info2 = info1.find_next('td').contents[0].string
            except:
                info2 = ''
            info2 = info2.replace("(", '').replace(")", '')
            if info2:
                info2Ant = info2
            else:
                info2 = info2Ant
            pal_es = cada.find(class_='ToWrd')
            if pal_es:
                pal_es = pal_es.contents[0].string
                pal_esAnt = pal_es
            else:
                pal_es = pal_esAnt
            tipo = cada.find(class_="tooltip POS2")
            if tipo:
                tipo = tipo.contents[0].string
            else:
                tipo = ''
            trans = cada.find(class_='FrEx')
            trans = cada.find(class_='FrEx')
            if trans:
                trans = trans.contents[0].string
                transAnt = trans
            else:
                trans = transAnt
            tr_es = cada.find(class_='ToEx')
            if tr_es:
                tr_es = tr_es.contents[0].string
                tr_esAnt = tr_es
            else:
                tr_es = tr_esAnt
            if not tipo and pals:
                pals[-1]['example'] = str(trans).strip()
                pals[-1]['ejemplo'] = str(tr_es).strip()
            elif word:
                if ',' in str(pal_es).strip():
                    pal2 = pal_es.split(',')
                    for p in pal2:
                        p2 = {}
                        p2['word'] = str(p.strip())
                        p2['info1'] = str(info1).strip()
                        p2['info2'] = str(info2).strip()
                        p2['example'] = str(trans).strip()
                        p2['ejemplo'] = str(tr_es).strip()
                        p2['tipo'] = str(tipo).strip()  
                        pals.append(p2)   
                else:                   
                    pal = {}
                    pal['word'] = str(pal_es).strip()
                    pal['info1'] = str(info1).strip()
                    pal['info2'] = str(info2).strip()
                    pal['example'] = str(trans).strip()
                    pal['ejemplo'] = str(tr_es).strip()
                    pal['tipo'] = str(tipo).strip()
                    pals.append(pal)
    return pals
                #print("de tabla2 ", "pal:", pal, "info1:", info1, "esp:", pal_es, "info2:", info2, "tipo:", tipo, "trans:", trans, "tr_es:", tr_es)

def searchWord(det):
    w = det[0]
    w = w.replace('_', '%20')
    #tipo = det[1]
    #mean = det[2]
    pals = []
    if w:
        art = bringArticle(w)
        if not art:
            art = bringArticle(w)
            return pals

        # search the table with word
        tabla1 = art.find('table', class_='WRD', id='') #table with single form of word
        tabla2 = art.find('table', class_='WRD', id='compound_forms') #table with compunded forms of word
        #words1 = tabla1.find_all(class_= 'ToWrd')
        #words2 = tabla2.find_all(class_= 'ToWrd')
        if tabla1:
            tr1 = tabla1.find_all('tr')
            pals = findPals_1(tr1)
        if tabla2:
            tr2 = tabla2.find_all('tr')
            if pals:
                pals = pals + findPals_2(w, tr2)
            else:
                pals = findPals_2(w, tr2)

        #for compunded forms (two or more words in an offset/sense)
        #pals = findPals_2(tr2)


    return pals
    
def savePal(wen, pos, sense, offset, pal, gloss):
    if pal:
        # print("Guardado", n, wen, pos, pal['word'], pal['tipo'], allPos[pal['tipo']] )
        t = "insert ignore into senti_trans (en_word, info1, info2, en_pos, sense, sp_word, sp_pos, \
        offset, example, ejemplo, gloss) values \
        (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
        pal['info1'] = re.sub('<[^>]*>', '', pal['info1'])
        pal['info2'] = re.sub('<[^>]*>', '', pal['info2'])            
        values = (wen, pal['info1'], pal['info2'], pos, sense, pal['word'], 
                            pal['tipo'], offset, pal['example'], pal['ejemplo'], gloss)
        cur = con.cursor()
        try:
            cur.execute(t, values)
        except my.Error as err:
            print("ERROR - ", err, t, values)

def sameSense(wen, enpos, sense, offset, pals, gloss):
    #save only if both senses, english/spanish are equivalent
    global n
    for pal in pals:
        try:
            if allPos[pal['tipo']] == enpos:
                savePal(wen, enpos, sense, offset, pal, gloss)
            elif pal['tipo'] == '?' and enpos == 'v' and pal['word'][-2:] in ['ar', 'er', 'ir']:
                savePal(wen, enpos, sense, offset, pal, gloss) 
            #else:
            #    print(".....NO...Guardado", n, wen, enpos, pal['word'], pal['tipo'], allPos[pal['tipo']] )
        except: #save it anyway
            print("Error_ ", wen, enpos, sense, offset, pal, gloss)
            savePal(wen, enpos, sense, offset, pal, gloss)
        
        
def main():
    global n
    pals = importWords()
    palAnterior = ''
    wsAnt = {}
    for pal in pals:
        # print(n, pal)
        wen = pal[0]
        offset = pal[1]
        syn = pal[2]
        det = syn.split('.')
        enpos = det[1]
        sense = det[2]
        gloss = pal[3]
        if wen == palAnterior:
            ws = wsAnt
        else:
            ws = searchWord(det)
            wsAnt = ws
            palAnterior = wen
        if ws:
            sameSense(wen, enpos, sense, offset, ws, gloss)
            #print(n, wen)
        """
        else:
            print(n, wen, " not found")
        """
        print(n, wen)
        n+=1 
if __name__ == '__main__':
    readPos('data/sp_pos.txt')
    main()
        

        
