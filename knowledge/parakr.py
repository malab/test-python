import nltk
import mysql.connector as my


con_data = {'user':'root','password':'agm','host':'127.0.0.1', \
'database':'ngrams','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)

imprime = False

def search_commons(tipo, limit):
    t = "select pal from en_1gram2  where freq > 1500000 \
and tipo = '%s' order by freq desc limit %s;" % (tipo, limit)
    cur = con.cursor()
    cur.execute(t)
 
    return cur.fetchall()

def search_lemmas(pals, tipo):
    retorno = []
    cur = con.cursor()
    for pal in pals:
        t = "select origen from db_noticias.dicc_eng where pal = '%s' and left(codigo, 2) ='%s';" % (pal, tipo)
        cur.execute(t)
        p = cur.fetchone()
        if p:
            p = p[0]
            retorno.append(p)
    return set(retorno)
    

def anal_pal2(pal2):
    t = "select pal1 from en_2gram2 where pal2 = '%s' and freq > 3000 order \
by freq desc limit 300;" % pal2
    cur = con.cursor()
    cur.execute(t)
    all = cur.fetchall()
    all = [x[0].decode() for x in all]
    nombres = [x for x in all if x in nouns and len(x) > 2]
    print(("x"*60))
    print((pal2, "nombres\n",[" ".join((x, pal2)) for x in nombres]))
    adjetivos = [x for x in all if x in adjs and len(x) > 2]
    print((pal2, "adjetivos\n",[" ".join((x, pal2)) for x in adjetivos]))
    verbos = [x for x in all if x in verbs and len(x) > 2]
    print((pal2, "verbos\n",[" ".join((x, pal2)) for x in verbos]))
    adverbios = [x for x in all if x in adverbs and len(x) > 2]
    print((pal2, "adverbios\n",[" ".join((x, pal2)) for x in adverbios]))
    preposiciones = [x for x in all if x in adps and len(x) > 2]
    print((pal2, "preposiciones\n",[" ".join((x, pal2)) for x in preposiciones]))
    pronombres = [x for x in all if x in prons and len(x) > 2]
    print((pal2, "pronombres\n",[" ".join((x, pal2)) for x in pronombres]))
    mas_preposic = [x for x in all if x in prts and len(x) > 2]
    print((pal2, "mas_preposic\n",[" ".join((x, pal2)) for x in mas_preposic]))
    conjunciones = [x for x in all if x in conjs and len(x) > 2]
    print((pal2, "conjunciones\n",[" ".join((x, pal2)) for x in conjunciones]))
    
def anal_pal1(pal1):
    t = "select pal2 from en_2gram2 where pal1 = '%s' and freq > 3000 order \
by freq desc limit 300;" % pal1
    cur = con.cursor()
    cur.execute(t)
    all = cur.fetchall()
    all = [x[0].decode() for x in all]
    nombres = [x for x in all if x in nouns and len(x) > 2]
    print(("-"*60))
    print((pal1, "nombre\n",[" ".join((pal1, x)) for x in nombres]))
    adjetivos = [x for x in all if x in adjs and len(x) > 2]
    print((pal1, "adjetivos\n",[" ".join((pal1, x)) for x in adjetivos]))
    verbos = [x for x in all if x in verbs and len(x) > 2]
    print((pal1, "verbos\n",[" ".join((pal1, x)) for x in verbos]))
    adverbios = [x for x in all if x in adverbs and len(x) > 2]
    print((pal1, "adverbios\n",[" ".join((pal1, x)) for x in adverbios]))
    preposiciones = [x for x in all if x in adps and len(x) > 2]
    print((pal1, "preposiciones\n",[" ".join((pal1, x)) for x in preposiciones]))
    pronombres = [x for x in all if x in prons and len(x) > 2]
    print((pal1, "pronombres\n",[" ".join((pal1, x)) for x in pronombres]))
    mas_preposic = [x for x in all if x in prts and len(x) > 2]
    print((pal1, "mas_preposic\n",[" ".join((pal1, x)) for x in mas_preposic]))
    conjunciones = [x for x in all if x in conjs and len(x) > 2]
    print((pal1, "conjunciones\n",[" ".join((pal1, x)) for x in conjunciones]))

nouns = search_commons('NOUN', 8000)
nouns = [x[0].decode().lower() for x in nouns if not x[0].decode().endswith('.')
             and x[0].decode().isalpha() and nltk.pos_tag([x[0].decode()])[0][1] == 'NN']
nouns = sorted(list(search_lemmas(nouns, 'NN')))
if imprime:
    print(("\nnombres", len(nouns), "\n", nouns[:200]))


verbs = search_commons('VERB', 6000)
verbs = [x[0].decode().lower() for x in verbs if not x[0].decode().endswith('.')
             and x[0].decode().isalpha() and nltk.pos_tag(nltk.word_tokenize('I ' + x[0].decode()))[1][1].startswith('V')]
verbs = sorted(list(search_lemmas(verbs, 'VB')))
if imprime:
    print(('\nverbos', len(verbs), '\n', verbs[:200]))



adjs = search_commons('ADJ', 6000)
adjs = [x[0].decode().lower() for x in adjs if not x[0].decode().endswith('.')
             and x[0].decode().isalpha() and nltk.pos_tag([x[0].decode()])[0][1] == 'JJ']
adjs = sorted(list(set(adjs)))
if imprime:
    print(('\nadjetivos', len(adjs), '\n', adjs[:200]))


adverbs = search_commons('ADV', 2000)
adverbs = [x[0].decode().lower() for x in adverbs if not x[0].decode().endswith('.')
             and x[0].decode().isalpha() and nltk.pos_tag([x[0].decode()])[0][1] == 'RB']
adverbs = sorted(list(set(adverbs)))
if imprime:
    print(('\nadverbios', len(adverbs), '\n', adverbs[:200]))


foreign = search_commons('X', 3000)
foreign = [x[0].decode().lower() for x in foreign if not x[0].decode().endswith('.')
             and x[0].decode().isalpha()]
foreign = sorted(list(set(foreign)))
if imprime:
    print(('\nextranjeras', len(foreign), '\n', foreign[:200]))

dets = search_commons('DET', 100)
dets = [x[0].decode().lower() for x in dets if not x[0].decode().endswith('.')
             and x[0].decode().isalpha() and nltk.pos_tag([x[0].decode()])[0][1] == 'DT']
dets = sorted(list(set(dets)))
if imprime:
    print(('\ndeterminantes', len(dets), '\n', dets[:200]))

adps = search_commons('ADP', 300)
adps = [x[0].decode().lower() for x in adps if not x[0].decode().endswith('.')
             and x[0].decode().isalpha() and nltk.pos_tag([x[0].decode()])[0][1] == 'IN']
adps = sorted(list(set(adps)))
if imprime:
    print(('\npreposiciones', len(adps), '\n', adps[:200]))

prons = search_commons('PRON', 100)
prons = [x[0].decode().lower() for x in prons if not x[0].decode().endswith('.')
             and x[0].decode().isalpha() and nltk.pos_tag([x[0].decode()])[0][1] == 'PRP']
prons = sorted(list(set(prons)))
if imprime:
    print(('\npronombres', len(prons), '\n', prons[:200]))

prts = search_commons('PRT', 50)
prts = [x[0].decode().lower() for x in prts if not x[0].decode().endswith('.')
             and x[0].decode().isalpha()]
prts = sorted(list(set(prts)))
if imprime:
    print(('\nmas preposiciones', len(prts), '\n', prts[:200]))       

conjs = search_commons('CONJ', 17)
conjs = [x[0].decode().lower() for x in conjs if not x[0].decode().endswith('.')
             and x[0].decode().isalpha() and nltk.pos_tag([x[0].decode()])[0][1] == 'CC']
conjs = sorted(list(set(conjs)))
if imprime:
    print(('\nconjunciones', len(conjs), '\n', conjs[:200]))

tot = 0
import random
for i in range(5):
    rn = random.randint(1,len(adjs))
    anal_pal2(adjs[rn])
    anal_pal1(adjs[rn])




            
