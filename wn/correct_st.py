'''
Created on 21/10/2014

@author: aurelio
'''
import mysql.connector as my
from pprint import pprint


con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)


class MySQLCursorDict(my.cursor.MySQLCursor):
    def _row_to_python(self, rowdata, desc=None):
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            return dict(zip(self.column_names, row))
        return None
    
def readPos(file):
    with open(file, 'rt') as f:
        lines = f.readlines()
        for line in lines:
            line = line[:-1]
            if line:
                datos = line.split(':')
                allPos[datos[0].strip()] = datos[1].strip()
                


def selectRecords(inicio):
    #only up to record 162000
    cuantos = 162000 - inicio
    # cuantos = 100 - inicio
    cur = con.cursor(cursor_class=MySQLCursorDict)
    t = "select * from senti_trans limit %s, %s;" % (inicio, cuantos)
    cur.execute(t)
    return cur.fetchall()

def update(cada, p):
    cur = con.cursor()
    t = "update senti_trans set sp_word = %s where \
    en_word = %s and en_pos = %s and sense = %s and sp_word = %s and sp_pos = %s;"
    values = (p.strip(), cada['en_word'], cada['en_pos'], cada['sense'], cada['sp_word'], cada['sp_pos'])
    try:
        cur.execute(t, values)
    except my.Error as err:
        pass
        # print("ERROR: ", err, t, values)

def deleteRecord(cada):
    cur = con.cursor()
    t = "delete from senti_trans where en_word = %s and en_pos = %s and sense = %s and sp_word = %s and sp_pos = %s;"
    values = (cada['en_word'], cada['en_pos'], cada['sense'], cada['sp_word'], cada['sp_pos'])
    try:
        cur.execute(t, values)
    except my.Error as err:
        print("ERROR: ", err, t, values)

        
def saveNew(cada, p):
    if cada:
        # print("Guardado", n, wen, pos, pal['word'], pal['tipo'], allPos[pal['tipo']] )
        t = "insert ignore into senti_trans (en_word, info1, info2, en_pos, sense, sp_word, sp_pos, \
        offset, example, ejemplo, gloss) values \
        (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"         
        values = (cada['en_word'], cada['info1'], cada['info2'], cada['en_pos'], cada['sense'], \
                    p, cada['sp_pos'], cada['offset'], \
                  cada['example'], cada['ejemplo'], cada['gloss'])
        cur = con.cursor()
        try:
            cur.execute(t, values)
        except my.Error as err:
            print("ERROR - ", err, t, values)

def main():
    all = selectRecords(inicio)
    for cada in all:
        try:
            if cada['sp_pos'] and allPos[cada['sp_pos']] != cada['en_pos']:
                # print("BORRAR SIGUIENTE - 1:", "-+" *30)
                deleteRecord(cada)
                # pprint(cada)
                """
                elif cada['sp_pos'] == '?' and cada['en_pos'] != 'v' and cada['sp_word'][-2:] in ['ar', 'er', 'ir']:
                    # print("BORRAR SIGUIENTE - 2:", "-+" *30)
                    deleteRecord(cada)
                    # pprint(cada)
                """
            else: 
                if "," in cada['sp_word']:
                    pal2 = cada['sp_word'].split(',')
                    # pprint(cada)
                    for a, p in enumerate(pal2):
                        if a == 0:
                            update (cada, p.strip())
                            # print("Actualizando el siguiente para ", p, "+-"*15)
                        else:
                            saveNew(cada, p.strip())
                            # print("guardando nuevo siguiente para ", p, "+-"*15)                
        except:
            pass
            # print("No encontrados: ", "*"*20, cada['en_word'],cada['info1'], cada['en_pos'], cada['sp_word'], cada['sp_pos'])


allPos = {}
inicio = 1

if __name__ == '__main__':
    readPos('data/sp_pos.txt')
    main()

