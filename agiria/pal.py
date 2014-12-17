'''
Created on 04/10/2013

@author: aurelio
'''

# import re
# import nltk
import freeling

class Pal():
    '''
    classdocs
    '''
    
    def get_word(self):
        return self.w.get_form()

    def get_label(self):
        return self.info.get_label()
    
    def get_label2(self):
        return self.linfo.get_label()
    
    def is_head(self):
        return self.info.is_head()

    def is_chunk(self):
        return self.info.is_chunk()
 
    def get_chunk_ord(self):
        return self.info.get_chunk_ord()
           
    def node_id(self):
        return self.info.get_node_id()
            
    def get_tag(self):
        return self.w.get_tag()
        
    def get_short_tag(self):
        pass
        #return self.w.get_short_tag()
        
    def is_multiword(self):
        return self.w.is_multiword()
    
    def split_node(self):
        # nodo = self.node_id()
        if self.nodo:
            self.node1, self.node2 = self.nodo.split('.')
        
    def get_senses(self):
        sentidos = []
        sen = self.w.get_senses_string().split("/")
        for cada in sen:
            num = cada[:8]
            t = "Select word from wn_variant where offset = '%s';" % num
            cur = self.con.cursor()
            cur.execute(t)
            for fila in cur.fetchall():
                sentidos.append(fila[0].decode("utf-8"))
        sentidos = set(sentidos)
        return sentidos

    def busca_relaciones(self):
        relaciones = []
        sen = self.w.get_senses_string().split("/")
        for cada in sen:
            num = cada[:8]
            t = "select word from wn_variant v inner join wn_relation r on v.offset = r.targetSynset \
            where r.sourceSynset = '%s';" % num
            cur = self.con.cursor()
            cur.execute(t)
            for fila in cur.fetchall():
                relaciones.append(fila[0].decode("utf-8"))
        relaciones = set(relaciones)
        return relaciones
        
    def get_lema(self):
        return self.w.get_lemma()
    
    def get_morpho(self):
        pass
    
    def set_info(self, info, depth):
        self.info = info
        self.depth = depth
        if info.is_head():
            self.head = self.info.is_head()
        if info.get_node_id():
            self.nodo = self.info.get_node_id()
        self.label = self.info.get_label()
        """
        if info.is_chunk():
            self.chunk = self.info.is_chunk()
        if info.get_chunk_ord():
            self.chunk_ord = self.info.get_chunk_ord()  
        """
              
    def set_linfo(self, linfo):
        self.linfo = linfo
        self.label2 = self.linfo.get_label()
        
    def busca_similes(self):
        t = "select sinonimos from corr where pal = '%s';" % self.lema
        cur = self.con.cursor()
        cur.execute(t)
        filas = cur.fetchall()
        ar = []
        for fila in filas:
            if fila[0]:
                sims = fila[0].split(",")
                for sim in sims:
                    ar.append(sim)
        return ar
    
    def busca_hiperonimos (self):
        pass
    
    def busca_hiponimos (self):
        pass
    
    def busca_holonimos (self):
        pass 
    
    def busca_meronimos (self):
        pass
    
    def busca_troponimos (self):
        pass
    
    def busca_vinculacion (self):
        pass
 
    def busca_contrarios(self):
        t = "select contrario from corripio where pal = '%s' and contrario <> '';" % self.lema
        cur = self.con.cursor()
        cur.execute(t)
        filas = cur.fetchone()
        ar = []
        if cur.rowcount:
            sims = filas[0].split(",")
            for sim in sims:
                ar.append(sim)
        return ar 
    
    def busca_adicionales(self):
        t = "select tipo, valores from corripio where pal = '%s' and tipo <> '';" % self.lema
        cur = self.con.cursor()
        cur.execute(t)
        ar = {}
        for tipo, valores in cur.fetchall():
            ar[tipo] = []
            adics = valores.split(",")
            for cada in adics:
                ar[tipo].append(cada)
        return ar 

    def busca_relacionados(self):
        t = "select adicional from corripio where pal = '%s' and adicional <> '';" % self.lema
        cur = self.con.cursor()
        cur.execute(t)
        ar = []
        for adic in cur.fetchall():
            adics = adic[0].split()
            pal = adics[0]
            if len(adics) == 2:
                num = adics[1]
            else:
                num = None
            if pal and num:
                t1 = "select similes from corripio where pal = '%s' and num_sign = '%s';" % (pal, num)
            elif pal and not num:
                t1 = "select similes from corripio where pal = '%s';" % (pal)
            cur = self.con.cursor()
            try:
                cur.execute(t1)
            except:
                print(("Error en busca_relacionados", cur.statement))
            for fila in cur.fetchall():
                if fila[0]:
                    sims = fila[0].split(",")
                    for sim in sims:
                        ar.append(sim)
        return ar
 
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.i<len(self.lst)-1:
            self.i += 1         
            return self.lst[self.i]
        else:
            raise StopIteration
        
    def save_pal(self):
        '''
        if self.senses:
            sens = ','.join(self.senses)
        else:
            sens = ''
        if self.relations:
            rel = ','.join(self.relations)
        else:
            rel = ''
        if self.similars:
            sim = ','.join(self.similars)
        else:
            sim = ''
        '''
        # print("saving pal: ", self.pal, " de ", self.doc_id, self.sent_id, self.num)
        '''
        t = "insert into pals (document, sentence, pal_id, token, lemma, tag, node1, node2, depth, head, chunk, label, label2, senses, relations, similars) \
        values (%i, %i, %i, '%s','%s','%s',%i, %i, %i, '%s','%s','%s','%s','%s','%s','%s')" % \
        (self.doc_id, self.sent_id, self.num, self.pal, self.lema, self.etiqueta, int(self.node1), int(self.node2), self.depth, self.head, self.chunk, self.label,
         self.label2, sens, rel, sim)
        if self.pal == "'":
            self.pal = "\'"
        '''
        if len(self.pal) <= 60: #assumed error if len(pal) > 50
            """
            if not self.is_chunk():
                self.chunk = 0
                self.chunk_ord = 0
            else:
                self.chunk = self.is_chunk()
            if not isinstance(self.chunk, int):
                self.chunk = 0
                self.chunk_ord = 0
            if not isinstance(self.head, int):
                self.head = 0
            """
            # print (self.pal, self.chunk, self.chunk_ord, self.label, self.label2)
            t = ''
            try:
                t = "insert ignore into pals (document, sentence, pal_id, token, lemma, tag, node1, node2, depth, head, \
                chunk, chunk_ord, label, label2) \
                values (%i, %i, %i, '%s','%s','%s',%i, %i, %i, '%i',\
                '%s', '%i', '%s','%s')" % \
                (self.doc_id, self.sent_id, self.num, self.pal, self.lema, self.etiqueta, int(self.node1), int(self.node2), int(self.depth), int(self.head), 
                 self.chunk, int(self.chunk_ord), self.label, self.label2)
            except:
                print(("error:- " , self.pal, self.chunk_ord, self.chunk_ord, self.label, self.label2))
            cur = self.con.cursor()
            try:
                cur.execute(t)
            except:
                print(("Error saving pal. ",  cur.statement))

    def __init__(self, w, con):
        '''
        Constructor
        '''
        '''
        con_data={'user':'root','password':'agm','host':'127.0.0.1', \
        'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
        self.con = my.connect(**con_data)
        '''
        self.con = con
        self.w = w
        self.doc_id = 0
        self.sent_id = 0
        self.pal = self.w.get_form()
        self.lema = self.w.get_lemma()

        # self.similars = self.busca_similes()
        # self.contrarios = self.busca_contrarios(self.lema)
        # self.adicionales = self.busca_adicionales(self.lema)
        # self.relations = self.busca_relacionados()

        self.etiqueta = self.get_tag()
        self.et_corta = self.get_short_tag()

        # self.senses = self.get_senses()
        '''
        self.relaciones = self.busca_relaciones()
        self.relaciones = self.busca_relaciones()
        self.multipal = self.is_multiword()
        '''
        self.morfo = self.get_morpho()
        self.nodo  = ''
        self.label = ""
        self.label2 = ""
        self.node1 = 0
        self.node2 = 0
        self.chunk = ''
        self.head = 0
        self.chunk_ord = 0
        self.num = 0
        