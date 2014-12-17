'''
Created on 22/10/2014

@author: aurelio
'''
from nltk.corpus import wordnet as wn
import mysql.connector as my
from pprint import pprint


con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'mywn','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)


class MySQLCursorDict(my.cursor.MySQLCursor):
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None
    
def selectRecords():
    cur = con.cursor(cursor_class=MySQLCursorDict)
    # t = "select word, sense, offset, pos from mcr30.wei_eng_30_variant;"
    t = "select distinct  w.offset, pos, eng as word from wn_words w left join lexname l \
on w.offset = l.offset where l.offset is null;"
    cur.execute(t)
    return cur.fetchall()

def saveRecord(word, offset, synset, lemma, sensekey):
    cur = con.cursor()
    t = "insert ignore into agiria.sensekey (word, offset, synset, lemma, sensekey) \
    values (%s, %s, %s, %s, %s);"
    values = (word, offset, synset, lemma, sensekey)
    try:
        cur.execute(t, values)
    except my.Error as err:
        print("ERROR: ", err, t, values )
        
def saveLexname(offset, lexname, region, topic, usage):
    cur = con.cursor()
    t = "insert ignore into lexname (offset, lexname, region, topic, uso) values (%s, %s, %s, %s, %s);"
    values = (offset, lexname, region, topic, usage)
    try:
        cur.execute(t, values)
    except my.Error as err:
        print("ERROR: ", err, t, values )
        
def lexnames():
    all = selectRecords()
    for cada in all:
        lemmas = []
        region = []
        topic = []
        usage = []
        syn = ''
        pos = ''
        # word = cada['word'].decode()
        word = cada['word']
        offset = cada['offset']
        # sense not included from wn_words
        # sense = str(cada['sense']).rjust(2, '0')
        # instead compute it from word and offset
        sense = '01'
        all_syn = wn.synsets(word)
        for a in all_syn:
            if a.offset == offset:
                sense = str(a.name()[-2:]).rjust(2, '0')
        # offset = cada['offset'].decode()
        
        # pos = cada['pos'].decode()
        pos = cada['pos']
        syns =  word + '.' + pos  + '.' + sense
        try:
            syn = wn.synset(syns)
            lexname = syn.lexname()
            region = syn.region_domains()
            if offset != str(syn.offset()).rjust(8, '0'):
                #they are different offsets with different senses
                #cancel this record
                lexname = ''
                print("error en ", syns, "offset en record:", offset, "en wn:", syn.offset())
            elif pos != syn.name()[-4:-3]:
                if pos == 'a' and syn.name()[-4:-3] == 's':
                    pass
                else:
                    print("error en ", syns, "pos en record:", pos, "en wn:", syn.name()[-4:-3])
                    lexname = '' #cancel this record
        except:
            print("syns no encontrado: ", syns)
            lexname = ''
        if lexname:
            if region:
                region = ", ".join ([str(x.offset()).rjust(8,'0') for x in region])
            else:
                region = ''
            if topic:
                topic = ", ".join ([str(x.offset()).rjust(8,'0') for x in topic])
            else:
                topic = ''
            if usage:
                usage = ", ".join ([str(x.offset()).rjust(8,'0') for x in usage])
            else:
                usage = ''                
            
            saveLexname(offset, lexname, region, topic, usage)
        
def main():
    all = selectRecords()
    for cada in all:
        lemmas = []
        word = cada['word'].decode()
        sense = str(cada['sense']).rjust(2, '0')
        offset = cada['offset'].decode()
        pos = cada['pos'].decode()
        syns =  word + '.' + pos  + '.' + sense
        try:
            syn = wn.synset(syns)
            lemmas = syn.lemmas()
        except:
            pass
        if lemmas:
            for lemma in lemmas:
                sensekey = lemma.key()
                # print(syn, lemma, sensekey, offset)
                saveRecord(word, offset, syn.name(), lemma.name(), sensekey)
                
if __name__ == '__main__':
    # main()
    lexnames()

                
            
            