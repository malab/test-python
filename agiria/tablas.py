'''
Created on 18/10/2014

@author: aurelio
'''
import mysql.connector as my

con_data = {'user':'root','password':'agm','host':'127.0.0.1', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)

def create(bd, tabla, todos):
    cur = con.cursor()
    for cada in todos:
        t = "insert ignore into tablas.tablas (bd, tabla, field, type, collation, nulo, clave, comments) \
        values (%s, %s, %s, %s, %s, %s, %s, %s);"
        field = cada[0]
        tipo = cada[1]
        collation = cada[2]
        if not collation:
            collation = ''
        nulo = cada[3]
        if not nulo:
            nulo = ''
        clave = cada[4]
        comments = ''
        values = (bd, tabla, field, tipo, collation, nulo, clave, comments)
        try:
            cur.execute(t, values)
        except my.Error as err:
            print("ERROR: ", err, t, values)

def changeCollation(funcion, bd, tabla, todos):
    desde = funcion['from']
    to = funcion['to']
    cur = con.cursor()
    t = "select database();"
    cur.execute(t)
    dbOrig = cur.fetchone()[0]
    t = "use %s" % bd
    cur.execute(t)
    for cada in todos:
        if cada[2] == desde:
            t = 'ALTER TABLE '+ tabla + ' MODIFY '+ cada[0] + ' ' + cada[1] + ' CHARACTER SET utf8 COLLATE ' + to + ';'
            try:
                cur.execute(t)
            except my.Error as err:
                print(err, t)
    #return to the original database
    t = "use %s" % dbOrig
    cur.execute(t)

def buscaColumnas(funcion, bd, tabla):
    t = "show full columns from %s in %s;" % (tabla, bd)
    cur = con.cursor()
    cur.execute(t)
    # print(tabla, "*"*20)
    todos =cur.fetchall()
    if funcion == 'create':
        create(bd, tabla, todos)
    elif isinstance(funcion, dict):
        changeCollation(funcion, bd, tabla, todos)


def buscaTablas(funcion, bd):
    cur = con.cursor()
    t = "show tables from %s;" % bd
    cur.execute(t)
    tablas = cur.fetchall()
    for tabla in tablas:
        buscaColumnas(funcion, bd, tabla[0])
        
def buscaDBs(funcion):
    exceptions = ['dbbolsa', 'information_schema', 'mysql', 'performance_schema']
    cur = con.cursor()
    t = "show databases;"
    cur.execute(t)
    bds = cur.fetchall()
    for bd in bds:
        if bd[0] not in exceptions:
            buscaTablas(funcion, bd[0])

if __name__ == '__main__':
    #insert function name e.g. 'create', 'collation'
    # create goes as a string for that name 'create'
    # collation goes as a dict with {'from':collation1, 'to':collation2}
    funcion = {'from':'utf8_czech_ci', 'to':'utf8_spanish_ci'} #for collation
    # funcion = 'create' #to create new tablas with schema information
    buscaDBs(funcion)
    