'''
Created on 05/11/2012

@author: aurelio
'''
import freeling

class MyFreeling:
  '''
  Ejemplo de uso:

  l = self.tk.tokenize(lin);
  ls = self.sp.split(l,0);

  ls = self.mf.analyze(ls);
  ls = self.tg.analyze(ls);
  ls = self.sen.analyze(ls);
  ls = self.parser.analyze(ls);
  ls = self.dep.analyze(ls);

  ## output results
  for s in ls :
    ws = s.get_words();
    for w in ws :
      print(w.get_form()+" "+w.get_lemma()+" "+w.get_tag()+" "+w.get_senses_string());
    print ("");

    tr = s.get_parse_tree();
    self.printTree(tr.begin(), 0);

    dp = s.get_dep_tree();
    self.printDepTree(dp.begin(), 0)
  '''

  def inicia(self):
    FREELINGDIR = "/usr/local";

    DATA = FREELINGDIR+"/share/freeling/";
    LANG="es";

    freeling.util_init_locale("default");   
    # create options set for maco analyzer. Default values are Ok, except for data files.
    op= freeling.maco_options("es");
    op.set_active_modules(0,1,1,1,1,1,1,1,1,1,0);
    op.set_data_files("",DATA+LANG+"/locucions.dat", DATA+LANG+"/quantities.dat", 
                      DATA+LANG+"/afixos.dat", DATA+LANG+"/probabilitats.dat", 
                      DATA+LANG+"/dicc.src", DATA+LANG+"/np.dat",  
                      DATA+"common/punct.dat",DATA+LANG+"/corrector/corrector.dat");
    
    # create analyzers
    self.tk=freeling.tokenizer(DATA+LANG+"/tokenizer.dat");
    self.sp=freeling.splitter(DATA+LANG+"/splitter.dat");
    self.mf=freeling.maco(op);
    
    self.tg=freeling.hmm_tagger("es",DATA+LANG+"/tagger.dat",1,2);
    self.sen=freeling.senses(DATA+LANG+"/senses.dat");
    ner=freeling.ner(DATA+LANG+"/ner/ner-ab.dat");
    
    self.parser= freeling.chart_parser(DATA+LANG+"/chunker/grammar-chunk.dat");
    self.dep=freeling.dep_txala(DATA+LANG+"/dep/dependences.dat", self.parser.get_start_symbol());   
    
## ------------  output a parse tree ------------
  def printTree(self, node, depth):
    print(''.rjust(depth*2),end='');
    info = node.get_info();
    if (info.is_head()): print('+',end='');

    nch = node.num_children();
    if (nch == 0) :
        w = info.get_word();
        print ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()),end='');

    else :
        print('{0}_['.format(info.get_label()));

        for i in range(nch) :
          child = node.nth_child_ref(i);
          self.printTree(child, depth+1);

        print(''.rjust(depth*2),end='');
        print(']',end='');
        
    print('');

  ## ------------  output a parse tree ------------
  def printDepTree(self, node, depth):

    print(''.rjust(depth*2),end='');

    info = node.get_info();
    link = info.get_link();
    linfo = link.get_info();
    print ('{0}/{1}/'.format(link.get_info().get_label(), info.get_label()),end='');

    w = node.get_info().get_word();
    print ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()),end='');

    nch = node.num_children();
    if (nch > 0) :
        print(' [');

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

        print(''.rjust(depth*2),end='');
        print(']',end='');

    print('');

  def __init__(self):
    '''
    Constructor
    '''
    self.inicia(self)
        
