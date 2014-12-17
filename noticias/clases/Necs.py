'''
Created on 31/07/2013

@author: aurelio
'''

import mysql.connector as my
import sys
sys.path.append('var/www/noticias/clases')
from Nec import *
from config import con_data

class Necs(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.con = my.connect(**con_data)
        
        
    def actualiza_necs(self):
        cur = self.con.cursor()
        t = "select ner, nec from not_importancia_ners"
        cur.execute(t)
        for fila in cur:
            nec = Nec()
            nec.ner = fila[0].strip()
            nec.nec = fila[1].strip()
            nec.mira_si_nuevo()

            