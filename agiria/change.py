import sys, os
import time as tm
import nltk
import mysql.connector as my
from nltk.tokenize import word_tokenize, wordpunct_tokenize, sent_tokenize

t1 = tm.time()

os.chdir('../agiria/agiria')
sys.path.append(os.getcwd())
from basic_agiria import BasicAgiria as ba

con_data = {'user':'root','password':'agm','host':'127.0.0.1', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)
cur = con.cursor()

def exists_mfn(noun, code):
    texto = "select codigo from dicc where origen = (select origen from dicc where \
pal = '%s' and codigo = '%s');" % (noun, code)
    #print(t)
    try:
        cur.execute(texto)  
    except:
        return False
    todos = cur.fetchall()
    mfns = []
    for cada in todos:
        mfns.append(cada[0][2:3])
    mfns = set(mfns)
    return mfns
        

def change_noun(noun, code, mfn = '', sp = ''):
    """Examples
    autor NCMS000
    autora NCFS000
    autores NCMP000
    periodista NCCS000 (C is for common)
    periodistas NCCP000
    """
    if code[1:2] == 'P': #proper name
        return (noun, code)
    if not mfn or code[2:3] == 'C':
        mfn = code[2:3]
    mfns = exists_mfn(noun, code)
    if not mfns or mfn.upper() not in mfns:
        mfn = code[2:3]
    if not sp:
        sp = code[3:4]
    ncode = (code[:2] + mfn + sp + code[-3:]).upper()
    texto = "select pal from dicc where origen = (select origen from dicc where \
pal = '%s' and codigo = '%s') and codigo = '%s';" % (noun, code, ncode)
    #print(t)
    try:
        cur.execute(texto)
    except:
        return (noun, code)
    if cur._rows[0][0]:
        return (cur._rows[0][0].decode(), ncode)
    else:
        return (noun, code)

def change_adj(adj, code, mfn = '', sp = ''):
    """Examples
    bonita AQ0FS0
    bonito AQ0MS0
    bonitas AQ0FP0
    antifascista AQ0CS0
    """
    if not mfn or code[3:4] == 'C':
        mfn = code[3:4]
    if not sp:
        sp = code[4:5]
    ncode = (code[:3] + mfn + sp + code[-1:]).upper()
    texto = "select pal from dicc where origen = (select origen from dicc where \
pal = '%s' and codigo = '%s') and codigo = '%s';" % (adj, code, ncode)
    #print(t)
    try:
        cur.execute(texto)
    except:
        return (adj, code)
    try:
        return (cur._rows[0][0].decode(), ncode)
    except:
        return (adj, code)

def change_det(det, code, mfn = '', sp = ''):
    """Examples
    el DA0MS0
    la DA0FS0
    los DA0MP0
    """
    if not mfn or code[3:4] == 'N':
        mfn = code[3:4]
    if not sp:
        sp = code[4:5]
    ncode = (code[:3] + mfn + sp + code[-1:]).upper()
    texto = "select pal from dicc where origen = (select origen from dicc where \
pal = '%s' and codigo = '%s') and codigo = '%s';" % (det, code, ncode)
    #print(t)
    try:
        cur.execute(texto)
    except:
        return (det, code)
    try:
        return (cur._rows[0][0].decode(), ncode)
    except:
        return (det, code)

def change_pro(pro, code, mfn = '', sp = ''):
    """Examples
    vuestra PX2FS0P0
    vuestro PX2NS0P0 (lo vuestro, neutro)
    vuestro PX2MS0P0 (vuestro auto)
    vuestros PX2MP0P0
    """
    if not mfn:
        mfn = code[3:4]
    if not sp:
        sp = code[4:5]
    ncode = (code[:3] + mfn + sp + code[-1:]).upper()
    texto = "select pal from dicc where origen = (select origen from dicc where \
pal = '%s' and codigo = '%s') and codigo = '%s';" % (pro, code, ncode)
    #print(t)
    try:
        cur.execute(texto)
    except:
        return (pro, code)
    try:
        return (cur._rows[0][0].decode(), ncode)
    except:
        return (pro, code)

def change_verb(verb, code, mfn = '', sp='', m = '', t='' , p='3'):
    if code[2:3] == 'G' or code[2:3] == 'N':
        return (verb, code)
    elif code[2:3] == 'P':
        if not mfn:
            mfn = code[6:7]
        if not sp:
            sp = code[5:6]
        ncode = (code[:5] + sp + mfn).upper()
    else:
        if not m:
            m = code[2:3]
        if not t:
            t = code[3:4]
        if not p:
            p = str(code[4:5])
        if not sp:
            sp = code[5:6]
        #print(code[:2], c , t, str(p), sp, code[6:])
        ncode = (code[:2] + m + t + str(p) + sp + code[6:]).upper()
    #print(ncode)
    texto = "select pal from dicc where origen = (select origen from dicc where \
pal = '%s' and codigo = '%s') and codigo = '%s';" % (verb, code, ncode)
    #print(t)
    try:
        cur.execute(texto)
    except:
        return (verb, code)
    try:
        return (cur._rows[0][0].decode(), ncode)
    except:
        return (verb, code)

def select_codigo(pal, tipo):
    text = "select codigo from dicc where pal = '%s' and tipo = '%s'" % (pal, tipo)
    cur.execute(text)
    return cur._rows[0][0].decode()

def change_sentence(sent, mfn, sp, m, t, p):

    cods = 'ADNPV' # CODES for adj det, nouns and pron and verbs
    tot = len(npals)
    for a in range(tot):
        pal = npals[a][0]
        # if pal == 'el':
            # print("problemas")
        if npals[a][1][:2] != 'NP':
            if npals[a][1][:1] in cods:
                changed = change_pal(pal, npals[a][1], mfn, sp, m, t, p)
                npals[a][0] = changed[0]
                npals[a][1] = changed[1]


def change_pal(pal, codigo, mfn, sp, m, t, p): 
    tipo = codigo[:1]
    resp = pal
    # tipo = tipos[0] # a djetivo, v erb, n oun, det erminante, pro nombre
    if tipo == 'V':
        resp = change_verb(pal,codigo,'', sp, m, t, p)
    elif tipo == 'N':
        resp = change_noun(pal,codigo, mfn, sp)
    elif tipo == 'A':
        resp = change_adj(pal,codigo, mfn, sp)
    elif tipo == 'D':
        resp = change_det(pal,codigo, mfn, sp)
    elif tipo == 'P':
        resp = change_pro(pal,codigo, mfn, sp)
    return resp

def review_sent(resp):
    tot = len(npals)
    for i in range(tot):
        pal = npals[i][0]
        """
        if pal == 'entre':
            print("problemas")
        """
        codigo = resp[i][1]
        #check if mfn o sp in two words are in agreement
        if codigo.startswith('D') or codigo.startswith('A') or codigo.startswith('P'): #determinante o adjetivo o pronombre
            check_range(npals, i, 2) # within a range of two words before/after
        if codigo.startswith('V'): #verb. Check subjects
            check_verb(npals, i, 5)
    return npals
        
def check_verb(npals, i, rango):
    # VMII3S0
    pal = npals[i][0]
    code = npals[i][1]
    mfn = ''
    m = code[2:3]
    t = code[3:4]
    p = str(code[4:5])
    sp = code[5:6]
    #check subjects before verb and their number
    tot = 0
    if npals[i][1][:3] == 'VMP':
        mfn = npals[i][1][6:7]
        sp = npals[i][1][5:6]
        if npals[i-1][2].lower() == 'haber':
            mfn = 'M'
            sp = 'S'
    else:
        for a in range(1,rango+1):
            if i - a >= 0:
                if npals[i-a][3] == 'subj':
                    if npals[i-a][1][4:5] == 'S':
                        tot +=1
                    elif npals[i-a][1][4:5] == 'P':
                        tot +=2
        if tot == 1:
            sp = 'S'
        else:
            sp = 'P'
    changed = change_verb(pal, code, mfn, sp, m , t , p)
    npals[i][0] = changed[0]
    npals[i][1] = changed[1]

def check_range(npals, i, rango):   
    m = t = p = ''
    pal = npals[i][0]

    code = npals[i][1]
    if code.startswith('N'):
        g, n = code[2:3], code[3:4]
    else:
        g, n = code[3:4], code[4:5]
    for a in range(1, rango+1):
        if i+a <= len(npals):
            if npals[i+a][1].startswith('N'):
                codex = npals[i+a][1]
                gx, nx = codex[2:3], codex[3:4]
                if g != gx:
                    changed = change_pal(npals[i][0], code, gx, nx, m, t, p)
                    npals[i][0] = changed[0]
                    npals[i][1] = changed[1]
                    break        
    for a in range(1, rango+1):
        if i - a >= 0:
            if npals[i-a][1].startswith('N'):
                codex = npals[i-a][1]
                gx, nx = codex[2:3], codex[3:4]
                if g != gx:
                    changed = change_pal(npals[i][0], code, gx, nx, m, t, p)
                    npals[i][0] = changed[0]
                    npals[i][1] = changed[1]
                    break

                
def imprime(ba):

    # print(sent.sentencia)
    num = 0
    for pal in ba.sent.pals:
        """ 
        # con el corripio
        print(pal.pal, pal.lema, pal.etiqueta, pal.et_corta, pal.label, pal.label2, 
              pal.multipal, "\n\t sim: ", pal.similes, "\n\t contr: ", pal.contrarios, 
              "\n\t adic ", pal.adicionales, "\n\t relac: ", pal.relacionados)
        """
        # con wordnet
        print((pal.pal, pal.lema, pal.etiqueta, pal.chunk, pal.label, pal.label2))
        npals[num] = []
        npals[num].append(pal.pal)
        npals[num].append(pal.etiqueta)
        npals[num].append(pal.lema)
        npals[num].append(pal.label)
        npals[num].append(pal.label2)
        num +=1
        """
              '\n.....senses: ', pal.get_senses(), '\n.....relaciones: ', pal.busca_relaciones(), 
              '\n.....similes: ', pal.busca_similes(), 
              '\n.....nodo: ', pal.nodo,
              '\n.....head: ' , pal.head,
              '\n.....chunk: ', pal.chunk,
              '\n.....label: ', pal.label,
              '\n.....label2: ', pal.label2
                  )
        """

ba = ba('es', con)
t2 = tm.time()
print(("inicializando", t2-t1))
my_fr = """Rajoy respondía asegurando que hay muchas diferencias entre el proceso de Escocia y los acontecimientos que se están produciendo aquí, entre otras porque Escocia no tiene las competencias que el País Vasco o Cataluña tienen aquí y recalcaba que el argumento más importante es que estos procesos son un torpedo en la línea de flotación de la UE, que se ha creado para integrar estados."""
if not my_fr.endswith('.'):
    my_fr += '.'

# Following is using dicc only, no freeling
pals = word_tokenize(my_fr)
"""
npals = {}
for pal in pals:
    t = "select origen, codigo, tipo from dicc where pal = '%s';" % pal
    cur = con.cursor()
    cur.execute(t)
    data = cur.fetchone()
    if data:
        npals[pal] = []
        npals[pal].append(data[0])
        npals[pal].append(data[1])
        npals[pal].append(data[2])
    else:
        npals[pal] = []


print(my_fr, "\n")
print("*"*60)
"""
ba.analiza(my_fr)
npals = {}
imprime(ba)
#change some variables 
m = ''
p = 3
mfn = 'f'
sp = 'p'
t = 'F'
print(("1.-", npals))
if len(pals) == 2 and pals[1] == '.': #there is one words in this sentence
    pal = pals[0]
    resp = change_pal(pal, npals[pal][1], mfn, sp, m, t, p)
else: #there is only one word
    change_sentence(my_fr, mfn, sp, m, t, p)
    # print("2.-", npals)
    # print(resp)
    review_sent(npals)
    print(("4.-", npals))
    retorno = []
    for cada in range(len(npals)-1):
        retorno.append(npals[cada][0])
    # print(retorno)
    resp = " ".join(retorno)
print(('antes: ', my_fr, '\nahora: ', resp ))
t3 = tm.time()
print(("analizando", t3-t2))
