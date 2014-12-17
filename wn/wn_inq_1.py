
import mysql.connector as my
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
verbo = re.compile('verb|^adverb', re.IGNORECASE)
nombre = re.compile('noun', re.IGNORECASE)
adj = re.compile('adj', re.IGNORECASE)
adv = re.compile('adv', re.IGNORECASE)
art = re.compile('art', re.IGNORECASE)
prep = re.compile('prep', re.IGNORECASE)
idiom = re.compile('idiom', re.IGNORECASE)
pron = re.compile('pron', re.IGNORECASE)
conj = re.compile('conj', re.IGNORECASE)
modal = re.compile('mod', re.IGNORECASE)

change = {'adj':'a', 'noun':'n', 'verb':'v'}


def search_type(tipo):
    verb = verbo.search(tipo)
    noun = nombre.search(tipo)
    adject = adj.search(tipo)
    adverb = adv.search(tipo)
    artic = art.search(tipo)
    prepos = prep.search(tipo)
    idiom1 = idiom.search(tipo)
    pron1 = pron.search(tipo)
    conj1 = conj.search(tipo)
    modal1 = modal.search(tipo)
    retorno = []
    if verb and len(verb.group()):
        retorno.append(verb.group())
    if noun and len(noun.group()): 
        retorno.append(noun.group())
    if adject and len(adject.group()): 
        retorno.append(adject.group())
    if adverb and len(adverb.group()): 
        retorno.append(adverb.group())
    if artic and len(artic.group()): 
        retorno.append(artic.group())
    if prepos and len(prepos.group()): 
        retorno.append(prepos.group())
    if idiom1 and len(idiom1.group()): 
        retorno.append(idiom1.group())
    if pron1 and len(pron1.group()): 
        retorno.append(pron1.group())
    if conj1 and len(conj1.group()): 
        retorno.append(conj1.group())
    if modal1 and len(modal1.group()): 
        retorno.append(modal1.group())
    if not retorno:
        print(("No encontrado el tipo: ", tipo))
    return retorno
    
def similarity(gloss):
    dord= {}
    try:
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(gloss)
    except:
        print(("error con ", gloss))   
        return dord 
    sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)
    sims = list(sims[0])
    """
    print(pal)
    print(gloss)
    print('-'*60)
    """
    for i, cada in enumerate(sims):
        dord[i]=[cada, gloss[i]]
    dord = sorted(dord, key=dord.get, reverse=True)
    return dord

    

def save_offset(pal, acep, offset):
    t = "update inquirer set wn = '%s' where pal_en = '%s' and acep = '%s';" % (offset, pal, acep)
    try:
        cur.execute(t)
    except my.Error as err:
        print(("error updating inquirer",err, t))

con = my.connect(**con_data)
cur = con.cursor()

t = "select distinct i.pal_en, i.acep, info from inq_info ii \
    right join inquirer i on i.pal_en = ii.pal and i.acep = ii.acep order by i.pal_en, i.acep;"
cur.execute(t)
todos = cur.fetchall()
for cada in todos:
    tipo = ''
    pal = cada[0]
    acep = cada[1]
    info = cada[2]
    if info:
        infos = info.split(':')
        tipo = infos[0].strip()
        info = infos[1].strip()
        tipo = search_type(tipo)
        if tipo and tipo[0] in change:
            tipo = change[tipo[0]]
        else:
            tipo = 'r'
    pal = pal.replace("'", "\\'")
    if tipo:
        t = "select v.offset, v.pos, v.sense, s.gloss from mcr30.wei_eng_30_variant v \
        inner join mcr30.wei_eng_30_synset s on v.offset = s.offset and v.pos = s.pos \
        where v.word = '%s' and v.pos = '%s';" % (pal, tipo)
    else:
        t = "select v.offset, v.pos, v.sense, s.gloss from mcr30.wei_eng_30_variant v \
        inner join mcr30.wei_eng_30_synset s on v.offset = s.offset and v.pos = s.pos \
        where v.word = '%s';" % pal    
    try:
        cur.execute(t)
    except my.Error as err:
        print(("error in selecting from mcr30.variant ", t, err))
    all = cur.fetchall()
    offset = []
    pos = []
    sense = []
    gloss = []
    ret = []
    if len(all) > 1 and tipo:
        gloss.append(info)
        for each in all:
            offset.append(each[0].decode())
            pos.append(each[1].decode())
            sense.append(each[2])
            gloss.append(each[3].decode())
        ret = similarity(gloss) 
    elif len(all) == 1:
        offset.append(all[0][0].decode())
        pos.append(all[0][1].decode())
        sense.append(all[0][2])
        gloss.append(all[0][3].decode())   

    if ret and len(ret) > 1:
        primero = ret[1] - 1 #one deducted because it was added as first gloss before the for each
        offset=offset[primero]
        pos = pos[primero]
        sense = sense[primero]
        # info2 = gloss[primero] #gloss tiene un valor más añadido antes del for each
        full = offset+'-'+pos+'-'+str(sense).rjust(2, '0')
        # print("*"*60, "\n", pal, full, info," **** ",  gloss[primero+1])
        save_offset(pal, acep, full)
    elif len(all) == 1:
        primero = 0
        offset=offset[primero]
        pos = pos[primero]
        sense = sense[primero]
        # info2 = gloss[primero] #gloss tiene un valor más añadido antes del for each
        full = offset+'-'+pos+'-'+str(sense).rjust(2, '0')
        # print("*"*60, "\n", pal, full, info," **** ",  gloss[primero+1])
        save_offset(pal, acep, full)
    else:
        print(("Nada encontrado para ", pal, "(", acep, ") como ", tipo, offset, info," **** "))
        continue

    

    