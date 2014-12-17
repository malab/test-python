'''
Created on 31/07/2013

@author: aurelio
'''

import json
import urllib.request
import urllib.parse
import pprint
import mysql.connector as my
from config import con_data


class Nec(object):
    '''
    recopila informacion de un NEC usando freebase y como output el resumen sobre el NEC de wikipedia
    '''
    

    def __init__(self):
        '''
        Constructor
        '''
        self.nec = ''
        self.ner = ''
        self.nombre = ''
        self.topic_id = ''
        self.propiedad = ''
        self.informacion = ''
        self.relaciones = []
        self.nuevo = True
        
        
        self.con = my.connect(**con_data)
        
       
    def mira_si_nuevo(self):
        cur = self.con.cursor()
        t = "select ner, topic_id, propiedad, significado1 from ners where ner = '%s'" % self.ner
        cur.execute(t)
        if cur.rowcount > 0:
            self.nuevo = False
        if self.nuevo == False:
            fila = cur.fetchone()
            self.topic_id = fila[1]
            self.propiedad = fila[2]
            self.significado = fila[3]
            #Siguiente anulado de momento
            #self.trae_relaciones()
        else:
            self.trae_nec()
            
            
    def trae_relaciones(self):
        cur = self.con.cursor()
        t= "select relacion from ners_relacion where ner = '%s'" % self.ner
        cur.execute(t)
        for fila in cur:
            self.relaciones.append(fila[0])
        # print(self.relaciones)    
        
        
    def trae_nec(self):
        api_key = 'AIzaSyCEKLXRIysevTb5RtJbv8rHFF67B5VULpM'
        query = self.ner
        service_url = 'https://www.googleapis.com/freebase/v1/search'
        params = {
                'query': query,
                'key': api_key,
                # 'filter':'(any type:/people/person type:/location/citytown)',
                'lang':'es',
                'output':'(type)',
                'output':'(description:wikipedia)'
        }
        # pprint.pprint(params)
        url = service_url + '?' + urllib.parse.urlencode(params)
        # print(url)
        resp = urllib.request.urlopen(url).read()
        resp = resp.decode()
        response = json.loads(resp)
        hay_algo = False
        if len(response['result']):
            primero = response['result'][0]
            hay_algo = True
        else:
            pprint.pprint(params)
        if hay_algo:
            # pprint.pprint(primero)
            self.nombre = primero['name']
            if 'id' in primero:
                self.topic_id = primero['id']
            else:
                self.topic_id = ''
            if 'notable' in primero:
                self.propiedad = primero['notable']['name']
            else:
                self.propiedad = ''
            if 'output' in primero:
                if 'description:wikipedia' in primero['output']:
                    if '/common/topic/description' in primero['output']['description:wikipedia']:
                        if len(primero['output']['description:wikipedia']) > 0:
                            self.significado = primero['output']['description:wikipedia']['/common/topic/description'][0]
                        else:
                            self.significado = ''
                    else:
                        self.significado = ''
            # print('\n ASOCIACIONES\n')
            num = 1
            for result in response['result']:
                self.relaciones.append(result['name'])
                if num >= 10:
                    break
                num+=1
            self.relaciones = set(self.relaciones)
            if self.significado:
                self.guarda_nec()
            if self.relaciones:
                self.guarda_relaciones()
        
    def guarda_nec(self):
        cur = self.con.cursor()
        t = "insert ignore into ners (ner, topic_id, significado1, propiedad) values('%s', '%s', '%s', '%s')" % (self.ner, self.topic_id, self.significado, self.propiedad)
        try:
            cur.execute(t)
        except:
            pass
            # print('Error en necs', t)
        
        
    def guarda_relaciones(self):
        cur = self.con.cursor()
        for relacion in self.relaciones:
            if relacion:
                t = "insert ignore into ners_relacion (ner, relacion) values ('%s', '%s')" % (self.ner, relacion)
                try:
                    cur.execute(t)
                except:
                    pass
                    #print('Error en necs_relacion', t)
        
        
        
        
            
    
    