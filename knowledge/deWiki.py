'''
Created on 31/10/2014

@author: aurelio
'''
import time as tm
import re, sys
import subprocess
from pymongo import MongoClient as mc
from operator import itemgetter


inicio = tm.time()
#port numbers for freeling in server
port1 = 50005
port2 = 50006   
client = mc('localhost', 27017)
mydb = client.wiki
col = mydb.pages

topic = {"title" : 'Instituto de Crédito Oficial'}

f = col.find_one(topic)
if f and len(f['redirect']) > 10:
    redireccion = re.sub('#REDIRECT', '',f['redirect']).strip()
    topic = {"title" : redireccion}
    f = col.find_one(topic)
    if not f:
        print("no encontrado")
        sys.exit()
elif not f or len(f['texto']) < 80:
    print("no encontrado")
    sys.exit()  
find1 = tm.time()

file = f['texto'].split("\n")

rango = 20
global sents
sents = {}
global sent_num
sent_num = 0
global sentences
sentences = {}
global people 
people = []
peop = ['nacer', 'morir', 'enterrar', 'estudiar', 'graduar', 'exponer', 'formular',  'criticar', 'formular', 'escribir', 'abandonar', 'ocupar', 'nombrar', 
          'mudar', 'elegir', 'leer', 'reanudar', 'contemporáneo', 'biografía', 'trabajar', 'novelista', 'autor', 'poeta', 'santo', 'san', 'obispo', 'papa', 'mártir',
          'rey', 'noble', 'monarca', 'conde', 'duque', 'marqués', 'escritor', 'inventor', 'político', 'gobernante', 'ministro', 
          'gobernador', 'presidente', 'científico', 'magistrado', 'parlamentario', 'congresista', 'director', 'libro', ]
global loc 
loc = []
local = ['capital', 'comarca', 'ciudad', 'pueblo', 'aldea', 'villa', 'pòblación', 'barrio', 'ruta', 'carretera', 'autovía', 
       'autopista', 'puerto', 'localidad', 'municipio', 'provincia', 'comunidad', 'abadía', 'pedanía', 'valle', 'asentamiento', 
       'término', 'confinar', 'sur', 'norte', 'este', 'oeste', 'barranco', 'orilla', 'río', 'mar', 'área', 'extensión',
       'aglutinar', 'situado', ]
global org
org = []
global misc 
misc = []
global dates 
dates = []
global cants 
cants = []
global tipos 
tipos = {'gente': people, 'lugares':loc, 'organizaciones': org, 'varios': misc, 'fechas': dates, 'cantidades':cants}


def freeling(frase):
    global sent_num
    sent_num +=1
    frase = cleanALittle(frase)
    sentences[sent_num] = frase
    p1 = subprocess.Popen("analyzer_client agm2:%i <<<'%s' 1>&1" % (port1, frase), shell=True, stdout=subprocess.PIPE,executable = '/bin/bash')
    (output1, err) = p1.communicate()
    output1 = output1.decode()  
    return output1.split("\n")

def processSentences(op, frase):
    global people, loc, org, misc, dates, cants
    info = []
    for cada in op:
        w = cada.split(' ')
        if len(w) > 1:
            info.append(w)
    sents[sent_num] = info
    people.append([x[0] for x in info if x[2][4:6] == 'SP'])
    loc.append([x[0] for x in info if x[2][4:6] == 'G0'])
    org.append([x[0] for x in info if x[2][4:6] == 'O0'])
    misc.append([x[0] for x in info if x[2][4:6] == 'V0'])  
    dates.append([x[0] for x in info if x[2] == 'W'])
    cants.append([x[0] for x in info if x[2].startswith('Z')])
    return sents

def quantitiesDates(sents):
    global dates, cants, sent_num
    info = sents[sent_num]
    rango2 = 3 #number of words before and after the quantity
    for cant in cants[sent_num-1]:
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
                ind = [info.index(x) for x in info if x[0] == cant][0]
            except:
                continue
            desde = max(0, ind -rango2)
            hasta = min(len(info), ind +rango2)    
            ind1 = cants[sent_num-1].index(cant)
            if isDate(cant, info[desde:hasta]):
                ind1 = cants[sent_num-1].index(cant)
                dates = changePos(dates, info, ind, 'W')
                cants[sent_num-1].pop(ind1)

hexaPattern = re.compile(r'\"#[0-9a-fA-F]*?\"')
hexaPattern2 = re.compile(r'#[0-9a-fA-F]*?')

def isDate(number, adjacents):
    #Not used. assuming years if 100>number<2150
    ind1 = [adjacents.index(x) for x in adjacents if x[0] == number][0]
    frase = " ". join([x[0] for x in adjacents])
    if re.findall(r'\d{4}',frase):
        return True
    if ind1-1 >= 0:
        if adjacents[ind1-1][1].lower() == 'en':
            return True
        if adjacents[ind1-1][1].lower() == 'de':
            return True
        if adjacents[ind1-1][1].lower() == 'durante':
            return True
        elif adjacents[ind1-1][1].lower() == 'años':
            return True
        elif adjacents[ind1-1][1] == ',':
            return True
        elif adjacents[ind1-1][1].lower() == 'años':
            return True
    elif ind1 + 1 < len(adjacents):
        if adjacents[ind1+1][1] == '-':
            return True
        elif adjacents[ind1+1][1] == ',':
            return True
        elif adjacents[ind1+1][1] == '(':
            return True
    else:
        return False

def summarizeNers():
    global people, loc, org, misc, dates, cants
    people =  sorted(set([item for sublist in people for item in sublist]))
    loc = sorted(set([item for sublist in loc for item in sublist]))
    org = sorted(set([item for sublist in org for item in sublist]))
    misc =  sorted(set([item for sublist in misc for item in sublist]))
    dates =  sorted(set([item for sublist in dates for item in sublist]))
    cants =  sorted(set([item for sublist in cants for item in sublist]))
    
def isPerson(word):
    pals = word[1].split('_')
    if len(pals) > 1:
        if pals[1] in 'IVX':
            #it's king
            word[2] = 'NP00SP0'
    return word
    
def NERS(sents):
    for a in sents:
        for word in sents[a]:
            word1 = isPerson(word)
            if word1 != word:
                sents[a][sents[a]].index(word)

    return sents
    
def printInfo():
    global tipos, sents, people, loc, org, misc, dates, cants
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
    
def changePos(dates, info, ind, pos):
    new = info[ind]
    new[2] = pos
    dates.append([new[0]])
    return dates

def cleanALittle(frase):
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
    
    return frase

def countOccurrences(sents):
    dic = {}
    interest = ['NP', 'W', 'Z']
    for k, v in sents.items():
        for word in v:
            for i in interest:
                if word[2][:len(i)] == i:
                    if word[1]+'-'+word[2] not in dic:
                        dic[word[1]+'-'+word[2]] = 1
                    else:
                        dic[word[1]+'-'+word[2]] +=1
    for key, value in sorted(dic.items(), key=itemgetter(0), reverse = False):
        print(key, value)

def main(file):
    
    for frase in file:
        if frase:
            op = freeling(frase) #analyze sentence in freeling
            intermedio = tm.time()
            sents = processSentences(op, frase)             
    occur = countOccurrences(sents)     
    quantitiesDates(sents)
    NERS(sents)
    intermedio2 = tm.time()
    
    print("INFORMACION SOBRE ", f['title'])
    for sentence in sentences.values():
        print(sentence)
    summarizeNers()
    printInfo()
    
    final = tm.time()
    print("Tiempo buscando en db:", find1-inicio, "segundos")
    print("Tiempo en freeling:", intermedio-find1, "segundos")
    print("Tiempo preparando:", intermedio2-intermedio, "segundos")
    print("Tiempo restante:", final-intermedio2, "segundos")
    
if __name__ == '__main__':
    main(file)

