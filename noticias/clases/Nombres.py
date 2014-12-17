from datetime import datetime
import random
import mysql.connector as my
import sys
sys.path.append('/home/aurelio/myfreeling/APIs/python')
import freeling
from config import con_data
from Necs import *

'''
Created on 05/04/2013

@author: aurelio

genera los nombres (NERs Name Entity Recognition) de todas las noticias
y los guarda en tabla not_nombres computando las veces que aparece
Además, unifica ners similares en la misma noticia (p.e. en una noticia se 
habla de Mariano Rajoy, otras veces de Rajoy y alguna otra de Mariano, siendo 
la misma persona)


'''

class Nombres:
    '''
    classdocs
    '''
    
    def __init__(self):
        print ("Inicializando Nombres")
        print(str(datetime.time(datetime.now())))
        FREELINGDIR = "/usr/local";
        DATA = FREELINGDIR+"/share/freeling/";
        LANG="es";
        freeling.util_init_locale("default");
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
        
        # self.sen=freeling.senses(DATA+LANG+"/senses.dat");
        # self.ner=freeling.ner(DATA+LANG+"/ner/ner-ab.dat");
        self.nec=freeling.nec(DATA+LANG+"/nec/nec-ab.dat");
        
        # self.parser= freeling.chart_parser(DATA+LANG+"/chunker/grammar-chunk.dat");
        
        self.pondera ={'titulo':3,'intro':2, 'texto':1} #ponderacion dada a cada ner según tipo origen.
        self.indice = 0 #indice que representa la proporción de ners comunes sobre todos de una noticia
        self.con = my.connect(**con_data)
        self.ultimo = 0
        self.minimo_comun = 0.45 # porcentaje que tienen que compartir dos noticias para ser relacionadas
        self.minimo_palabras = 14 #mínimo numero de palabras (pnderadas) para poder entrar en relación
        # pasamos a list (no_incluir) las palabras que no deben ser consideradas NERs
        self.cur1 = self.con.cursor()
        texto = "Select nombre from no_nombres order by nombre";
        try:
            self.cur1.execute(texto)
        except my.Error as err:
            print("Error seleccionando nombres de tabla no_nombres", format(err))
        self.no_incluir = [] # lista de palabras a omitir en ners identificados
        for nombre in self.cur1:
            try:
                nombre = str(nombre[0]).upper()
                nombre = nombre[2:-1] # quitar simbolo de byte b'
                
                nombre = nombre.replace('\\XC3\\XA1', 'Á')
                nombre = nombre.replace('\\XC3\\X81', 'Á')
                nombre = nombre.replace('\\XC3\\XA9', 'É')
                nombre = nombre.replace('\\XC3\\XAD', 'Í')
                nombre = nombre.replace('\\XC3\\X8D', 'Í')
                nombre = nombre.replace('\\XC3\\XB3', 'Ó')
                nombre = nombre.replace('\\XC3\\X93', 'Ó')
                nombre = nombre.replace('\\XC3\\XBA', 'Ú')
                nombre = nombre.replace('\\XC3\\XBC', 'Ü')
                nombre = nombre.replace('\\XC3\\XB1', 'Ñ')
                nombre = nombre.replace('\\XC3\\X91', 'Ñ')
                nombre = nombre.replace('\\XC2\\XBA', 'º')
                nombre = nombre.replace('\\XC4\\X82\\XC4\\X84', 'ĂĄ')
                
                self.no_incluir.append(nombre)
            except:
                print("Error incluyendo no_nombres en lista")
        self.no_incluir= sorted(set(self.no_incluir))
        # corefs de tabla
        self.cur1 = self.con.cursor()
        texto = "Select original, coref from coref order by original";
        try:
            self.cur1.execute(texto)
        except my.Error as err:
            print("Error seleccionando corefs", format(err))
        self.corefs = {} # dict de palabras corefs para cambiar en ners   
        for original,coref in self.cur1:  
            self.corefs[original] = coref
            
        print("Inicialización terminada", str(datetime.time(datetime.now())))
        
        
    def analiza(self):      
        # Llamada desde programa feeds.py
        #seleccionamos la última noticia (id mayor) para incluir solo las nuevas
        t1 = "select max(noticia) from not_nombres_relaciones;"
        self.cur = self.con.cursor()
        try:
            self.cur.execute(t1)
        except my.Error as err:
            print("Error seleccionando última noticia en Nombres", format(err))
        fila = self.cur.fetchone()
        try:
            self.ultimo = fila[0]
            print("Ultima noticia ", self.ultimo)
        except:
            print("Ultima noticia no recogida en clase Nombres")
        if not self.ultimo:
            self.ultimo = 0
        texto = "select id as num, titulo, intro, texto from noticias \
        where id > '"+str(self.ultimo)+"' ;"
        try:
            self.cur = self.con.cursor()
            self.cur.execute(texto)
        except:# my.Error as err:
            print("Error seleccionando noticias para nombres ", texto)
        try:
            self.filas = self.cur.rowcount  
            self.fila = 0
        except:
            print("Error hallando numero de filas en analiza")   
        # identificamos los NERs para cada noticia, separando de titulo, intro y texto
        # Se guardan en tabla not_nombres, los links a nums de noticia donde cada ner aparece
        for num, titulo, intro, texto in self.cur.fetchall(): 
            try:     
                self.fila +=1
                # print(num, titulo)
                self.unificado = {'ner':[], 'nec':[], 'tipo':[]} # dict con ners y necs para una noticia
                # Se manda a identifica_ner() por tipo de texto para buscar los ners
                self.identifica_ner(num, titulo, 'titulo')
                self.identifica_ner(num, intro, 'intro')
                self.identifica_ner(num, texto, 'texto')

            except:
                print("Error en loop mandando a identifca_ner y a unifica_ner de analiza \
                en fila", self.fila, self.unificado['ner'])
            
        self.cur.close()
        

        '''
        # Se prepara un dict con todos los ners de todas las noticias  
        '''
        self.fila = 0
        self.relaciona_noticias()
        
        
        
        
    def identifica_ner(self, num, texto, tipo):
        
        '''
        Proviene de analiza() para cada tipo (titulo, intro, texto)
        Usando freeling, identifica ners y necs del texto
        Los valores los pasa a listas self.unificado['ners'] , ['necs'] y ['tipos']
        Los pasa a funcion self.unifica_ner(num)
        '''
        # para iniciar freeling
        # print("noticia que llega a freeling en identifica_ner", num)
        try:
            l = self.tk.tokenize(texto);
            ls = self.sp.split(l,0);
            ls = self.mf.analyze(ls);
            ls = self.tg.analyze(ls);
            # ls = self.parser.analyze(ls);
            # ls = self.dep.analyze(ls);
            # ls = self.ner.analyze(ls)
            ls = self.nec.analyze(ls)
            # self.ners = [] # inicializa lista de ners para esa noticia y tipo
        except:
            print("Error calculando freeling para texto:", texto)
        pal = ''
        try:
            for s in ls :
                ws = s.get_words();
                for w in ws: 
                    try:
                        propio = w.get_tag()
                        if propio.startswith('NP'): # identifica los NERs como NP00000
                            pal = w.get_form()
                            pal.strip()
                            if pal.upper() not in self.no_incluir:
                                #Cambia coreferencias
                                if pal in self.corefs.keys():
                                    pal = self.corefs[pal]
                                # añade a dict
                                self.unificado['ner'].append(pal.replace("'", "\\'"))
                                self.unificado['nec'].append(propio)
                                self.unificado['tipo'].append(tipo)
                    except:
                        print("Error en loop w in ws de identifica_ner()", pal, propio, tipo) 
                            
        except:
            print("Error en loop s in ls de identifica_ner()")
        if tipo == 'texto':
            try:
                # pass # hasta arreglarlo
                self.unifica_ner(num)
            except:
                print("Algún error en funcion self.unifica_ner(num) enviado desde identifica_ner()")
                
        # print("Ners sacados en freeling", self.unificado['ner'])
                       
    def relaciona_noticias(self):
        # proviene de analiza()
        # prepara un dict con datos de not_nombres_relaciones por noticias
        print(str(datetime.time(datetime.now())), "hemos comenzado en relaciones nombres:")
        self.relaciones = {}
        self.conex = 0
        t = "Select noticia, tipo, ner as nombre from not_nombres_relaciones \
        group by noticia, tipo, ner"
        cur1 = self.con.cursor()
        cur1.execute(t)
        print(str(datetime.time(datetime.now())), "hemos seleccionado:")
        tipo_viejo = ''
        noticia_vieja=0
        for noticia, tipo, nombre in cur1: 
            if not self.relaciones.get(noticia):
                self.relaciones[noticia] = {'titulo':[], 'intro':[], 'texto':[], 'hash':''}
            try:
                self.relaciones[noticia][tipo].append(nombre)
            except:
                print("Error: tipos viejos y nuevos", tipo_viejo, tipo, \
                    "  Noticia vieja y actual:", noticia_vieja, noticia, "en", noticia, tipo, nombre)
            tipo_viejo = tipo
            noticia_vieja = noticia  
        print(str(datetime.time(datetime.now())), "hemos hecho el dict:" )
            
            
    def busca_relacion(self):
        try:
            # función llamada desde programa feeds que crea clase Nombres
            # Relaciona noticias con otras similares basado en el número de ners
            # comunes a ambas noticias. A partir de un mínimo (self.minimo_comun
            # apartir del dict con ners creado en relaciona_noticias()
            # print("Estamos en busca_relacion")
            t = "Select id as noticia from not_relacion where hash = '';"
            cur2 = self.con.cursor()
            try:
                cur2.execute(t)
                self.filas = cur2.rowcount
            except my.Error as err:
                print("Error en busca_relacion seleccionando de not_relacion", format(err))
            #print(cur2.statement)
            for row in cur2:
                self.fila +=1
                # print("Relacionando:"+str(self.fila)+" de "+str(self.filas))
                noticia = row[0]
                original = []
                try:                        
                    original = self.relaciones[noticia]
                except:
                    # print("No hay relaciones para", noticia)
                    continue
                palabras = len(original['titulo']) * self.pondera['titulo']\
                           +len(original['intro']) * self.pondera['intro']\
                           +len(original['texto']) * self.pondera['texto']
                if not palabras or palabras == 0:
                    print("Error en palabras", palabras)
                elif palabras < self.minimo_palabras:
                    # no llega al minimo de palabras para poder comparar (una vez ponderadas)
                    continue
                for noti, val in self.relaciones.items():
                    try:
                        en_relacion = len(list(set(original['titulo']) & set(val['titulo']))) * self.pondera['titulo']
                        en_relacion += len(list(set(original['intro']) & set(val['intro']))) * self.pondera['intro']
                        en_relacion += len(list(set(original['texto']) & set(val['texto']))) * self.pondera['texto']
                    except:
                        print("Error calculando en_relacion en busca_relacion")
                    # el indice muestra la proporcion de palabras comunes que la noticia de la tabla
                    # (noticia) tiene con la que se compara en self.relaciones (noti)
                    self.indice = en_relacion / palabras
                    # noticia es el id de la tabla not_relacion sin hash
                    # original es el array relaciones de esa noticia (id)
                    # noti es el id del dict relaciones que se prepara en relaciona_noticias, o sea,
                    # todas que están en tabla not_nombres_relaciones
                    # val es el list con resto del dict relaciones que se prepara en relaciona_noticias 
                    if  self.indice > self.minimo_comun:
                        if noticia != noti:
                            try:
                                if val['hash'] and not original['hash']:
                                    # print("Estamos en 1")
                                    original['hash'] = val['hash']
                                    self.guarda(noticia, val['hash'])
                                elif original['hash'] and not val['hash']:
                                    # print("Estamos en 2")
                                    val['hash'] = original['hash']
                                    self.guarda(noti, original['hash'])
                                elif not val['hash'] and not original['hash']:
                                    # print("Estamos en 3")
                                    original['hash'] = int(random.random()*100000000)
                                    val['hash'] = original['hash']
                                    self.guarda(noticia, original['hash'])
                                    self.guarda(noti, original['hash'])
                                elif val['hash'] and original['hash'] and val['hash'] != original['hash']:
                                    self.guarda(noticia, val['hash'])
                                    self.guarda_resto(noticia, original['hash'], val['hash'])
                                '''
                                else:
                                    # Crea un nuevo hash para esta noticia, aunque sea la única con tal hash
                                    original['hash'] = int(random.random()*100000000)
                                    self.guarda(noticia, original['hash'])
                                '''
                                    
                            except:
                                print("Error tratando hashes en busca_relacion de Nombres", noticia, noti)
                    '''            
                    else:
                        
                        # Crea un nuevo hash para esta noticia, aunque sea la única con tal hash
                        original['hash'] = int(random.random()*100000000)
                        self.guarda(noticia, original['hash'])   
                    '''                     
        except:
            print("Error general en busca_relacion")
        #nformación de ners para tablas ners y ners_relacion
        self.informacion_ners()

    def guarda(self, noticia, mihash):
        # Viene de busca_relacion()
        # print("Llegamos a guardar en guarda para noticia", noticia)
        t = "update not_relacion set hash = '%s', indice = %s \
             where id = %s" % (str(mihash), str('{0:.6f}'.format(self.indice)), str(noticia))
        cur3 = self.con.cursor()
        try:
            cur3.execute(t)
        except my.Error as err:
            if err.errno == 1265: #Data truncated 
                pass
            else:
                print("Error guardando hash", t, format(err))

    def guarda_resto(self, noticia, hash_antiguo, hash_nuevo):
        # Viene de busca_relacion()
        # miramos si una vez cambiado el hash, pudiera afectar a otros con mismo hash antiguo
        # que estaban relacionados inicialmente con la noticia a la que se acaba de cambiar el hash
        set_original = set(sorted(self.relaciones[noticia]))
        for notic, conjunto in self.relaciones.items():
            union = set_original & set(sorted(self.relaciones[notic]))
            if noticia != notic and hash_antiguo == self.relaciones[notic]['hash']:
                if len(union)/len(set_original) > self.minimo_comun:
                    self.guarda(notic, hash_nuevo)                                     
            
    def unifica_ner(self, noticia):
        # proviene de identifica_ner
        # función para igualar ners de personas, 
        # p.e. ner1 = 'Mariano Rajoy', ner2 = 'Mariano', ner3 = 'Rajoy'
        # En esos casos, al estar en la misma noticia, se asume que los tres ners son la misma persona
        # Se igualan todos el mayor('Mariano_Rajoy') desechando 'Mariano' y 'Rajoy' que son cambiados al mayor
        
        
        # print("Llega a unifica_ner la noticia", noticia)
        i = -1 # indice de self.unificado['ner']
        for ner, nec, tipo in zip(self.unificado['ner'], self.unificado['nec'], self.unificado['tipo']):
            # print("En unifica_ner tenemos en loop, ",  ner, nec, tipo)
            i +=1 
            if ner.find('_')<0: # solo para palabras sencillas no compuestas
                # print("buscando simples", noticia, ner, "es ner", nec, tipo)
                for ner1, nec1, tipo1 in zip(self.unificado['ner'], self.unificado['nec'], self.unificado['tipo']):
                    # print("En unifica_ner1 tenemos en loop, ",  ner1, nec1, tipo1)
                    if ner1.find('_')>0: # buscando ahora en palabras compuestas
                        # print(".....buscando compuestos", noticia, ner1, " es ner1", nec1, tipo1)
                        if ner1.find(ner)>-1 and nec1 == 'NP00SP0': 
                            # print("..........HALLADOS...EN ", noticia, tipo, "ner y ner1", ner, ner1)
                            self.unificado['ner'][i] = ner1
                            self.unificado['nec'][i] = nec1
                            self.unificado['tipo'][i] = tipo1
                            

            '''
            # Ahora buscamos siglas, abreviaturas de nombres (INE = Instituto Nacional de Estadística)
            if ner == ner.upper() and len(ner) < 6: # si está todo en mayúsculas y solo paralabras cortas en mayúsculas
                for ner1, nec1 in self.unificado.items():
                    sigla = 
            '''    
        #guardamos la nueva lista de ners y necs, una vez quitados los de una sola palabra repetidos
        #Guardar en tabla not_nombres_relaciones, junto ncon tipo
        # print(noticia, self.unificado)
        self.guarda_ners_necs(noticia)
        # print("\npasamos", tipo, "en noticia", noticia, "\n")
        # print ("ner tras unifica", (self.unificado['ner']))
        
        
    def guarda_ners_necs(self, noticia):
        # print("Llega a guarda_mners_necs la noticia", noticia)
        try:
            for ner, nec, tipo in zip(self.unificado['ner'], self.unificado['nec'], self.unificado['tipo']):
                t = "insert ignore into not_nombres_relaciones (ner, tipo, noticia, nec) \
                    values('%s', '%s', '%s', '%s')" % (ner, tipo, str(noticia), nec)
                try:
                    self.cur.execute(t)
                except my.Error as err:
                    print("\n Error insertando/actualizando en tabla not_nombres_relaciones en sentencia ", t)
                    print(format(err))
            # print(10, " y final")
        except:
            print("Error formando sentencia de insert into not_nombres_relaciones para ", noticia)
    
    def informacion_ners(self):
        informa = Necs()
        informa.actualiza_necs()
        
        
            
                
                
                
            
            
            
