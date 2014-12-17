'''
Created on 04/10/2013

@author: aurelio
'''
    
import freeling
# import sys
# from nltk import sent_tokenize
import mysql.connector as my
"""
from document import Document
"""
from sentence import Sentence

class BasicAgiria():
    '''
    classdocs
    '''

    
    def inicializa(self):

        FREELINGDIR = "/usr/local";
        
        DATA = FREELINGDIR+"/share/freeling/";
        LANG=self.lang;
        
        freeling.util_init_locale("default");
        
        # create language analyzer
        self.la=freeling.lang_ident(DATA+"common/lang_ident/ident.dat");
        
        # opciones para maco analyzer. 
        op= freeling.maco_options("es");
        op.set_active_modules(0,1,1,1,1,1,1,1,1,1)
        op.set_data_files("",DATA+LANG+"/locucions.dat", DATA+LANG+"/quantities.dat", 
                          DATA+LANG+"/afixos.dat", DATA+LANG+"/probabilitats.dat", 
                          DATA+LANG+"/dicc.src", DATA+LANG+"/np.dat",  
                          DATA+"common/punct.dat",DATA+LANG+"/corrector/corrector.dat");
        
        # crear analyzers
        self.tk=freeling.tokenizer(DATA+LANG+"/tokenizer.dat");
        self.sp=freeling.splitter(DATA+LANG+"/splitter.dat");
        self.mf=freeling.maco(op);
        
        self.tg=freeling.hmm_tagger(DATA+LANG+"/tagger.dat",1,2);
        self.sen=freeling.senses(DATA+LANG+"/senses.dat");
        self.nec=freeling.nec(DATA+LANG+"/nerc/nec/nec-ab-rich.dat");
        # self.ner=freeling.nec(DATA+LANG+"/ner/ner-ab.dat");
        
        self.parser= freeling.chart_parser(DATA+LANG+"/chunker/grammar-chunk.dat");
        self.dep=freeling.dep_txala(DATA+LANG+"/dep/dependences.dat", self.parser.get_start_symbol());

        con_data={'user':'root','password':'agm','host':'127.0.0.1', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}

        self.con = my.connect(**con_data)


    ## ------------  salida del parse tree ------------
    def printTree(self,node, depth):
    
        if self.printing: print(''.rjust(depth*2),end='');
        info = node.get_info();
        if (info.is_head()): print('+',end='');
    
        nch = node.num_children();
        if (nch == 0) :
            w = info.get_word();
            if self.printing: print ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()),end='');
    
        else :
            if self.printing: print('{0}_['.format(info.get_label()));
    
            for i in range(nch) :
                child = node.nth_child_ref(i);
                self.printTree(child, depth+1);
    
            if self.printing: print(''.rjust(depth*2),end='');
            if self.printing: print(']',end='');
            
        if self.printing: print('');

    def computeTree(self,node, depth):
    
        if self.printing: print(''.rjust(depth*2),end='');
        info = node.get_info();
        # if (info.is_head()): print('+',end='');
    
        nch = node.num_children();
        if (nch == 0) :
            w = info.get_word();
            if self.printing: print ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()),end='');
    
        else :
            if self.printing: print('{0}_['.format(info.get_label()));
    
            for i in range(nch) :
                child = node.nth_child_ref(i);
                self.computeTree(child, depth+1);
    
            if self.printing: print(''.rjust(depth*2),end='');
            if self.printing: print(']',end='');
            
        if self.printing: print('');
    
    ## ------------  salida del parse tree ------------
    def printDepTree(self, node, depth):
    
        if self.printing: print(''.rjust(depth*2),end='');
    
        info = node.get_info();
        link = info.get_link();
        linfo = link.get_info();
        # print("sacamos", linfo.get_label(), link.get_info().get_label(), info.get_label())
        if self.printing: print ('{0}/{1}/'.format(link.get_info().get_label(), info.get_label()),end='');
    
        w = node.get_info().get_word();
        if self.printing: print ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()),end='');
        for num in range(len(self.sentencias[len(self.sentencias)-1].pals)):
            if w.get_form() == self.sentencias[len(self.sentencias)-1].pals[num].pal:
                self.sentencias[len(self.sentencias)-1].pals[num].set_info(info)
                self.sentencias[len(self.sentencias)-1].pals[num].set_linfo(linfo)
                break
        nch = node.num_children();
        if (nch > 0) :
            if self.printing: print(' [');
    
            for i in range(nch) :
                d = node.nth_child_ref(i);
                if (not d.get_info().is_chunk()) :
                    self.printDepTree(d, depth+1);
            ch = {};
            for i in range(nch) :
                d = node.nth_child_ref(i);
                if (d.get_info().is_chunk()) :
                    ch[d.get_info().get_chunk_ord()] = d;
     
            for i in sorted(ch.keys()) :
                self.printDepTree(ch[i], depth + 1);
    
            if self.printing: print(''.rjust(depth*2),end='');
            if self.printing: print(']',end='');
    
        print('');
        
    
     ## ------------  salida del parse tree ------------
    def computeDepTree(self, node, depth):

    
        info = node.get_info();
        link = info.get_link();
        linfo = link.get_info();
        w = node.get_info().get_word();
        p = w.get_form()
        # print(p, depth)
        pals = [pal.pal for pal in self.sent.pals]
        #for num in range(len(self.doc.sent.pals)):
        if pals.count(p) == 1:
            self.sent.pals[pals.index(p)].set_info(info, depth)
            self.sent.pals[pals.index(p)].set_linfo(linfo)
        else:
            #to be improved. run as many times as number of p in pals
            nlist = [i for i, j in enumerate(pals) if j == p]
            for i in nlist:
                self.sent.pals[i].set_info(info, depth)
                self.sent.pals[i].set_linfo(linfo)                    
            '''
            if w.get_form() == self.doc.sent.pals[num].pal:
                self.doc.sent.pals[num].set_info(info)
                self.doc.sent.pals[num].set_linfo(linfo)
                break
            '''
        nch = node.num_children();
        if (nch > 0) :    
            for i in range(nch) :
                d = node.nth_child_ref(i);
                if (not d.get_info().is_chunk()) :
                    self.computeDepTree(d, depth+1);
            ch = {};
            for i in range(nch) :
                d = node.nth_child_ref(i);
                if (d.get_info().is_chunk()) :
                    ch[d.get_info().get_chunk_ord()] = d;
     
            for i in sorted(ch.keys()) :
                self.computeDepTree(ch[i], depth + 1);        
      

        
    def analiza(self, sent):
        sentencia = sent 
        # if self.printing: print(sentencia)
        # sent = Sentencia(sentencia)
        # self.sentencias.append(Sentencia(sentencia))
        # self.sentencias[self.n] = Sentencia
        # self.sentencias[self.n].pals = {}
        l = self.tk.tokenize(sentencia);
        ls = self.sp.split(l,0);
    
        ls = self.mf.analyze(ls);
        ls = self.tg.analyze(ls);
        ls = self.nec.analyze(ls)
        
        ls = self.sen.analyze(ls);
        ls = self.parser.analyze(ls);
        ls = self.dep.analyze(ls);
        
        self.sent = Sentence()
        self.sent.set_sentence(sent)
        self.sent.set_con(self.con)
        
        ## output results
        for s in ls :
            # sent.pals = []
            self.sent.sentence = s
            ws = s.get_words();
            num = 0
            for w in ws :
                self.sent.add_pal(w, num)
                # self.sentencias[len(self.sentencias)-1].pals.append(Pal(w, self.con))
                num += 1
            '''
                print(w.get_form()+" "+w.get_lemma()+" "+w.get_tag()+" "+w.get_senses_string());
            print ("");
            '''
            # self.tr = s.get_parse_tree();
            # self.printTree(self.tr.begin(), 0);
            # self.computeTree(self.tr.begin(), 0);
            
            self.dp = s.get_dep_tree();
            self.computeDepTree(self.dp.begin(), 0)        
            

    def save_pals(self):
        for pal in self.doc.sent.pals:
            pal.doc_id = self.doc.doc_id
            pal.sent_id  = self.doc.sent.sent_id
            pal.split_node()
            pal.save_pal()

    def __init__(self, lang = 'es',  printing=True):
        '''
        Constructor
        '''
        self.printing = printing
        if lang in ['en', 'es', 'fr']:
            self.lang = lang
        else:
            print("Language not identified, using Spanish")
            self.lang = 'es'
        self.inicializa()
        # self.n = 0

        