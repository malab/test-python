'''
Created on 26/11/2013

@author: aurelio
'''
"""
Un borrador para separar palabras unidas erróneamente
por ejemplo: lacasadelmar = la casa del mar
"""
import mysql.connector as my
con_data = {'user':'root','password':'agm','host':'localhost', \
            'database':'db_noticias','raise_on_warnings': True, 'autocommit':True, 'buffered':True}

class multipal:

    def __init__(self):
        self.con = my.connect(**con_data)
        self.cur = self.con.cursor()
        t = "Select pal from dicc_distinct order by pal"
        self.pals = []
        self.cur.execute(t)
        for cada in self.cur.fetchall():
            self.pals.append(cada[0])

        self.pals = tuple(self.pals)

    def analiza(self,fr):
        nf = len(fr)
        npal = []
        com = 0
        fin = nf
        s = True
        print(fr)
        while s:
            for a in range(nf):
                if fr[com:fin] in self.pals:
                    npal.append(fr[com:fin])
                    com = nf - a
                    fin = nf
                    break
                fin -= 1
            if com >= fin - 1:
                s = False
        print((" ".join(npal)))
        # faltaría cotejar con ngrams para ver si resultado tiene sentido. Si no, buscar otra combinación.
        
n = multipal()
frase = "lossalchichonessonbuenos"
n.analiza(frase)
