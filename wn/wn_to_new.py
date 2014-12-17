import mysql.connector as my

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}

def select_from_gloss(pal, gloss):
        try:
            t = "select w.lemma, x.synsetid, x.sensenum, x.pos, x.definition from wn.words w inner join wn.sensesXsynsets x \
            on w.wordid = x.wordid where  w.lemma = '{0}' \
            and x.definition = '{1}';".format(pal.lower(), gloss.replace("\\'", "'").replace("'", "\\'"))
            cur.execute(t)
        except my.Error as err:
            print(("error en sql ", err, t, pal, gloss))
            return ''
        except:
            print(("error en ", pal, gloss))
            return ''
        return cur.fetchall()
    
def select_from_gloss_def(pal, pos):
    try:
        t = "select x.definition from wn.words w inner join wn.sensesXsynsets x \
        on w.wordid = x.wordid where  w.lemma = '{0}' \
        and x.pos = '{1}';".format(pal.lower(), pos)
        cur.execute(t)
    except my.Error as err:
        print(("error en sql ", err, t, pal, gloss))
        return ''
    return cur.fetchall()
    
def select_from_old():
    t = "select v.word, v.sense, v.offset, v.pos, s.gloss \
        from mcr30.wei_eng_30_variant v inner join mcr30.wei_eng_30_synset s \
        on v.offset = s.offset and v.pos = s.pos;"
    
    """
    next sql statement is of those not paired and to which we will apply similarity process of glosses to select highest similar
    t = "select v.word, v.sense, v.offset, v.pos, s.gloss \
        from mcr30.wei_eng_30_variant v inner join mcr30.wei_eng_30_synset s \
        on v.offset = s.offset and v.pos = s.pos \
        left join mcr30.relacion r on v.offset = r.old_offset and v.pos = r.old_pos and v.sense = r.old_sense \
        where r.new_word is null;"
    """
    cur.execute(t)
    todos = cur.fetchall()
    return todos

def old_to_new(old_pal, new_pal, old_pos, old_offset, old_sense, new_pos, new_offset, new_sense):
    t = "insert ignore into mcr30.relacion (word, new_word, old_pos, old_offset, old_sense, new_pos, new_offset, new_sense) \
    values ('%s', '%s', '%s', '%s', %s, '%s', '%s', %s);" % (old_pal, new_pal, old_pos, old_offset, old_sense, 
                                                       new_pos, new_offset, new_sense)
    cur2 = con.cursor()
    try:
        cur2.execute(t)
    except my.Error as err:
        print(("error insertando ", err, t))

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
    ndord = dord
    if len(dord) > 1:
        dord = sorted(dord, key=dord.get, reverse=True)
        if ndord[dord[1]][0] > 0.1: #only returns highest indexed (besides the original sentence in index
            return ndord[dord[1]]
        else:
            return 0
    else:
        return 0


con = my.connect(**con_data)
cur = con.cursor()

todos = select_from_old()

for uno in todos:
    pal = uno[0].decode().replace('_', ' ').replace("'", "\\'")
    sense = uno[1]
    off = uno[2].decode()
    pos = uno[3].decode()
    gloss = uno[4].decode()
    gloss = gloss.replace("'", "\\'")
    gloss = gloss.strip()
    # print(pal, sense, off, pos, gloss, "\n", "*"*80)
    corresp = select_from_gloss(pal, gloss)
    if not corresp:
        sim = select_from_gloss_def(pal, pos)
        simils = []
        simils.append(gloss)
        for uno in sim:
            if uno:
                simils.append(uno[0])
        if len(simils) > 1: #search similarity only if sql statement gave records
            ret = similarity(simils)
            if ret:
                corresp = select_from_gloss(pal, ret[1])
                if not corresp:
                    print(("nada para ", pal, gloss, ret[1]))
                    continue
        else:
            print(("nada para ", pal, gloss))
            continue
    for cada in corresp:
        # print("la palabra ", cada[0], " con synset y sense antiguo:", off, sense, " tiene ahora el synset y sense:", cada[1], cada[2])
        new_pal = cada[0].replace("'", "\\'")
        # save old and new values in table relacion db mcr30
        old_to_new(pal.lower(), new_pal, pos, off, sense, cada[3], cada[1], cada[2])